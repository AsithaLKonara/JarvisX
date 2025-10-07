/**
 * Remote Control Service for JarvisX Mobile App
 * Handles remote control of desktop JarvisX from mobile device
 */

import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface RemoteCommand {
  id: string;
  type: 'voice' | 'click' | 'keyboard' | 'system' | 'browser' | 'approval';
  action: string;
  parameters: any;
  timestamp: number;
  status: 'pending' | 'executing' | 'completed' | 'failed';
  result?: any;
  error?: string;
}

export interface DesktopStatus {
  isConnected: boolean;
  isListening: boolean;
  isProcessing: boolean;
  isSpeaking: boolean;
  currentEmotion: string;
  confidence: number;
  lastCommand: string;
  systemStats: {
    cpu: number;
    memory: number;
    network: number;
    uptime: string;
  };
  activeServices: string[];
}

export interface ApprovalRequest {
  id: string;
  action: string;
  description: string;
  riskScore: number;
  riskCategory: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  timestamp: number;
  expiresAt: number;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
}

export class RemoteControlService {
  private static instance: RemoteControlService;
  private ws: WebSocket | null = null;
  private isConnected: boolean = false;
  private desktopStatus: DesktopStatus | null = null;
  private pendingApprovals: Map<string, ApprovalRequest> = new Map();
  private commandHistory: RemoteCommand[] = [];
  private eventHandlers: Map<string, (data: any) => void> = new Map();

  private constructor() {
    this.initialize();
  }

  public static getInstance(): RemoteControlService {
    if (!RemoteControlService.instance) {
      RemoteControlService.instance = new RemoteControlService();
    }
    return RemoteControlService.instance;
  }

  private async initialize(): Promise<void> {
    try {
      console.log('📱 Initializing Remote Control Service...');
      
      // Load saved connection settings
      await this.loadConnectionSettings();
      
      // Try to connect to desktop
      await this.connectToDesktop();
      
      console.log('✅ Remote Control Service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Remote Control Service:', error);
    }
  }

  private async loadConnectionSettings(): Promise<void> {
    try {
      const settings = await AsyncStorage.getItem('jarvisx_connection_settings');
      if (settings) {
        const parsed = JSON.parse(settings);
        // Use saved settings for connection
        console.log('📱 Loaded connection settings:', parsed);
      }
    } catch (error) {
      console.error('❌ Failed to load connection settings:', error);
    }
  }

  private async saveConnectionSettings(settings: any): Promise<void> {
    try {
      await AsyncStorage.setItem('jarvisx_connection_settings', JSON.stringify(settings));
    } catch (error) {
      console.error('❌ Failed to save connection settings:', error);
    }
  }

  public async connectToDesktop(serverUrl: string = 'ws://localhost:3000'): Promise<boolean> {
    try {
      console.log('🔌 Connecting to desktop JarvisX...');
      
      this.ws = new WebSocket(serverUrl);
      
      this.ws.onopen = () => {
        console.log('✅ Connected to desktop JarvisX');
        this.isConnected = true;
        this.emit('connected', { serverUrl });
        
        // Send mobile device info
        this.sendMobileDeviceInfo();
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleDesktopMessage(data);
        } catch (error) {
          console.error('❌ Failed to parse desktop message:', error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('🔌 Disconnected from desktop JarvisX');
        this.isConnected = false;
        this.emit('disconnected', {});
        
        // Attempt to reconnect after 5 seconds
        setTimeout(() => {
          if (!this.isConnected) {
            this.connectToDesktop(serverUrl);
          }
        }, 5000);
      };
      
      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        this.emit('error', { error: error.message });
      };
      
      return true;
    } catch (error) {
      console.error('❌ Failed to connect to desktop:', error);
      return false;
    }
  }

  private sendMobileDeviceInfo(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'mobile_device_info',
        data: {
          platform: Platform.OS,
          version: Platform.Version,
          deviceType: 'mobile',
          timestamp: Date.now(),
        }
      }));
    }
  }

  private handleDesktopMessage(data: any): void {
    console.log('📱 Received desktop message:', data.type);
    
    switch (data.type) {
      case 'desktop_status':
        this.desktopStatus = data.data;
        this.emit('status_update', this.desktopStatus);
        break;
        
      case 'approval_request':
        this.handleApprovalRequest(data.data);
        break;
        
      case 'command_result':
        this.handleCommandResult(data.data);
        break;
        
      case 'voice_status':
        this.emit('voice_status', data.data);
        break;
        
      case 'system_alert':
        this.emit('system_alert', data.data);
        break;
        
      default:
        console.log('📱 Unknown message type:', data.type);
    }
  }

  private handleApprovalRequest(data: any): void {
    const approval: ApprovalRequest = {
      id: data.id,
      action: data.action,
      description: data.description,
      riskScore: data.riskScore,
      riskCategory: data.riskCategory,
      timestamp: data.timestamp,
      expiresAt: data.expiresAt,
      status: 'pending'
    };
    
    this.pendingApprovals.set(approval.id, approval);
    this.emit('approval_request', approval);
  }

  private handleCommandResult(data: any): void {
    const command = this.commandHistory.find(cmd => cmd.id === data.commandId);
    if (command) {
      command.status = data.success ? 'completed' : 'failed';
      command.result = data.result;
      command.error = data.error;
      
      this.emit('command_result', command);
    }
  }

  public async sendVoiceCommand(command: string): Promise<string> {
    const commandId = this.generateCommandId();
    
    const remoteCommand: RemoteCommand = {
      id: commandId,
      type: 'voice',
      action: 'execute_voice_command',
      parameters: { command },
      timestamp: Date.now(),
      status: 'pending'
    };
    
    this.commandHistory.unshift(remoteCommand);
    this.commandHistory = this.commandHistory.slice(0, 50); // Keep last 50 commands
    
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'voice_command',
        data: {
          commandId,
          command,
          timestamp: Date.now()
        }
      }));
      
      return commandId;
    } else {
      throw new Error('Not connected to desktop');
    }
  }

  public async sendClickCommand(x: number, y: number): Promise<string> {
    const commandId = this.generateCommandId();
    
    const remoteCommand: RemoteCommand = {
      id: commandId,
      type: 'click',
      action: 'mouse_click',
      parameters: { x, y },
      timestamp: Date.now(),
      status: 'pending'
    };
    
    this.commandHistory.unshift(remoteCommand);
    this.commandHistory = this.commandHistory.slice(0, 50);
    
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'mouse_click',
        data: {
          commandId,
          x,
          y,
          timestamp: Date.now()
        }
      }));
      
      return commandId;
    } else {
      throw new Error('Not connected to desktop');
    }
  }

  public async sendKeyboardCommand(key: string): Promise<string> {
    const commandId = this.generateCommandId();
    
    const remoteCommand: RemoteCommand = {
      id: commandId,
      type: 'keyboard',
      action: 'keyboard_input',
      parameters: { key },
      timestamp: Date.now(),
      status: 'pending'
    };
    
    this.commandHistory.unshift(remoteCommand);
    this.commandHistory = this.commandHistory.slice(0, 50);
    
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'keyboard_input',
        data: {
          commandId,
          key,
          timestamp: Date.now()
        }
      }));
      
      return commandId;
    } else {
      throw new Error('Not connected to desktop');
    }
  }

  public async sendSystemCommand(action: string, parameters: any = {}): Promise<string> {
    const commandId = this.generateCommandId();
    
    const remoteCommand: RemoteCommand = {
      id: commandId,
      type: 'system',
      action,
      parameters,
      timestamp: Date.now(),
      status: 'pending'
    };
    
    this.commandHistory.unshift(remoteCommand);
    this.commandHistory = this.commandHistory.slice(0, 50);
    
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'system_command',
        data: {
          commandId,
          action,
          parameters,
          timestamp: Date.now()
        }
      }));
      
      return commandId;
    } else {
      throw new Error('Not connected to desktop');
    }
  }

  public async sendBrowserCommand(action: string, parameters: any = {}): Promise<string> {
    const commandId = this.generateCommandId();
    
    const remoteCommand: RemoteCommand = {
      id: commandId,
      type: 'browser',
      action,
      parameters,
      timestamp: Date.now(),
      status: 'pending'
    };
    
    this.commandHistory.unshift(remoteCommand);
    this.commandHistory = this.commandHistory.slice(0, 50);
    
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'browser_command',
        data: {
          commandId,
          action,
          parameters,
          timestamp: Date.now()
        }
      }));
      
      return commandId;
    } else {
      throw new Error('Not connected to desktop');
    }
  }

  public async approveRequest(requestId: string, approved: boolean, reason?: string): Promise<boolean> {
    try {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          type: 'approval_decision',
          data: {
            requestId,
            decision: approved ? 'approve' : 'reject',
            reason: reason || `Mobile ${approved ? 'approval' : 'rejection'}`,
            timestamp: Date.now()
          }
        }));
        
        // Update local approval status
        const approval = this.pendingApprovals.get(requestId);
        if (approval) {
          approval.status = approved ? 'approved' : 'rejected';
          this.pendingApprovals.set(requestId, approval);
        }
        
        return true;
      } else {
        throw new Error('Not connected to desktop');
      }
    } catch (error) {
      console.error('❌ Failed to send approval decision:', error);
      return false;
    }
  }

  public async getDesktopStatus(): Promise<DesktopStatus | null> {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'get_status',
        data: { timestamp: Date.now() }
      }));
    }
    
    return this.desktopStatus;
  }

  public async getPendingApprovals(): Promise<ApprovalRequest[]> {
    return Array.from(this.pendingApprovals.values())
      .filter(approval => approval.status === 'pending');
  }

  public getCommandHistory(): RemoteCommand[] {
    return this.commandHistory;
  }

  public getConnectionStatus(): boolean {
    return this.isConnected;
  }

  public on(event: string, handler: (data: any) => void): void {
    this.eventHandlers.set(event, handler);
  }

  public off(event: string): void {
    this.eventHandlers.delete(event);
  }

  private emit(event: string, data: any): void {
    const handler = this.eventHandlers.get(event);
    if (handler) {
      handler(data);
    }
  }

  private generateCommandId(): string {
    return `cmd_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
  }
}

export default RemoteControlService;
