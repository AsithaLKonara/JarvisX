/**
 * Memory System - Persistent, human-like memory for JarvisX
 */

import { EventEmitter } from 'events';
import * as sqlite3 from 'sqlite3';
import { promisify } from 'util';

export interface Memory {
  id: string;
  content: string;
  type: 'conversation' | 'preference' | 'fact' | 'skill' | 'relationship' | 'context' | 'achievement';
  importance: number;        // 1-10
  confidence: number;        // 0-100
  tags: string[];
  context: any;
  createdAt: Date;
  lastAccessed: Date;
  accessCount: number;
  emotionalWeight: number;   // How emotionally significant
  source: string;           // Where this memory came from
}

export interface MemoryQuery {
  type?: string;
  tags?: string[];
  importance?: { min?: number; max?: number };
  dateRange?: { start?: Date; end?: Date };
  limit?: number;
  searchText?: string;
}

export interface UserProfile {
  userId: string;
  name?: string;
  preferences: Map<string, any>;
  communicationStyle: any;
  expertise: string[];
  interests: string[];
  relationshipLevel: 'stranger' | 'acquaintance' | 'friend' | 'close_friend' | 'collaborator';
  trustLevel: number;       // 0-100
  interactionCount: number;
  lastInteraction: Date;
  createdAt: Date;
}

export class MemorySystem extends EventEmitter {
  private db: sqlite3.Database;
  private dbPromises: {
    run: (sql: string, params?: any[]) => Promise<any>;
    get: (sql: string, params?: any[]) => Promise<any>;
    all: (sql: string, params?: any[]) => Promise<any[]>;
  };
  private memoryCache: Map<string, Memory>;
  private userProfiles: Map<string, UserProfile>;
  private memoryIndex: Map<string, Set<string>>; // tag -> memory IDs
  private lastCleanup: Date;

  constructor() {
    super();
    this.memoryCache = new Map();
    this.userProfiles = new Map();
    this.memoryIndex = new Map();
    this.lastCleanup = new Date();
    
    this.initializeDatabase();
  }

  private async initializeDatabase(): Promise<void> {
    this.db = new sqlite3.Database(':memory:'); // In-memory for now, can be persisted
    
    this.dbPromises = {
      run: promisify(this.db.run.bind(this.db)),
      get: promisify(this.db.get.bind(this.db)),
      all: promisify(this.db.all.bind(this.db))
    };

    // Create tables
    await this.dbPromises.run(`
      CREATE TABLE IF NOT EXISTS memories (
        id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        type TEXT NOT NULL,
        importance INTEGER NOT NULL,
        confidence INTEGER NOT NULL,
        tags TEXT,
        context TEXT,
        created_at TEXT NOT NULL,
        last_accessed TEXT NOT NULL,
        access_count INTEGER DEFAULT 0,
        emotional_weight INTEGER DEFAULT 0,
        source TEXT,
        user_id TEXT
      )
    `);

    await this.dbPromises.run(`
      CREATE TABLE IF NOT EXISTS user_profiles (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        preferences TEXT,
        communication_style TEXT,
        expertise TEXT,
        interests TEXT,
        relationship_level TEXT DEFAULT 'stranger',
        trust_level INTEGER DEFAULT 50,
        interaction_count INTEGER DEFAULT 0,
        last_interaction TEXT,
        created_at TEXT
      )
    `);

    // Create indexes
    await this.dbPromises.run(`CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)`);
    await this.dbPromises.run(`CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)`);
    await this.dbPromises.run(`CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories(tags)`);
    await this.dbPromises.run(`CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(user_id)`);

    console.log('🧠 Memory System database initialized');
  }

  public async addMemory(
    content: string, 
    type: Memory['type'], 
    importance: number = 5, 
    tags: string[] = [],
    context: any = {},
    source: string = 'user',
    userId: string = 'default'
  ): Promise<string> {
    const id = this.generateMemoryId();
    const now = new Date();
    
    const memory: Memory = {
      id,
      content,
      type,
      importance,
      confidence: 90, // Default high confidence
      tags,
      context,
      createdAt: now,
      lastAccessed: now,
      accessCount: 0,
      emotionalWeight: this.calculateEmotionalWeight(content, context),
      source
    };

    // Store in database
    await this.dbPromises.run(`
      INSERT INTO memories 
      (id, content, type, importance, confidence, tags, context, created_at, last_accessed, access_count, emotional_weight, source, user_id)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      id, content, type, importance, memory.confidence, 
      JSON.stringify(tags), JSON.stringify(context), 
      now.toISOString(), now.toISOString(), 0, 
      memory.emotionalWeight, source, userId
    ]);

    // Cache in memory
    this.memoryCache.set(id, memory);
    
    // Update index
    tags.forEach(tag => {
      if (!this.memoryIndex.has(tag)) {
        this.memoryIndex.set(tag, new Set());
      }
      this.memoryIndex.get(tag)!.add(id);
    });

    // Update user profile
    await this.updateUserProfile(userId, { interactionCount: 1 });

    this.emit('memoryAdded', memory);
    console.log(`🧠 Memory added: ${type} - "${content.substring(0, 50)}..." (importance: ${importance})`);

    return id;
  }

  public async getMemory(id: string): Promise<Memory | null> {
    // Check cache first
    if (this.memoryCache.has(id)) {
      const memory = this.memoryCache.get(id)!;
      this.updateAccess(memory);
      return memory;
    }

    // Load from database
    const row = await this.dbPromises.get(`SELECT * FROM memories WHERE id = ?`, [id]);
    if (!row) return null;

    const memory = this.rowToMemory(row);
    this.memoryCache.set(id, memory);
    this.updateAccess(memory);
    
    return memory;
  }

  public async searchMemories(query: MemoryQuery, userId: string = 'default'): Promise<Memory[]> {
    let sql = `SELECT * FROM memories WHERE user_id = ?`;
    const params: any[] = [userId];

    // Build query conditions
    if (query.type) {
      sql += ` AND type = ?`;
      params.push(query.type);
    }

    if (query.importance) {
      if (query.importance.min !== undefined) {
        sql += ` AND importance >= ?`;
        params.push(query.importance.min);
      }
      if (query.importance.max !== undefined) {
        sql += ` AND importance <= ?`;
        params.push(query.importance.max);
      }
    }

    if (query.dateRange) {
      if (query.dateRange.start) {
        sql += ` AND created_at >= ?`;
        params.push(query.dateRange.start.toISOString());
      }
      if (query.dateRange.end) {
        sql += ` AND created_at <= ?`;
        params.push(query.dateRange.end.toISOString());
      }
    }

    if (query.tags && query.tags.length > 0) {
      const tagConditions = query.tags.map(() => `tags LIKE ?`);
      sql += ` AND (${tagConditions.join(' OR ')})`;
      query.tags.forEach(tag => params.push(`%"${tag}"%`));
    }

    if (query.searchText) {
      sql += ` AND content LIKE ?`;
      params.push(`%${query.searchText}%`);
    }

    // Order by importance and recency
    sql += ` ORDER BY importance DESC, created_at DESC`;

    if (query.limit) {
      sql += ` LIMIT ?`;
      params.push(query.limit);
    }

    const rows = await this.dbPromises.all(sql, params);
    const memories = rows.map(row => this.rowToMemory(row));

    // Update access counts
    memories.forEach(memory => this.updateAccess(memory));

    return memories;
  }

  public async getRecentMemories(limit: number = 10, userId: string = 'default'): Promise<Memory[]> {
    return this.searchMemories({ limit }, userId);
  }

  public async getMemoriesByType(type: Memory['type'], limit?: number, userId: string = 'default'): Promise<Memory[]> {
    return this.searchMemories({ type, limit }, userId);
  }

  public async getImportantMemories(minImportance: number = 7, userId: string = 'default'): Promise<Memory[]> {
    return this.searchMemories({ importance: { min: minImportance } }, userId);
  }

  public async getMemoriesByTag(tag: string, userId: string = 'default'): Promise<Memory[]> {
    return this.searchMemories({ tags: [tag] }, userId);
  }

  public async updateMemory(id: string, updates: Partial<Memory>): Promise<boolean> {
    const memory = await this.getMemory(id);
    if (!memory) return false;

    const updatedMemory = { ...memory, ...updates };
    
    await this.dbPromises.run(`
      UPDATE memories SET 
        content = ?, importance = ?, confidence = ?, tags = ?, context = ?, emotional_weight = ?
      WHERE id = ?
    `, [
      updatedMemory.content,
      updatedMemory.importance,
      updatedMemory.confidence,
      JSON.stringify(updatedMemory.tags),
      JSON.stringify(updatedMemory.context),
      updatedMemory.emotionalWeight,
      id
    ]);

    this.memoryCache.set(id, updatedMemory);
    this.emit('memoryUpdated', updatedMemory);
    
    return true;
  }

  public async deleteMemory(id: string): Promise<boolean> {
    const memory = await this.getMemory(id);
    if (!memory) return false;

    await this.dbPromises.run(`DELETE FROM memories WHERE id = ?`, [id]);
    this.memoryCache.delete(id);
    
    // Update index
    memory.tags.forEach(tag => {
      const memorySet = this.memoryIndex.get(tag);
      if (memorySet) {
        memorySet.delete(id);
        if (memorySet.size === 0) {
          this.memoryIndex.delete(tag);
        }
      }
    });

    this.emit('memoryDeleted', memory);
    return true;
  }

  public async createUserProfile(userId: string, name?: string): Promise<UserProfile> {
    const profile: UserProfile = {
      userId,
      name,
      preferences: new Map(),
      communicationStyle: {},
      expertise: [],
      interests: [],
      relationshipLevel: 'stranger',
      trustLevel: 50,
      interactionCount: 0,
      lastInteraction: new Date(),
      createdAt: new Date()
    };

    await this.dbPromises.run(`
      INSERT INTO user_profiles 
      (user_id, name, preferences, communication_style, expertise, interests, relationship_level, trust_level, interaction_count, last_interaction, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      userId, name, JSON.stringify({}), JSON.stringify({}), 
      JSON.stringify([]), JSON.stringify([]), 'stranger', 50, 0,
      new Date().toISOString(), new Date().toISOString()
    ]);

    this.userProfiles.set(userId, profile);
    this.emit('userProfileCreated', profile);
    
    return profile;
  }

  public async getUserProfile(userId: string): Promise<UserProfile | null> {
    if (this.userProfiles.has(userId)) {
      return this.userProfiles.get(userId)!;
    }

    const row = await this.dbPromises.get(`SELECT * FROM user_profiles WHERE user_id = ?`, [userId]);
    if (!row) return null;

    const profile: UserProfile = {
      userId: row.user_id,
      name: row.name,
      preferences: new Map(Object.entries(JSON.parse(row.preferences || '{}'))),
      communicationStyle: JSON.parse(row.communication_style || '{}'),
      expertise: JSON.parse(row.expertise || '[]'),
      interests: JSON.parse(row.interests || '[]'),
      relationshipLevel: row.relationship_level,
      trustLevel: row.trust_level,
      interactionCount: row.interaction_count,
      lastInteraction: new Date(row.last_interaction),
      createdAt: new Date(row.created_at)
    };

    this.userProfiles.set(userId, profile);
    return profile;
  }

  public async updateUserProfile(userId: string, updates: Partial<UserProfile>): Promise<boolean> {
    let profile = await this.getUserProfile(userId);
    if (!profile) {
      profile = await this.createUserProfile(userId);
    }

    const updatedProfile = { ...profile, ...updates };
    
    await this.dbPromises.run(`
      UPDATE user_profiles SET 
        name = ?, preferences = ?, communication_style = ?, expertise = ?, 
        interests = ?, relationship_level = ?, trust_level = ?, 
        interaction_count = ?, last_interaction = ?
      WHERE user_id = ?
    `, [
      updatedProfile.name,
      JSON.stringify(Object.fromEntries(updatedProfile.preferences)),
      JSON.stringify(updatedProfile.communicationStyle),
      JSON.stringify(updatedProfile.expertise),
      JSON.stringify(updatedProfile.interests),
      updatedProfile.relationshipLevel,
      updatedProfile.trustLevel,
      updatedProfile.interactionCount,
      updatedProfile.lastInteraction.toISOString(),
      userId
    ]);

    this.userProfiles.set(userId, updatedProfile);
    this.emit('userProfileUpdated', updatedProfile);
    
    return true;
  }

  public async updatePreferences(userId: string, preferences: Map<string, any>): Promise<void> {
    await this.updateUserProfile(userId, { preferences });
    console.log(`🧠 Preferences updated for user ${userId}`);
  }

  public async learnFromInteraction(
    userId: string, 
    interaction: any, 
    outcome: 'success' | 'failure' | 'partial'
  ): Promise<void> {
    // Extract learnings from interaction
    const learnings = this.extractLearnings(interaction, outcome);
    
    for (const learning of learnings) {
      await this.addMemory(
        learning.content,
        learning.type,
        learning.importance,
        learning.tags,
        learning.context,
        'interaction',
        userId
      );
    }

    // Update user profile
    const profile = await this.getUserProfile(userId);
    if (profile) {
      const newInteractionCount = profile.interactionCount + 1;
      let trustLevel = profile.trustLevel;
      
      if (outcome === 'success') {
        trustLevel = Math.min(100, trustLevel + 1);
      } else if (outcome === 'failure') {
        trustLevel = Math.max(0, trustLevel - 1);
      }
      
      await this.updateUserProfile(userId, {
        interactionCount: newInteractionCount,
        trustLevel,
        lastInteraction: new Date()
      });
    }
  }

  private extractLearnings(interaction: any, outcome: string): any[] {
    const learnings: any[] = [];
    
    // Extract user preferences
    if (interaction.userFeedback) {
      learnings.push({
        content: `User preference: ${interaction.userFeedback}`,
        type: 'preference' as Memory['type'],
        importance: 7,
        tags: ['preference', 'user_feedback'],
        context: interaction
      });
    }
    
    // Extract successful patterns
    if (outcome === 'success') {
      learnings.push({
        content: `Successful interaction pattern: ${interaction.type}`,
        type: 'skill' as Memory['type'],
        importance: 6,
        tags: ['success', 'pattern'],
        context: interaction
      });
    }
    
    // Extract contextual information
    if (interaction.context) {
      learnings.push({
        content: `Contextual information: ${JSON.stringify(interaction.context)}`,
        type: 'context' as Memory['type'],
        importance: 4,
        tags: ['context', 'environment'],
        context: interaction
      });
    }
    
    return learnings;
  }

  public getMemoryCount(): number {
    return this.memoryCache.size;
  }

  public async getMemoryStats(): Promise<any> {
    const stats = await this.dbPromises.get(`
      SELECT 
        COUNT(*) as total_memories,
        AVG(importance) as avg_importance,
        AVG(confidence) as avg_confidence,
        AVG(access_count) as avg_access_count
      FROM memories
    `);

    const typeStats = await this.dbPromises.all(`
      SELECT type, COUNT(*) as count 
      FROM memories 
      GROUP BY type
    `);

    return {
      totalMemories: stats.total_memories,
      averageImportance: Math.round(stats.avg_importance || 0),
      averageConfidence: Math.round(stats.avg_confidence || 0),
      averageAccessCount: Math.round(stats.avg_access_count || 0),
      memoriesByType: typeStats.reduce((acc, row) => {
        acc[row.type] = row.count;
        return acc;
      }, {} as any),
      cacheSize: this.memoryCache.size,
      indexSize: this.memoryIndex.size
    };
  }

  private generateMemoryId(): string {
    return `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private rowToMemory(row: any): Memory {
    return {
      id: row.id,
      content: row.content,
      type: row.type,
      importance: row.importance,
      confidence: row.confidence,
      tags: JSON.parse(row.tags || '[]'),
      context: JSON.parse(row.context || '{}'),
      createdAt: new Date(row.created_at),
      lastAccessed: new Date(row.last_accessed),
      accessCount: row.access_count,
      emotionalWeight: row.emotional_weight,
      source: row.source
    };
  }

  private updateAccess(memory: Memory): void {
    memory.accessCount++;
    memory.lastAccessed = new Date();
    
    // Update in database
    this.dbPromises.run(`
      UPDATE memories SET access_count = ?, last_accessed = ? WHERE id = ?
    `, [memory.accessCount, memory.lastAccessed.toISOString(), memory.id]);
  }

  private calculateEmotionalWeight(content: string, context: any): number {
    let weight = 5; // Base weight
    
    // Increase weight for emotional keywords
    const emotionalKeywords = [
      'love', 'hate', 'excited', 'frustrated', 'happy', 'sad', 
      'amazing', 'terrible', 'perfect', 'awful', 'incredible', 'disappointing'
    ];
    
    emotionalKeywords.forEach(keyword => {
      if (content.toLowerCase().includes(keyword)) {
        weight += 2;
      }
    });
    
    // Increase weight for personal information
    const personalKeywords = [
      'name', 'family', 'friend', 'work', 'home', 'personal', 
      'private', 'secret', 'important', 'special'
    ];
    
    personalKeywords.forEach(keyword => {
      if (content.toLowerCase().includes(keyword)) {
        weight += 1;
      }
    });
    
    return Math.min(10, weight);
  }

  public async cleanup(): Promise<void> {
    const now = new Date();
    const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    
    // Remove old, low-importance memories that haven't been accessed
    await this.dbPromises.run(`
      DELETE FROM memories 
      WHERE importance < 3 
      AND last_accessed < ? 
      AND access_count < 2
    `, [oneDayAgo.toISOString()]);
    
    this.lastCleanup = now;
    console.log('🧠 Memory cleanup completed');
  }
}
