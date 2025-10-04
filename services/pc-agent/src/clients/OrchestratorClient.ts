/**
 * Orchestrator Client for JarvisX PC Agent
 * Handles communication with the central orchestrator service
 */

import { EventEmitter } from 'events';
import axios, { AxiosInstance } from 'axios';
import WebSocket from 'ws';

export interface OrchestratorConfig {
  baseUrl: string;
  wsUrl: string;
  apiKey?: string;
  timeout?: number;
}

export interface SessionCapabilities {
  screenShare: boolean;
  audioShare: boolean;
  systemControl: boolean;
  voiceControl: boolean;
  webAutomation: boolean;
}

export interface OrchestratorMessage {
  type: string;
  data?: any;
  sessionId?: string;
  timestamp: string;
}

export class OrchestratorClient extends EventEmitter {
  private config: OrchestratorConfig;
  private httpClient: AxiosInstance;
  private wsClient: WebSocket | null = null;
  private isConnected: boolean = false;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectDelay: number = 3000;
  private heartbeatInterval: NodeJS.Timeout | null = null;

  constructor(config: OrchestratorConfig) {
    super();
    this.config = {
      timeout: 30000,
      ...config
    };

    // Initialize HTTP client
    this.httpClient = axios.create({
      baseURL: this.config.baseUrl,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
        ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` })
      }
    });

    this.setupHttpInterceptors();
  }

  private setupHttpInterceptors(): void {
    // Request interceptor
    this.httpClient.interceptors.request.use(
      (config) => {
        console.log(`📡 HTTP Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ HTTP Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.httpClient.interceptors.response.use(
      (response) => {
        console.log(`📡 HTTP Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('❌ HTTP Response Error:', error.response?.status, error.message);
        return Promise.reject(error);
      }
    );
  }

  public async connect(): Promise<void> {
    try {
      console.log('🔌 Connecting to JarvisX Orchestrator...');
      
      // Test HTTP connection first
      await this.testConnection();
      
      // Connect WebSocket
      await this.connectWebSocket();
      
      this.isConnected = true;
      this.reconnectAttempts = 0;
      
      console.log('✅ Connected to JarvisX Orchestrator');
      this.emit('connected');
      
    } catch (error) {
      console.error('❌ Failed to connect to orchestrator:', error);
      this.isConnected = false;
      this.emit('connectionFailed', error);
      
      // Attempt to reconnect
      await this.scheduleReconnect();
    }
  }

  private async testConnection(): Promise<void> {
    try {
      const response = await this.httpClient.get('/health');
      if (response.status !== 200) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      console.log('✅ HTTP connection test passed');
    } catch (error) {
      throw new Error(`HTTP connection test failed: ${error.message}`);
    }
  }

  private async connectWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.wsClient = new WebSocket(this.config.wsUrl);
        
        this.wsClient.on('open', () => {
          console.log('✅ WebSocket connected');
          this.startHeartbeat();
          resolve();
        });
        
        this.wsClient.on('message', (data) => {
          try {
            const message: OrchestratorMessage = JSON.parse(data.toString());
            this.handleWebSocketMessage(message);
          } catch (error) {
            console.error('❌ Failed to parse WebSocket message:', error);
          }
        });
        
        this.wsClient.on('close', (code, reason) => {
          console.log(`🔌 WebSocket closed: ${code} ${reason}`);
          this.isConnected = false;
          this.stopHeartbeat();
          this.emit('disconnected', { code, reason });
          
          // Attempt to reconnect
          this.scheduleReconnect();
        });
        
        this.wsClient.on('error', (error) => {
          console.error('❌ WebSocket error:', error);
          this.isConnected = false;
          this.stopHeartbeat();
          reject(error);
        });
        
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleWebSocketMessage(message: OrchestratorMessage): void {
    console.log(`📨 Received message: ${message.type}`);
    
    switch (message.type) {
      case 'ping':
        this.sendWebSocketMessage({ type: 'pong', timestamp: new Date().toISOString() });
        break;
        
      case 'session_start':
        this.emit('sessionStart', message.data);
        break;
        
      case 'session_end':
        this.emit('sessionEnd', message.data);
        break;
        
      case 'system_command':
        this.emit('systemCommand', message.data);
        break;
        
      case 'screen_capture_request':
        this.emit('screenCaptureRequest', message.data);
        break;
        
      case 'voice_command':
        this.emit('voiceCommand', message.data);
        break;
        
      case 'approval_request':
        this.emit('approvalRequest', message.data);
        break;
        
      case 'emergency_stop':
        this.emit('emergencyStop', message.data);
        break;
        
      default:
        console.log(`📨 Unknown message type: ${message.type}`);
        this.emit('unknownMessage', message);
    }
  }

  private sendWebSocketMessage(message: any): void {
    if (this.wsClient && this.wsClient.readyState === WebSocket.OPEN) {
      try {
        const messageWithTimestamp = {
          ...message,
          timestamp: new Date().toISOString()
        };
        
        this.wsClient.send(JSON.stringify(messageWithTimestamp));
        console.log(`📤 Sent message: ${message.type}`);
      } catch (error) {
        console.error('❌ Failed to send WebSocket message:', error);
      }
    } else {
      console.warn('⚠️ WebSocket not connected, cannot send message');
    }
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.sendWebSocketMessage({ type: 'heartbeat' });
      }
    }, 30000); // Send heartbeat every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private async scheduleReconnect(): Promise<void> {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
      return;
    }
    
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
    
    console.log(`🔄 Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    setTimeout(async () => {
      try {
        await this.connect();
      } catch (error) {
        console.error('❌ Reconnection attempt failed:', error);
      }
    }, delay);
  }

  public async notifySessionStart(sessionId: string, capabilities: SessionCapabilities): Promise<void> {
    try {
      await this.httpClient.post('/sessions', {
        sessionId,
        type: 'pc_agent',
        capabilities,
        status: 'active'
      });
      
      this.sendWebSocketMessage({
        type: 'session_started',
        data: { sessionId, capabilities }
      });
      
      console.log(`📡 Notified orchestrator of session start: ${sessionId}`);
    } catch (error) {
      console.error('❌ Failed to notify session start:', error);
      throw error;
    }
  }

  public async notifySessionEnd(sessionId: string): Promise<void> {
    try {
      await this.httpClient.delete(`/sessions/${sessionId}`);
      
      this.sendWebSocketMessage({
        type: 'session_ended',
        data: { sessionId }
      });
      
      console.log(`📡 Notified orchestrator of session end: ${sessionId}`);
    } catch (error) {
      console.error('❌ Failed to notify session end:', error);
      throw error;
    }
  }

  public async sendActionEvent(actionEvent: any): Promise<void> {
    try {
      await this.httpClient.post('/events', {
        type: 'action_event',
        data: actionEvent
      });
      
      this.sendWebSocketMessage({
        type: 'action_event',
        data: actionEvent
      });
      
    } catch (error) {
      console.error('❌ Failed to send action event:', error);
      throw error;
    }
  }

  public async sendSystemStatus(status: any): Promise<void> {
    try {
      this.sendWebSocketMessage({
        type: 'system_status',
        data: status
      });
    } catch (error) {
      console.error('❌ Failed to send system status:', error);
      throw error;
    }
  }

  public async requestApproval(approvalData: any): Promise<any> {
    try {
      const response = await this.httpClient.post('/approvals', approvalData);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to request approval:', error);
      throw error;
    }
  }

  public async sendError(error: any): Promise<void> {
    try {
      await this.httpClient.post('/errors', {
        type: 'pc_agent_error',
        data: error,
        timestamp: new Date().toISOString()
      });
      
      this.sendWebSocketMessage({
        type: 'error',
        data: error
      });
      
    } catch (error) {
      console.error('❌ Failed to send error:', error);
    }
  }

  public async getConfiguration(): Promise<any> {
    try {
      const response = await this.httpClient.get('/config');
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get configuration:', error);
      throw error;
    }
  }

  public async updateConfiguration(config: any): Promise<void> {
    try {
      await this.httpClient.put('/config', config);
      console.log('✅ Configuration updated');
    } catch (error) {
      console.error('❌ Failed to update configuration:', error);
      throw error;
    }
  }

  public async getActiveSessions(): Promise<any[]> {
    try {
      const response = await this.httpClient.get('/sessions');
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get active sessions:', error);
      throw error;
    }
  }

  public async disconnect(): Promise<void> {
    try {
      this.stopHeartbeat();
      
      if (this.wsClient) {
        this.wsClient.close();
        this.wsClient = null;
      }
      
      this.isConnected = false;
      console.log('🔌 Disconnected from orchestrator');
      
    } catch (error) {
      console.error('❌ Error during disconnect:', error);
    }
  }

  public isConnected(): boolean {
    return this.isConnected && this.wsClient?.readyState === WebSocket.OPEN;
  }

  public getConnectionStatus(): any {
    return {
      connected: this.isConnected(),
      reconnectAttempts: this.reconnectAttempts,
      websocketState: this.wsClient?.readyState,
      lastError: null // Could track last error
    };
  }
}
