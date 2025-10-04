/**
 * Database Manager for JarvisX Orchestrator
 * Handles SQLite database operations with connection pooling and migrations
 */

import sqlite3 from 'sqlite3';
import path from 'path';
import fs from 'fs/promises';

export interface DatabaseConfig {
  databasePath: string;
  enableWAL: boolean;
  busyTimeout: number;
}

export interface TaskRecord {
  id: string;
  user_id: string;
  status: 'pending' | 'approved' | 'rejected' | 'executing' | 'completed' | 'failed';
  intent: string;
  user_text: string;
  task_data: string; // JSON string
  created_at: string;
  updated_at: string;
  approved_by?: string;
  approved_at?: string;
  executed_at?: string;
  error_message?: string;
}

export interface AuditLogRecord {
  id: string;
  task_id?: string;
  user_id?: string;
  action: string;
  details: string; // JSON string
  timestamp: string;
  ip_address?: string;
  user_agent?: string;
}

export interface UserRecord {
  id: string;
  username: string;
  email: string;
  password_hash: string;
  permissions: string; // JSON string
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export class DatabaseManager {
  private db: sqlite3.Database | null = null;
  private config: DatabaseConfig;

  constructor(config?: Partial<DatabaseConfig>) {
    this.config = {
      databasePath: config?.databasePath || path.join(process.cwd(), 'data', 'jarvisx.db'),
      enableWAL: config?.enableWAL ?? true,
      busyTimeout: config?.busyTimeout || 5000
    };
  }

  public async initialize(): Promise<void> {
    try {
      // Ensure data directory exists
      const dataDir = path.dirname(this.config.databasePath);
      await fs.mkdir(dataDir, { recursive: true });

      // Open database connection
      this.db = new sqlite3.Database(this.config.databasePath);
      
      // Configure database
      await this.configureDatabase();
      
      // Run migrations
      await this.runMigrations();
      
      console.log(`✅ Database initialized: ${this.config.databasePath}`);
    } catch (error) {
      console.error('❌ Database initialization failed:', error);
      throw error;
    }
  }

  private async configureDatabase(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.serialize(() => {
        // Enable WAL mode for better concurrency
        if (this.config.enableWAL) {
          this.db!.run('PRAGMA journal_mode=WAL', (err) => {
            if (err) reject(err);
          });
        }

        // Set busy timeout
        this.db!.run(`PRAGMA busy_timeout=${this.config.busyTimeout}`, (err) => {
          if (err) reject(err);
        });

        // Enable foreign keys
        this.db!.run('PRAGMA foreign_keys=ON', (err) => {
          if (err) reject(err);
          else resolve();
        });
      });
    });
  }

  private async runMigrations(): Promise<void> {
    const migrations = [
      this.createUsersTable,
      this.createTasksTable,
      this.createAuditLogTable,
      this.createPermissionsTable,
      this.createExecutorLogsTable
    ];

    for (const migration of migrations) {
      await migration.call(this);
    }
  }

  private async createUsersTable(): Promise<void> {
    const sql = `
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        permissions TEXT DEFAULT '[]',
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME
      )
    `;
    
    await this.run(sql);
  }

  private async createTasksTable(): Promise<void> {
    const sql = `
      CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'executing', 'completed', 'failed')),
        intent TEXT NOT NULL,
        user_text TEXT NOT NULL,
        task_data TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        approved_by TEXT,
        approved_at DATETIME,
        executed_at DATETIME,
        error_message TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (approved_by) REFERENCES users(id)
      )
    `;
    
    await this.run(sql);
  }

  private async createAuditLogTable(): Promise<void> {
    const sql = `
      CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        task_id TEXT,
        user_id TEXT,
        action TEXT NOT NULL,
        details TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT,
        user_agent TEXT,
        FOREIGN KEY (task_id) REFERENCES tasks(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
      )
    `;
    
    await this.run(sql);
  }

  private async createPermissionsTable(): Promise<void> {
    const sql = `
      CREATE TABLE IF NOT EXISTS permissions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        permission TEXT NOT NULL,
        resource TEXT,
        granted_by TEXT,
        granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        expires_at DATETIME,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (granted_by) REFERENCES users(id),
        UNIQUE(user_id, permission, resource)
      )
    `;
    
    await this.run(sql);
  }

  private async createExecutorLogsTable(): Promise<void> {
    const sql = `
      CREATE TABLE IF NOT EXISTS executor_logs (
        id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL,
        executor_name TEXT NOT NULL,
        action TEXT NOT NULL,
        input_data TEXT,
        output_data TEXT,
        status TEXT CHECK(status IN ('success', 'error', 'timeout')),
        duration_ms INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        error_message TEXT,
        FOREIGN KEY (task_id) REFERENCES tasks(id)
      )
    `;
    
    await this.run(sql);
  }

  // Generic database operations
  public async run(sql: string, params: any[] = []): Promise<sqlite3.RunResult> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve(this);
      });
    });
  }

  public async get<T = any>(sql: string, params: any[] = []): Promise<T | undefined> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.get(sql, params, (err, row) => {
        if (err) reject(err);
        else resolve(row as T);
      });
    });
  }

  public async all<T = any>(sql: string, params: any[] = []): Promise<T[]> {
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows as T[]);
      });
    });
  }

  // Task operations
  public async createTask(task: Omit<TaskRecord, 'id' | 'created_at' | 'updated_at'>): Promise<string> {
    const id = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const now = new Date().toISOString();
    
    const sql = `
      INSERT INTO tasks (id, user_id, status, intent, user_text, task_data, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `;
    
    await this.run(sql, [
      id,
      task.user_id,
      task.status,
      task.intent,
      task.user_text,
      task.task_data,
      now,
      now
    ]);
    
    return id;
  }

  public async getTask(id: string): Promise<TaskRecord | undefined> {
    return this.get<TaskRecord>('SELECT * FROM tasks WHERE id = ?', [id]);
  }

  public async updateTaskStatus(
    id: string, 
    status: TaskRecord['status'], 
    approvedBy?: string,
    errorMessage?: string
  ): Promise<void> {
    const now = new Date().toISOString();
    let sql = 'UPDATE tasks SET status = ?, updated_at = ?';
    const params: any[] = [status, now];

    if (status === 'approved' && approvedBy) {
      sql += ', approved_by = ?, approved_at = ?';
      params.push(approvedBy, now);
    }

    if (status === 'executing') {
      sql += ', executed_at = ?';
      params.push(now);
    }

    if (errorMessage) {
      sql += ', error_message = ?';
      params.push(errorMessage);
    }

    sql += ' WHERE id = ?';
    params.push(id);

    await this.run(sql, params);
  }

  public async getTasksForUser(userId: string, limit: number = 50): Promise<TaskRecord[]> {
    return this.all<TaskRecord>(
      'SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
      [userId, limit]
    );
  }

  public async getPendingTasks(limit: number = 100): Promise<TaskRecord[]> {
    return this.all<TaskRecord>(
      'SELECT * FROM tasks WHERE status = "pending" ORDER BY created_at ASC LIMIT ?',
      [limit]
    );
  }

  // Audit log operations
  public async logAuditEvent(logEntry: Omit<AuditLogRecord, 'id' | 'timestamp'>): Promise<string> {
    const id = `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const timestamp = new Date().toISOString();
    
    const sql = `
      INSERT INTO audit_logs (id, task_id, user_id, action, details, timestamp, ip_address, user_agent)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `;
    
    await this.run(sql, [
      id,
      logEntry.task_id,
      logEntry.user_id,
      logEntry.action,
      logEntry.details,
      timestamp,
      logEntry.ip_address,
      logEntry.user_agent
    ]);
    
    return id;
  }

  public async getAuditLogs(taskId?: string, userId?: string, limit: number = 100): Promise<AuditLogRecord[]> {
    let sql = 'SELECT * FROM audit_logs WHERE 1=1';
    const params: any[] = [];

    if (taskId) {
      sql += ' AND task_id = ?';
      params.push(taskId);
    }

    if (userId) {
      sql += ' AND user_id = ?';
      params.push(userId);
    }

    sql += ' ORDER BY timestamp DESC LIMIT ?';
    params.push(limit);

    return this.all<AuditLogRecord>(sql, params);
  }

  // User operations
  public async createUser(user: Omit<UserRecord, 'id' | 'created_at' | 'updated_at'>): Promise<string> {
    const id = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const now = new Date().toISOString();
    
    const sql = `
      INSERT INTO users (id, username, email, password_hash, permissions, is_active, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `;
    
    await this.run(sql, [
      id,
      user.username,
      user.email,
      user.password_hash,
      user.permissions,
      user.is_active,
      now,
      now
    ]);
    
    return id;
  }

  public async getUserByUsername(username: string): Promise<UserRecord | undefined> {
    return this.get<UserRecord>('SELECT * FROM users WHERE username = ? AND is_active = 1', [username]);
  }

  public async getUserById(id: string): Promise<UserRecord | undefined> {
    return this.get<UserRecord>('SELECT * FROM users WHERE id = ? AND is_active = 1', [id]);
  }

  public async close(): Promise<void> {
    if (this.db) {
      return new Promise((resolve, reject) => {
        this.db!.close((err) => {
          if (err) reject(err);
          else {
            this.db = null;
            resolve();
          }
        });
      });
    }
  }
}
