/**
 * Authentication Service for JarvisX Orchestrator
 * Handles user authentication, registration, and password management
 */

import bcrypt from 'bcryptjs';
import { DatabaseManager } from '../database/DatabaseManager';
import { PermissionManager } from '../security/PermissionManager';

export interface AuthResult {
  success: boolean;
  user?: any;
  error?: string;
}

export interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
  permissions?: string[];
}

export class AuthService {
  private dbManager: DatabaseManager;
  private permissionManager: PermissionManager;
  private saltRounds: number;

  constructor(dbManager: DatabaseManager) {
    this.dbManager = dbManager;
    this.permissionManager = new PermissionManager(dbManager);
    this.saltRounds = parseInt(process.env.BCRYPT_SALT_ROUNDS || '12');
  }

  /**
   * Authenticate user with username and password
   */
  public async authenticate(username: string, password: string): Promise<AuthResult> {
    try {
      const user = await this.dbManager.getUserByUsername(username);
      
      if (!user) {
        return {
          success: false,
          error: 'User not found'
        };
      }

      if (!user.is_active) {
        return {
          success: false,
          error: 'User account is disabled'
        };
      }

      const isValidPassword = await bcrypt.compare(password, user.password_hash);
      
      if (!isValidPassword) {
        return {
          success: false,
          error: 'Invalid password'
        };
      }

      // Update last login
      await this.dbManager.run(
        'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
        [user.id]
      );

      return {
        success: true,
        user
      };

    } catch (error: any) {
      console.error('❌ Authentication failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Create a new user
   */
  public async createUser(userData: CreateUserRequest): Promise<AuthResult> {
    try {
      // Validate input
      if (!userData.username || !userData.email || !userData.password) {
        return {
          success: false,
          error: 'Username, email, and password are required'
        };
      }

      // Check if username already exists
      const existingUser = await this.dbManager.getUserByUsername(userData.username);
      if (existingUser) {
        return {
          success: false,
          error: 'Username already exists'
        };
      }

      // Check if email already exists
      const existingEmail = await this.dbManager.get(
        'SELECT id FROM users WHERE email = ?',
        [userData.email]
      );
      if (existingEmail) {
        return {
          success: false,
          error: 'Email already exists'
        };
      }

      // Hash password
      const passwordHash = await bcrypt.hash(userData.password, this.saltRounds);

      // Set default permissions if not provided
      const permissions = userData.permissions || this.permissionManager.getDefaultPermissions();

      // Create user
      const userId = await this.dbManager.createUser({
        username: userData.username,
        email: userData.email,
        password_hash: passwordHash,
        permissions: JSON.stringify(permissions),
        is_active: true
      });

      // Get created user
      const user = await this.dbManager.getUserById(userId);

      return {
        success: true,
        user
      };

    } catch (error: any) {
      console.error('❌ User creation failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Update user password
   */
  public async updatePassword(userId: string, newPassword: string): Promise<AuthResult> {
    try {
      if (!newPassword || newPassword.length < 8) {
        return {
          success: false,
          error: 'Password must be at least 8 characters long'
        };
      }

      // Hash new password
      const passwordHash = await bcrypt.hash(newPassword, this.saltRounds);

      // Update password
      await this.dbManager.run(
        'UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        [passwordHash, userId]
      );

      return {
        success: true
      };

    } catch (error: any) {
      console.error('❌ Password update failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get user by username
   */
  public async getUserByUsername(username: string): Promise<any> {
    return await this.dbManager.getUserByUsername(username);
  }

  /**
   * Get user by ID
   */
  public async getUserById(userId: string): Promise<any> {
    return await this.dbManager.getUserById(userId);
  }

  /**
   * Update user profile
   */
  public async updateUserProfile(userId: string, updates: {
    username?: string;
    email?: string;
  }): Promise<AuthResult> {
    try {
      const user = await this.dbManager.getUserById(userId);
      if (!user) {
        return {
          success: false,
          error: 'User not found'
        };
      }

      // Check if new username is taken
      if (updates.username && updates.username !== user.username) {
        const existingUser = await this.dbManager.getUserByUsername(updates.username);
        if (existingUser) {
          return {
            success: false,
            error: 'Username already exists'
          };
        }
      }

      // Check if new email is taken
      if (updates.email && updates.email !== user.email) {
        const existingEmail = await this.dbManager.get(
          'SELECT id FROM users WHERE email = ? AND id != ?',
          [updates.email, userId]
        );
        if (existingEmail) {
          return {
            success: false,
            error: 'Email already exists'
          };
        }
      }

      // Build update query
      const updateFields: string[] = [];
      const params: any[] = [];

      if (updates.username) {
        updateFields.push('username = ?');
        params.push(updates.username);
      }

      if (updates.email) {
        updateFields.push('email = ?');
        params.push(updates.email);
      }

      if (updateFields.length === 0) {
        return {
          success: false,
          error: 'No fields to update'
        };
      }

      updateFields.push('updated_at = CURRENT_TIMESTAMP');
      params.push(userId);

      const sql = `UPDATE users SET ${updateFields.join(', ')} WHERE id = ?`;
      await this.dbManager.run(sql, params);

      // Get updated user
      const updatedUser = await this.dbManager.getUserById(userId);

      return {
        success: true,
        user: updatedUser
      };

    } catch (error: any) {
      console.error('❌ Profile update failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Deactivate user account
   */
  public async deactivateUser(userId: string): Promise<AuthResult> {
    try {
      const user = await this.dbManager.getUserById(userId);
      if (!user) {
        return {
          success: false,
          error: 'User not found'
        };
      }

      await this.dbManager.run(
        'UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        [userId]
      );

      return {
        success: true
      };

    } catch (error: any) {
      console.error('❌ User deactivation failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Activate user account
   */
  public async activateUser(userId: string): Promise<AuthResult> {
    try {
      const user = await this.dbManager.getUserById(userId);
      if (!user) {
        return {
          success: false,
          error: 'User not found'
        };
      }

      await this.dbManager.run(
        'UPDATE users SET is_active = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        [userId]
      );

      return {
        success: true
      };

    } catch (error: any) {
      console.error('❌ User activation failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get all users
   */
  public async getAllUsers(): Promise<any[]> {
    try {
      return await this.dbManager.all(
        'SELECT id, username, email, is_active, created_at, last_login FROM users ORDER BY created_at DESC'
      );
    } catch (error: any) {
      console.error('❌ Failed to get users:', error);
      return [];
    }
  }

  /**
   * Check if authentication service is configured
   */
  public isConfigured(): boolean {
    // Check if JWT secret is configured
    return !!(process.env.JWT_SECRET && process.env.JWT_SECRET !== 'default-secret');
  }

  /**
   * Initialize default admin user
   */
  public async initializeDefaultAdmin(): Promise<void> {
    try {
      // Check if admin user exists
      const adminUser = await this.getUserByUsername('admin');
      
      if (adminUser) {
        console.log('✅ Default admin user already exists');
        return;
      }

      // Create default admin user
      const result = await this.createUser({
        username: 'admin',
        email: 'admin@jarvisx.local',
        password: process.env.DEFAULT_ADMIN_PASSWORD || 'admin123',
        permissions: this.permissionManager.getAdminPermissions()
      });

      if (result.success) {
        console.log('✅ Created default admin user');
      } else {
        console.error('❌ Failed to create default admin user:', result.error);
      }

    } catch (error: any) {
      console.error('❌ Failed to initialize default admin:', error);
    }
  }
}
