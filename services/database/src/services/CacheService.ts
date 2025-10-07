/**
 * Cache Service
 * Redis-based caching for improved performance
 */

import { redisClient } from '../config/database';

export interface CacheOptions {
  ttl?: number; // Time to live in seconds
  tags?: string[]; // Cache tags for invalidation
}

export class CacheService {
  private static instance: CacheService;
  private isConnected: boolean = false;

  private constructor() {
    this.initialize();
  }

  public static getInstance(): CacheService {
    if (!CacheService.instance) {
      CacheService.instance = new CacheService();
    }
    return CacheService.instance;
  }

  private async initialize(): Promise<void> {
    try {
      await redisClient.connect();
      this.isConnected = true;
      console.log('✅ Cache Service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Cache Service:', error);
      this.isConnected = false;
    }
  }

  public async set(key: string, value: any, options: CacheOptions = {}): Promise<boolean> {
    if (!this.isConnected) {
      console.warn('⚠️ Cache not connected, skipping set operation');
      return false;
    }

    try {
      const serializedValue = JSON.stringify(value);
      const ttl = options.ttl || 3600; // Default 1 hour

      await redisClient.setEx(key, ttl, serializedValue);

      // Store tags for invalidation
      if (options.tags && options.tags.length > 0) {
        for (const tag of options.tags) {
          await redisClient.sAdd(`tag:${tag}`, key);
        }
      }

      return true;
    } catch (error) {
      console.error('❌ Cache set error:', error);
      return false;
    }
  }

  public async get<T = any>(key: string): Promise<T | null> {
    if (!this.isConnected) {
      console.warn('⚠️ Cache not connected, skipping get operation');
      return null;
    }

    try {
      const value = await redisClient.get(key);
      if (!value) {
        return null;
      }

      return JSON.parse(value) as T;
    } catch (error) {
      console.error('❌ Cache get error:', error);
      return null;
    }
  }

  public async del(key: string): Promise<boolean> {
    if (!this.isConnected) {
      console.warn('⚠️ Cache not connected, skipping delete operation');
      return false;
    }

    try {
      const result = await redisClient.del(key);
      return result > 0;
    } catch (error) {
      console.error('❌ Cache delete error:', error);
      return false;
    }
  }

  public async exists(key: string): Promise<boolean> {
    if (!this.isConnected) {
      return false;
    }

    try {
      const result = await redisClient.exists(key);
      return result === 1;
    } catch (error) {
      console.error('❌ Cache exists error:', error);
      return false;
    }
  }

  public async expire(key: string, ttl: number): Promise<boolean> {
    if (!this.isConnected) {
      return false;
    }

    try {
      const result = await redisClient.expire(key, ttl);
      return result;
    } catch (error) {
      console.error('❌ Cache expire error:', error);
      return false;
    }
  }

  public async ttl(key: string): Promise<number> {
    if (!this.isConnected) {
      return -1;
    }

    try {
      return await redisClient.ttl(key);
    } catch (error) {
      console.error('❌ Cache TTL error:', error);
      return -1;
    }
  }

  public async invalidateByTag(tag: string): Promise<boolean> {
    if (!this.isConnected) {
      return false;
    }

    try {
      const keys = await redisClient.sMembers(`tag:${tag}`);
      if (keys.length > 0) {
        await redisClient.del(keys);
        await redisClient.del(`tag:${tag}`);
      }
      return true;
    } catch (error) {
      console.error('❌ Cache tag invalidation error:', error);
      return false;
    }
  }

  public async invalidateByPattern(pattern: string): Promise<boolean> {
    if (!this.isConnected) {
      return false;
    }

    try {
      const keys = await redisClient.keys(pattern);
      if (keys.length > 0) {
        await redisClient.del(keys);
      }
      return true;
    } catch (error) {
      console.error('❌ Cache pattern invalidation error:', error);
      return false;
    }
  }

  public async flush(): Promise<boolean> {
    if (!this.isConnected) {
      return false;
    }

    try {
      await redisClient.flushAll();
      return true;
    } catch (error) {
      console.error('❌ Cache flush error:', error);
      return false;
    }
  }

  public async getStats(): Promise<any> {
    if (!this.isConnected) {
      return null;
    }

    try {
      const info = await redisClient.info('memory');
      const dbSize = await redisClient.dbSize();
      
      return {
        connected: this.isConnected,
        dbSize,
        memory: info,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('❌ Cache stats error:', error);
      return null;
    }
  }

  // Specific caching methods for JarvisX
  public async cacheUser(userId: string, userData: any, ttl: number = 3600): Promise<boolean> {
    return this.set(`user:${userId}`, userData, { ttl, tags: ['users'] });
  }

  public async getCachedUser(userId: string): Promise<any> {
    return this.get(`user:${userId}`);
  }

  public async cacheCommand(commandId: string, commandData: any, ttl: number = 1800): Promise<boolean> {
    return this.set(`command:${commandId}`, commandData, { ttl, tags: ['commands'] });
  }

  public async getCachedCommand(commandId: string): Promise<any> {
    return this.get(`command:${commandId}`);
  }

  public async cacheApprovalRequest(requestId: string, requestData: any, ttl: number = 1800): Promise<boolean> {
    return this.set(`approval:${requestId}`, requestData, { ttl, tags: ['approvals'] });
  }

  public async getCachedApprovalRequest(requestId: string): Promise<any> {
    return this.get(`approval:${requestId}`);
  }

  public async cacheSystemStats(stats: any, ttl: number = 60): Promise<boolean> {
    return this.set('system:stats', stats, { ttl, tags: ['system'] });
  }

  public async getCachedSystemStats(): Promise<any> {
    return this.get('system:stats');
  }

  public async cacheLearningInsights(userId: string, insights: any, ttl: number = 3600): Promise<boolean> {
    return this.set(`learning:${userId}`, insights, { ttl, tags: ['learning', 'users'] });
  }

  public async getCachedLearningInsights(userId: string): Promise<any> {
    return this.get(`learning:${userId}`);
  }

  public async invalidateUserCache(userId: string): Promise<boolean> {
    const patterns = [
      `user:${userId}`,
      `learning:${userId}`,
      `command:*:${userId}`,
      `approval:*:${userId}`
    ];

    for (const pattern of patterns) {
      await this.invalidateByPattern(pattern);
    }

    return true;
  }

  public async invalidateAllCaches(): Promise<boolean> {
    return this.invalidateByPattern('*');
  }

  public isReady(): boolean {
    return this.isConnected;
  }
}

export default CacheService;
