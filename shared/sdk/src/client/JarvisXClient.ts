/**
 * JarvisX Client - Main SDK entry point
 * Used by both Desktop (Tauri) and Mobile (React Native) apps
 */

import { io, Socket } from 'socket.io-client';
import axios, { AxiosInstance } from 'axios';
import EventEmitter from 'eventemitter3';
import { AuthManager } from '../auth/AuthManager';
import { SyncManager } from '../sync/SyncManager';
import type {
  JarvisXConfig,
  Task,
  AvatarState,
  VoiceCommand,
  SyncEvent,
  User
} from '../types';

export interface JarvisXClientEvents {
  'connected': () => void;
  'disconnected': () => void;
  'task_update': (task: Task) => void;
  'avatar_update': (state: AvatarState) => void;
  'voice_command': (command: VoiceCommand) => void;
  'sync_event': (event: SyncEvent) => void;
  'permission_request': (data: any) => void;
  'error': (error: Error) => void;
}

export class JarvisXClient extends EventEmitter<JarvisXClientEvents> {
  private config: JarvisXConfig;
  private socket: Socket | null = null;
  private http: AxiosInstance;
  public auth: AuthManager;
  public sync: SyncManager;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;

  constructor(config: JarvisXConfig) {
    super();
    this.config = config;

    // Setup HTTP client
    this.http = axios.create({
      baseURL: config.apiUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'X-Device-ID': config.deviceId,
        'X-Device-Type': config.deviceType,
        'X-Platform': config.platform
      }
    });

    // Initialize managers
    this.auth = new AuthManager(this.http, config);
    this.sync = new SyncManager(this.http, config);

    // Setup interceptors
    this.setupHttpInterceptors();
  }

  /**
   * Connect to JarvisX backend
   */
  async connect(): Promise<void> {
    try {
      // Ensure authenticated
      if (!this.auth.isAuthenticated()) {
        throw new Error('Not authenticated. Call client.auth.login() first.');
      }

      // Connect to WebSocket
      await this.connectWebSocket();

      console.log('✅ JarvisX Client connected');
    } catch (error) {
      console.error('❌ Failed to connect:', error);
      this.emit('error', error as Error);
      throw error;
    }
  }

  /**
   * Disconnect from backend
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    console.log('🔌 JarvisX Client disconnected');
  }

  /**
   * Send task to orchestrator
   */
  async sendTask(type: string, input: any): Promise<Task> {
    try {
      const response = await this.http.post('/tasks', {
        type,
        input,
        deviceId: this.config.deviceId
      });

      return response.data.task;
    } catch (error) {
      console.error('❌ Failed to send task:', error);
      throw error;
    }
  }

  /**
   * Get task by ID
   */
  async getTask(taskId: string): Promise<Task> {
    const response = await this.http.get(`/tasks/${taskId}`);
    return response.data.task;
  }

  /**
   * Get all tasks
   */
  async getTasks(filters?: any): Promise<Task[]> {
    const response = await this.http.get('/tasks', { params: filters });
    return response.data.tasks;
  }

  /**
   * Update avatar state
   */
  async updateAvatar(state: Partial<AvatarState>): Promise<void> {
    await this.http.post('/avatar/state', state);
    
    // Also emit via WebSocket for real-time sync
    if (this.socket) {
      this.socket.emit('avatar_update', state);
    }
  }

  /**
   * Send voice command
   */
  async sendVoiceCommand(text: string, language: 'si' | 'en'): Promise<Task> {
    return this.sendTask('voice_command', { text, language });
  }

  /**
   * Request remote execution on another device
   */
  async requestRemoteExecution(targetDeviceId: string, task: any): Promise<void> {
    if (this.socket) {
      this.socket.emit('remote_execution_request', {
        targetDeviceId,
        task,
        sourceDeviceId: this.config.deviceId
      });
    }
  }

  /**
   * Setup HTTP interceptors for auth
   */
  private setupHttpInterceptors(): void {
    // Request interceptor - add auth token
    this.http.interceptors.request.use((config) => {
      const token = this.auth.getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor - handle token refresh
    this.http.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            await this.auth.refreshToken();
            const token = this.auth.getAccessToken();
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return this.http(originalRequest);
          } catch (refreshError) {
            this.emit('error', new Error('Session expired'));
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  /**
   * Connect to WebSocket
   */
  private async connectWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket = io(this.config.wsUrl, {
        auth: {
          token: this.auth.getAccessToken(),
          deviceId: this.config.deviceId,
          deviceType: this.config.deviceType
        },
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000
      });

      this.socket.on('connect', () => {
        console.log('🔌 WebSocket connected');
        this.reconnectAttempts = 0;
        this.emit('connected');
        resolve();
      });

      this.socket.on('disconnect', () => {
        console.log('🔌 WebSocket disconnected');
        this.emit('disconnected');
      });

      this.socket.on('connect_error', (error) => {
        this.reconnectAttempts++;
        console.error('❌ WebSocket connection error:', error);
        
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          reject(new Error('Max reconnection attempts reached'));
        }
      });

      // Event listeners
      this.socket.on('task_update', (task: Task) => {
        this.emit('task_update', task);
      });

      this.socket.on('avatar_update', (state: AvatarState) => {
        this.emit('avatar_update', state);
      });

      this.socket.on('voice_command', (command: VoiceCommand) => {
        this.emit('voice_command', command);
      });

      this.socket.on('sync_event', (event: SyncEvent) => {
        this.emit('sync_event', event);
      });

      this.socket.on('permission_request', (data: any) => {
        this.emit('permission_request', data);
      });

      this.socket.on('remote_execution_request', (data: any) => {
        // Handle remote execution requests from other devices
        console.log('📱 Remote execution request from:', data.sourceDeviceId);
        this.emit('permission_request', {
          type: 'remote_execution',
          ...data
        });
      });
    });
  }

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    const response = await this.http.get('/auth/me');
    return response.data.user;
  }

  /**
   * Get registered devices
   */
  async getDevices(): Promise<RegisteredDevice[]> {
    const response = await this.http.get('/devices');
    return response.data.devices;
  }

  /**
   * Unregister a device
   */
  async unregisterDevice(deviceId: string): Promise<void> {
    await this.http.delete(`/devices/${deviceId}`);
  }
}

export default JarvisXClient;

