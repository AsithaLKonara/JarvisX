/**
 * Permission Manager for JarvisX Orchestrator
 * Handles user permissions and access control
 */

import { DatabaseManager } from '../database/DatabaseManager';

export interface Permission {
  id: string;
  user_id: string;
  permission: string;
  resource?: string;
  granted_by?: string;
  granted_at: string;
  expires_at?: string;
  is_active: boolean;
}

export class PermissionManager {
  private dbManager: DatabaseManager;

  // Default permission scopes
  public static readonly PERMISSIONS = {
    // File operations
    READ_FILES: 'read_files',
    WRITE_FILES: 'write_files',
    DELETE_FILES: 'delete_files',
    
    // System operations
    RUN_COMMAND: 'run_command',
    ADMIN_ACCESS: 'admin_access',
    
    // Network operations
    NETWORK: 'network',
    
    // Credential access
    USE_CREDENTIALS: 'use_credentials',
    
    // Task management
    CREATE_TASKS: 'create_tasks',
    APPROVE_TASKS: 'approve_tasks',
    EXECUTE_TASKS: 'execute_tasks',
    
    // User management
    MANAGE_USERS: 'manage_users',
    
    // Admin operations
    VIEW_AUDIT_LOGS: 'view_audit_logs',
    SYSTEM_ADMIN: 'system_admin'
  };

  constructor(dbManager: DatabaseManager) {
    this.dbManager = dbManager;
  }

  /**
   * Check if user has specific permissions
   */
  public async checkUserPermissions(userId: string, requiredPermissions: string[]): Promise<boolean> {
    try {
      const userPermissions = await this.getUserPermissions(userId);
      
      for (const requiredPermission of requiredPermissions) {
        if (!userPermissions.includes(requiredPermission)) {
          console.log(`❌ User ${userId} missing permission: ${requiredPermission}`);
          return false;
        }
      }
      
      return true;
    } catch (error: any) {
      console.error('❌ Permission check failed:', error);
      return false;
    }
  }

  /**
   * Get all permissions for a user
   */
  public async getUserPermissions(userId: string): Promise<string[]> {
    try {
      // Get permissions from user record
      const user = await this.dbManager.getUserById(userId);
      if (!user) {
        return [];
      }

      let permissions: string[] = [];
      try {
        permissions = JSON.parse(user.permissions);
      } catch {
        permissions = [];
      }

      // Get additional permissions from permissions table
      const additionalPermissions = await this.dbManager.all(
        `SELECT permission FROM permissions 
         WHERE user_id = ? AND is_active = 1 
         AND (expires_at IS NULL OR expires_at > datetime('now'))`,
        [userId]
      );

      const additionalPermissionNames = additionalPermissions.map((p: any) => p.permission);
      
      // Combine and deduplicate
      const allPermissions = [...new Set([...permissions, ...additionalPermissionNames])];
      
      return allPermissions;
    } catch (error: any) {
      console.error('❌ Failed to get user permissions:', error);
      return [];
    }
  }

  /**
   * Grant permission to user
   */
  public async grantPermission(
    userId: string,
    permission: string,
    resource?: string,
    grantedBy?: string,
    expiresAt?: string
  ): Promise<void> {
    try {
      const permissionId = `perm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      await this.dbManager.run(
        `INSERT INTO permissions (id, user_id, permission, resource, granted_by, granted_at, expires_at, is_active)
         VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, 1)`,
        [permissionId, userId, permission, resource, grantedBy, expiresAt]
      );

      console.log(`✅ Granted permission ${permission} to user ${userId}`);
    } catch (error: any) {
      console.error('❌ Failed to grant permission:', error);
      throw error;
    }
  }

  /**
   * Revoke permission from user
   */
  public async revokePermission(userId: string, permission: string, resource?: string): Promise<void> {
    try {
      let sql = 'UPDATE permissions SET is_active = 0 WHERE user_id = ? AND permission = ?';
      const params: any[] = [userId, permission];

      if (resource) {
        sql += ' AND resource = ?';
        params.push(resource);
      }

      await this.dbManager.run(sql, params);
      console.log(`❌ Revoked permission ${permission} from user ${userId}`);
    } catch (error: any) {
      console.error('❌ Failed to revoke permission:', error);
      throw error;
    }
  }

  /**
   * Update user permissions in user record
   */
  public async updateUserPermissions(userId: string, permissions: string[]): Promise<void> {
    try {
      await this.dbManager.run(
        'UPDATE users SET permissions = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        [JSON.stringify(permissions), userId]
      );

      console.log(`✅ Updated permissions for user ${userId}: ${permissions.join(', ')}`);
    } catch (error: any) {
      console.error('❌ Failed to update user permissions:', error);
      throw error;
    }
  }

  /**
   * Get default permissions for new users
   */
  public getDefaultPermissions(): string[] {
    return [
      PermissionManager.PERMISSIONS.CREATE_TASKS,
      PermissionManager.PERMISSIONS.READ_FILES
    ];
  }

  /**
   * Get admin permissions
   */
  public getAdminPermissions(): string[] {
    return Object.values(PermissionManager.PERMISSIONS);
  }

  /**
   * Check if user is admin
   */
  public async isUserAdmin(userId: string): Promise<boolean> {
    const permissions = await this.getUserPermissions(userId);
    return permissions.includes(PermissionManager.PERMISSIONS.SYSTEM_ADMIN);
  }

  /**
   * Validate permission scope for resource access
   */
  public async validateResourceAccess(userId: string, permission: string, resource: string): Promise<boolean> {
    try {
      // Check general permission
      const hasGeneralPermission = await this.checkUserPermissions(userId, [permission]);
      if (!hasGeneralPermission) {
        return false;
      }

      // Check resource-specific permission
      const resourcePermission = await this.dbManager.get(
        `SELECT * FROM permissions 
         WHERE user_id = ? AND permission = ? AND resource = ? AND is_active = 1
         AND (expires_at IS NULL OR expires_at > datetime('now'))`,
        [userId, permission, resource]
      );

      return !!resourcePermission;
    } catch (error: any) {
      console.error('❌ Resource access validation failed:', error);
      return false;
    }
  }

  /**
   * Get all users with specific permission
   */
  public async getUsersWithPermission(permission: string): Promise<string[]> {
    try {
      // Get from user permissions
      const users = await this.dbManager.all(
        'SELECT id FROM users WHERE permissions LIKE ? AND is_active = 1',
        [`%"${permission}"%`]
      );

      // Get from permissions table
      const permissionUsers = await this.dbManager.all(
        `SELECT DISTINCT user_id FROM permissions 
         WHERE permission = ? AND is_active = 1
         AND (expires_at IS NULL OR expires_at > datetime('now'))`,
        [permission]
      );

      const userIds = [
        ...users.map((u: any) => u.id),
        ...permissionUsers.map((u: any) => u.user_id)
      ];

      return [...new Set(userIds)];
    } catch (error: any) {
      console.error('❌ Failed to get users with permission:', error);
      return [];
    }
  }

  /**
   * Create default admin user with full permissions
   */
  public async createDefaultAdmin(): Promise<void> {
    try {
      // Check if admin already exists
      const existingAdmin = await this.dbManager.get(
        'SELECT id FROM users WHERE username = "admin"'
      );

      if (existingAdmin) {
        console.log('✅ Default admin user already exists');
        return;
      }

      // Create admin user with full permissions
      const adminId = await this.dbManager.createUser({
        username: 'admin',
        email: 'admin@jarvisx.local',
        password_hash: 'admin_hash_placeholder', // Should be hashed password
        permissions: JSON.stringify(this.getAdminPermissions()),
        is_active: true
      });

      console.log(`✅ Created default admin user: ${adminId}`);
    } catch (error: any) {
      console.error('❌ Failed to create default admin:', error);
    }
  }
}
