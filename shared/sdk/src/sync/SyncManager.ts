/**
 * Sync Manager - Cross-device synchronization
 * Handles real-time state sync between devices
 */

import { AxiosInstance } from 'axios';
import type { JarvisXConfig, SyncEvent } from '../types';

export class SyncManager {
  private http: AxiosInstance;
  private config: JarvisXConfig;
  private syncQueue: SyncEvent[] = [];
  private isSyncing: boolean = false;

  constructor(http: AxiosInstance, config: JarvisXConfig) {
    this.http = http;
    this.config = config;
  }

  /**
   * Handle incoming sync event
   */
  handleSyncEvent(event: SyncEvent): void {
    console.log('📡 Sync event received:', event.type);

    // Add to queue
    this.syncQueue.push(event);

    // Process queue
    this.processSyncQueue();
  }

  /**
   * Send sync event to other devices
   */
  async sendSyncEvent(type: string, data: any): Promise<void> {
    const event: SyncEvent = {
      id: this.generateId(),
      type: type as any,
      data,
      deviceId: this.config.deviceId,
      timestamp: new Date().toISOString()
    };

    try {
      await this.http.post('/sync/events', event);
      console.log('📡 Sync event sent:', type);
    } catch (error) {
      console.error('❌ Failed to send sync event:', error);
      throw error;
    }
  }

  /**
   * Get sync status
   */
  async getSyncStatus(): Promise<any> {
    try {
      const response = await this.http.get('/sync/status', {
        params: { deviceId: this.config.deviceId }
      });
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get sync status:', error);
      throw error;
    }
  }

  /**
   * Force full sync
   */
  async forceSync(): Promise<void> {
    try {
      await this.http.post('/sync/force', {
        deviceId: this.config.deviceId
      });
      console.log('✅ Force sync completed');
    } catch (error) {
      console.error('❌ Force sync failed:', error);
      throw error;
    }
  }

  /**
   * Process sync queue
   */
  private async processSyncQueue(): Promise<void> {
    if (this.isSyncing || this.syncQueue.length === 0) return;

    this.isSyncing = true;

    while (this.syncQueue.length > 0) {
      const event = this.syncQueue.shift();
      if (event) {
        await this.processEvent(event);
      }
    }

    this.isSyncing = false;
  }

  /**
   * Process individual event
   */
  private async processEvent(event: SyncEvent): Promise<void> {
    // Different handling based on event type
    switch (event.type) {
      case 'task_update':
        // Update local task cache
        break;
      case 'avatar_update':
        // Update local avatar state
        break;
      case 'voice_command':
        // Process voice command
        break;
      default:
        console.log('Unknown sync event type:', event.type);
    }
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

export default SyncManager;

