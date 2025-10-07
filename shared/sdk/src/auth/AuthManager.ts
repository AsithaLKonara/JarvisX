/**
 * Auth Manager - Cross-device authentication
 * Handles JWT tokens, device registration, and session management
 */

import { AxiosInstance } from 'axios';
import type { AuthCredentials, AuthToken, User, JarvisXConfig } from '../types';

export class AuthManager {
  private http: AxiosInstance;
  private config: JarvisXConfig;
  private authToken: AuthToken | null = null;
  private storageKey: string = 'jarvisx_auth_token';

  constructor(http: AxiosInstance, config: JarvisXConfig) {
    this.http = http;
    this.config = config;
    this.loadTokenFromStorage();
  }

  /**
   * Login with email/password
   */
  async login(email: string, password: string): Promise<User> {
    try {
      const credentials: AuthCredentials = {
        email,
        password,
        deviceId: this.config.deviceId,
        deviceType: this.config.deviceType,
        platform: this.config.platform
      };

      const response = await this.http.post('/auth/login', credentials);
      
      this.authToken = response.data.token;
      this.saveTokenToStorage();

      console.log('✅ Logged in successfully');
      return response.data.user;
    } catch (error) {
      console.error('❌ Login failed:', error);
      throw error;
    }
  }

  /**
   * Register new user
   */
  async register(email: string, password: string, name: string): Promise<User> {
    try {
      const response = await this.http.post('/auth/register', {
        email,
        password,
        name,
        deviceId: this.config.deviceId,
        deviceType: this.config.deviceType,
        platform: this.config.platform
      });

      this.authToken = response.data.token;
      this.saveTokenToStorage();

      console.log('✅ Registered successfully');
      return response.data.user;
    } catch (error) {
      console.error('❌ Registration failed:', error);
      throw error;
    }
  }

  /**
   * Logout
   */
  async logout(): Promise<void> {
    try {
      await this.http.post('/auth/logout', {
        deviceId: this.config.deviceId
      });

      this.authToken = null;
      this.clearTokenFromStorage();

      console.log('✅ Logged out');
    } catch (error) {
      console.error('❌ Logout failed:', error);
      throw error;
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<void> {
    if (!this.authToken?.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await this.http.post('/auth/refresh', {
        refreshToken: this.authToken.refreshToken,
        deviceId: this.config.deviceId
      });

      this.authToken = response.data.token;
      this.saveTokenToStorage();

      console.log('✅ Token refreshed');
    } catch (error) {
      console.error('❌ Token refresh failed:', error);
      this.authToken = null;
      this.clearTokenFromStorage();
      throw error;
    }
  }

  /**
   * Check if authenticated
   */
  isAuthenticated(): boolean {
    if (!this.authToken) return false;
    
    // Check if token is expired
    const now = Date.now();
    if (this.authToken.expiresAt < now) {
      return false;
    }

    return true;
  }

  /**
   * Get access token
   */
  getAccessToken(): string | null {
    return this.authToken?.accessToken || null;
  }

  /**
   * Get user ID
   */
  getUserId(): string | null {
    return this.authToken?.userId || null;
  }

  /**
   * Register device
   */
  async registerDevice(deviceName: string): Promise<void> {
    try {
      await this.http.post('/devices/register', {
        deviceId: this.config.deviceId,
        deviceType: this.config.deviceType,
        platform: this.config.platform,
        name: deviceName
      });

      console.log('✅ Device registered');
    } catch (error) {
      console.error('❌ Device registration failed:', error);
      throw error;
    }
  }

  /**
   * Save token to storage (platform-specific)
   */
  private saveTokenToStorage(): void {
    if (!this.authToken) return;

    try {
      // For React Native, use AsyncStorage
      // For Tauri/Web, use localStorage
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem(this.storageKey, JSON.stringify(this.authToken));
      }
      // AsyncStorage would be injected by React Native app
    } catch (error) {
      console.error('Failed to save token:', error);
    }
  }

  /**
   * Load token from storage
   */
  private loadTokenFromStorage(): void {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const stored = localStorage.getItem(this.storageKey);
        if (stored) {
          this.authToken = JSON.parse(stored);
          
          // Verify not expired
          if (this.authToken && this.authToken.expiresAt < Date.now()) {
            this.authToken = null;
            this.clearTokenFromStorage();
          }
        }
      }
    } catch (error) {
      console.error('Failed to load token:', error);
    }
  }

  /**
   * Clear token from storage
   */
  private clearTokenFromStorage(): void {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.removeItem(this.storageKey);
      }
    } catch (error) {
      console.error('Failed to clear token:', error);
    }
  }

  /**
   * Connect to WebSocket
   */
  private async connectWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket = io(this.config.wsUrl, {
        auth: {
          token: this.getAccessToken(),
          deviceId: this.config.deviceId,
          deviceType: this.config.deviceType
        },
        transports: ['websocket', 'polling']
      });

      this.socket.on('connect', () => {
        this.emit('connected');
        resolve();
      });

      this.socket.on('disconnect', () => {
        this.emit('disconnected');
      });

      this.socket.on('connect_error', (error) => {
        reject(error);
      });

      // Setup event listeners
      this.setupWebSocketListeners();
    });
  }

  /**
   * Setup WebSocket event listeners
   */
  private setupWebSocketListeners(): void {
    if (!this.socket) return;

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
      this.sync.handleSyncEvent(event);
    });

    this.socket.on('permission_request', (data: any) => {
      this.emit('permission_request', data);
    });
  }
}

export default AuthManager;

