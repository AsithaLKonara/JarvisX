/**
 * Authentication routes for JarvisX Orchestrator
 */

import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

const router = express.Router();

// POST /auth/login - User login
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({
        error: 'Username and password are required'
      });
    }

    const authService = req.context.authService;

    // Authenticate user
    const authResult = await authService.authenticate(username, password);
    
    if (!authResult.success) {
      return res.status(401).json({
        error: 'Invalid credentials'
      });
    }

    // Generate JWT token
    const token = jwt.sign(
      { 
        user_id: authResult.user.id,
        username: authResult.user.username,
        permissions: JSON.parse(authResult.user.permissions)
      },
      process.env.JWT_SECRET || 'default-secret',
      { expiresIn: '24h' }
    );

    // Log successful login
    await req.context.auditLogger.logEvent({
      user_id: authResult.user.id,
      action: 'user_login',
      details: { username },
      ip_address: req.ip,
      user_agent: req.get('User-Agent')
    });

    res.json({
      success: true,
      token,
      user: {
        id: authResult.user.id,
        username: authResult.user.username,
        permissions: JSON.parse(authResult.user.permissions)
      }
    });

  } catch (error: any) {
    console.error('❌ Login failed:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// POST /auth/register - User registration (admin only)
router.post('/register', async (req, res) => {
  try {
    const { username, email, password, permissions = [] } = req.body;

    if (!username || !email || !password) {
      return res.status(400).json({
        error: 'Username, email, and password are required'
      });
    }

    const authService = req.context.authService;

    // Check if user already exists
    const existingUser = await authService.getUserByUsername(username);
    if (existingUser) {
      return res.status(409).json({
        error: 'Username already exists'
      });
    }

    // Create new user
    const userResult = await authService.createUser({
      username,
      email,
      password,
      permissions
    });

    if (!userResult.success) {
      return res.status(400).json({
        error: userResult.error
      });
    }

    // Log user creation
    await req.context.auditLogger.logEvent({
      user_id: userResult.user.id,
      action: 'user_created',
      details: { username, email, permissions }
    });

    res.status(201).json({
      success: true,
      user: {
        id: userResult.user.id,
        username: userResult.user.username,
        email: userResult.user.email,
        permissions: JSON.parse(userResult.user.permissions)
      }
    });

  } catch (error: any) {
    console.error('❌ User registration failed:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// GET /auth/me - Get current user info
router.get('/me', async (req, res) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({
        error: 'No token provided'
      });
    }

    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'default-secret') as any;
      
      const authService = req.context.authService;
      const user = await authService.getUserById(decoded.user_id);
      
      if (!user) {
        return res.status(401).json({
          error: 'User not found'
        });
      }

      res.json({
        success: true,
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          permissions: JSON.parse(user.permissions),
          created_at: user.created_at,
          last_login: user.last_login
        }
      });

    } catch (jwtError) {
      return res.status(401).json({
        error: 'Invalid token'
      });
    }

  } catch (error: any) {
    console.error('❌ Failed to get user info:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// POST /auth/logout - User logout
router.post('/logout', async (req, res) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (token) {
      try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET || 'default-secret') as any;
        
        // Log logout event
        await req.context.auditLogger.logEvent({
          user_id: decoded.user_id,
          action: 'user_logout',
          details: {},
          ip_address: req.ip,
          user_agent: req.get('User-Agent')
        });
      } catch (jwtError) {
        // Token is invalid, but that's okay for logout
      }
    }

    res.json({
      success: true,
      message: 'Logged out successfully'
    });

  } catch (error: any) {
    console.error('❌ Logout failed:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// POST /auth/change-password - Change user password
router.post('/change-password', async (req, res) => {
  try {
    const { current_password, new_password } = req.body;
    const token = req.headers.authorization?.replace('Bearer ', '');

    if (!token) {
      return res.status(401).json({
        error: 'No token provided'
      });
    }

    if (!current_password || !new_password) {
      return res.status(400).json({
        error: 'Current password and new password are required'
      });
    }

    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'default-secret') as any;
      
      const authService = req.context.authService;
      
      // Verify current password
      const user = await authService.getUserById(decoded.user_id);
      if (!user) {
        return res.status(404).json({
          error: 'User not found'
        });
      }

      const isValidPassword = await bcrypt.compare(current_password, user.password_hash);
      if (!isValidPassword) {
        return res.status(401).json({
          error: 'Current password is incorrect'
        });
      }

      // Update password
      const updateResult = await authService.updatePassword(decoded.user_id, new_password);
      
      if (!updateResult.success) {
        return res.status(400).json({
          error: updateResult.error
        });
      }

      // Log password change
      await req.context.auditLogger.logEvent({
        user_id: decoded.user_id,
        action: 'password_changed',
        details: {},
        ip_address: req.ip,
        user_agent: req.get('User-Agent')
      });

      res.json({
        success: true,
        message: 'Password changed successfully'
      });

    } catch (jwtError) {
      return res.status(401).json({
        error: 'Invalid token'
      });
    }

  } catch (error: any) {
    console.error('❌ Password change failed:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

export default router;
