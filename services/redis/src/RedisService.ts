/**
 * Redis Service
 * High-performance caching and session management
 */

import Redis from 'ioredis';
import { v4 as uuidv4 } from 'uuid';

export interface CacheOptions {
  ttl?: number; // Time to live in seconds
  tags?: string[]; // Cache tags for invalidation
  nx?: boolean; // Only set if key doesn't exist
  xx?: boolean; // Only set if key exists
}

export interface SessionData {
  userId: string;
  deviceId: string;
  deviceType: 'desktop' | 'mobile' | 'web';
  ipAddress: string;
  userAgent: string;
  createdAt: Date;
  lastActivity: Date;
  isActive: boolean;
  metadata?: any;
}

export interface PubSubMessage {
  channel: string;
  message: any;
  timestamp: number;
  id: string;
}

export class RedisService {
  private static instance: RedisService;
  private redis: Redis;
  private subscriber: Redis;
  private publisher: Redis;
  private isConnected: boolean = false;

  private constructor() {
    this.initialize();
  }

  public static getInstance(): RedisService {
    if (!RedisService.instance) {
      RedisService.instance = new RedisService();
    }
    return RedisService.instance;
  }

  private async initialize(): Promise<void> {
    try {
      // Main Redis connection
      this.redis = new Redis({
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        password: process.env.REDIS_PASSWORD,
        db: parseInt(process.env.REDIS_DB || '0'),
        retryDelayOnFailover: 100,
        maxRetriesPerRequest: 3,
        lazyConnect: true
      });

      // Subscriber connection
      this.subscriber = new Redis({
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        password: process.env.REDIS_PASSWORD,
        db: parseInt(process.env.REDIS_DB || '0'),
        retryDelayOnFailover: 100,
        maxRetriesPerRequest: 3,
        lazyConnect: true
      });

      // Publisher connection
      this.publisher = new Redis({
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        password: process.env.REDIS_PASSWORD,
        db: parseInt(process.env.REDIS_DB || '0'),
        retryDelayOnFailover: 100,
        maxRetriesPerRequest: 3,
        lazyConnect: true
      });

      // Event handlers
      this.redis.on('connect', () => {
        console.log('✅ Redis connected');
        this.isConnected = true;
      });

      this.redis.on('error', (err) => {
        console.error('❌ Redis error:', err);
        this.isConnected = false;
      });

      this.redis.on('disconnect', () => {
        console.log('🔌 Redis disconnected');
        this.isConnected = false;
      });

      // Connect
      await this.redis.connect();
      await this.subscriber.connect();
      await this.publisher.connect();

      console.log('✅ Redis Service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Redis Service:', error);
      this.isConnected = false;
    }
  }

  // Basic cache operations
  public async set(key: string, value: any, options: CacheOptions = {}): Promise<boolean> {
    if (!this.isConnected) {
      console.warn('⚠️ Redis not connected, skipping set operation');
      return false;
    }

    try {
      const serializedValue = JSON.stringify(value);
      const ttl = options.ttl || 3600; // Default 1 hour

      if (options.nx) {
        const result = await this.redis.setnx(key, serializedValue);
        if (result && ttl > 0) {
          await this.redis.expire(key, ttl);
        }
        return result === 1;
      } else if (options.xx) {
        const result = await this.redis.set(key, serializedValue, 'XX', 'EX', ttl);
        return result === 'OK';
      } else {
        await this.redis.setex(key, ttl, serializedValue);
      }

      // Store tags for invalidation
      if (options.tags && options.tags.length > 0) {
        for (const tag of options.tags) {
          await this.redis.sadd(`tag:${tag}`, key);
        }
      }

      return true;
    } catch (error) {
      console.error('❌ Redis set error:', error);
      return false;
    }
  }

  public async get<T = any>(key: string): Promise<T | null> {
    if (!this.isConnected) {
      console.warn('⚠️ Redis not connected, skipping get operation');
      return null;
    }

    try {
      const value = await this.redis.get(key);
      if (!value) {
        return null;
      }

      return JSON.parse(value) as T;
    } catch (error) {
      console.error('❌ Redis get error:', error);
      return null;
    }
  }

  public async del(key: string): Promise<boolean> {
    if (!this.isConnected) {
      return false;
    }

    try {
      const result = await this.redis.del(key);
      return result > 0;
    } catch (error) {
      console.error('❌ Redis delete error:', error);
      return false;
    }
  }

  public async exists(key: string): Promise<boolean> {
    if (!this.isConnected) {
      return false;
    }

    try {
      const result = await this.redis.exists(key);
      return result === 1;
    } catch (error) {
      console.error('❌ Redis exists error:', error);
      return false;
    }
  }

  public async expire(key: string, ttl: number): Promise<boolean> {
    if (!this.isConnected) {
      return false;
    }

    try {
      const result = await this.redis.expire(key, ttl);
      return result === 1;
    } catch (error) {
      console.error('❌ Redis expire error:', error);
      return false;
    }
  }

  public async ttl(key: string): Promise<number> {
    if (!this.isConnected) {
      return -1;
    }

    try {
      return await this.redis.ttl(key);
    } catch (error) {
      console.error('❌ Redis TTL error:', error);
      return -1;
    }
  }

  // Session management
  public async createSession(sessionData: SessionData): Promise<string> {
    const sessionId = uuidv4();
    const key = `session:${sessionId}`;
    
    await this.set(key, sessionData, { ttl: 86400 }); // 24 hours
    
    // Add to user's active sessions
    await this.redis.sadd(`user_sessions:${sessionData.userId}`, sessionId);
    
    return sessionId;
  }

  public async getSession(sessionId: string): Promise<SessionData | null> {
    const key = `session:${sessionId}`;
    return this.get<SessionData>(key);
  }

  public async updateSession(sessionId: string, updates: Partial<SessionData>): Promise<boolean> {
    const session = await this.getSession(sessionId);
    if (!session) {
      return false;
    }

    const updatedSession = { ...session, ...updates, lastActivity: new Date() };
    const key = `session:${sessionId}`;
    
    return this.set(key, updatedSession, { ttl: 86400 });
  }

  public async deleteSession(sessionId: string): Promise<boolean> {
    const session = await this.getSession(sessionId);
    if (!session) {
      return false;
    }

    const key = `session:${sessionId}`;
    await this.del(key);
    
    // Remove from user's active sessions
    await this.redis.srem(`user_sessions:${session.userId}`, sessionId);
    
    return true;
  }

  public async getUserSessions(userId: string): Promise<string[]> {
    return this.redis.smembers(`user_sessions:${userId}`);
  }

  public async deleteUserSessions(userId: string): Promise<boolean> {
    const sessionIds = await this.getUserSessions(userId);
    
    for (const sessionId of sessionIds) {
      await this.deleteSession(sessionId);
    }
    
    return true;
  }

  // Pub/Sub messaging
  public async publish(channel: string, message: any): Promise<boolean> {
    if (!this.isConnected) {
      return false;
    }

    try {
      const pubMessage: PubSubMessage = {
        channel,
        message,
        timestamp: Date.now(),
        id: uuidv4()
      };

      const result = await this.publisher.publish(channel, JSON.stringify(pubMessage));
      return result > 0;
    } catch (error) {
      console.error('❌ Redis publish error:', error);
      return false;
    }
  }

  public async subscribe(channel: string, callback: (message: PubSubMessage) => void): Promise<void> {
    if (!this.isConnected) {
      return;
    }

    try {
      await this.subscriber.subscribe(channel);
      
      this.subscriber.on('message', (receivedChannel, message) => {
        if (receivedChannel === channel) {
          try {
            const pubMessage: PubSubMessage = JSON.parse(message);
            callback(pubMessage);
          } catch (error) {
            console.error('❌ Error parsing pub/sub message:', error);
          }
        }
      });
    } catch (error) {
      console.error('❌ Redis subscribe error:', error);
    }
  }

  public async unsubscribe(channel: string): Promise<void> {
    if (!this.isConnected) {
      return;
    }

    try {
      await this.subscriber.unsubscribe(channel);
    } catch (error) {
      console.error('❌ Redis unsubscribe error:', error);
    }
  }

  // Cache invalidation
  public async invalidateByTag(tag: string): Promise<boolean> {
    if (!this.isConnected) {
      return false;
    }

    try {
      const keys = await this.redis.smembers(`tag:${tag}`);
      if (keys.length > 0) {
        await this.redis.del(...keys);
        await this.redis.del(`tag:${tag}`);
      }
      return true;
    } catch (error) {
      console.error('❌ Redis tag invalidation error:', error);
      return false;
    }
  }

  public async invalidateByPattern(pattern: string): Promise<boolean> {
    if (!this.isConnected) {
      return false;
    }

    try {
      const keys = await this.redis.keys(pattern);
      if (keys.length > 0) {
        await this.redis.del(...keys);
      }
      return true;
    } catch (error) {
      console.error('❌ Redis pattern invalidation error:', error);
      return false;
    }
  }

  public async flush(): Promise<boolean> {
    if (!this.isConnected) {
      return false;
    }

    try {
      await this.redis.flushall();
      return true;
    } catch (error) {
      console.error('❌ Redis flush error:', error);
      return false;
    }
  }

  // Statistics and monitoring
  public async getStats(): Promise<any> {
    if (!this.isConnected) {
      return null;
    }

    try {
      const info = await this.redis.info();
      const dbSize = await this.redis.dbsize();
      const memory = await this.redis.memory('usage');
      
      return {
        connected: this.isConnected,
        dbSize,
        memory,
        info: info.split('\r\n').reduce((acc, line) => {
          if (line.includes(':')) {
            const [key, value] = line.split(':');
            acc[key] = value;
          }
          return acc;
        }, {}),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('❌ Redis stats error:', error);
      return null;
    }
  }

  // Specific JarvisX caching methods
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

  public isReady(): boolean {
    return this.isConnected;
  }

  public async disconnect(): Promise<void> {
    try {
      await this.redis.disconnect();
      await this.subscriber.disconnect();
      await this.publisher.disconnect();
      this.isConnected = false;
      console.log('✅ Redis connections closed');
    } catch (error) {
      console.error('❌ Error closing Redis connections:', error);
    }
  }
}

export default RedisService;
