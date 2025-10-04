/**
 * Admin routes for JarvisX Orchestrator
 */

import express from 'express';

const router = express.Router();

// GET /admin/stats - Get system statistics
router.get('/stats', async (req, res) => {
  try {
    const dbManager = req.context.dbManager;
    const auditLogger = req.context.auditLogger;

    // Get basic statistics
    const stats = {
      tasks: {
        total: 0,
        pending: 0,
        approved: 0,
        completed: 0,
        failed: 0
      },
      users: {
        total: 0,
        active: 0
      },
      audit_logs: {
        total: 0,
        last_24h: 0
      }
    };

    // Get task statistics
    const taskStats = await dbManager.all(`
      SELECT status, COUNT(*) as count 
      FROM tasks 
      GROUP BY status
    `);

    taskStats.forEach((stat: any) => {
      stats.tasks[stat.status as keyof typeof stats.tasks] = stat.count;
      stats.tasks.total += stat.count;
    });

    // Get user statistics
    const userStats = await dbManager.get(`
      SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active
      FROM users
    `);

    if (userStats) {
      stats.users.total = userStats.total;
      stats.users.active = userStats.active;
    }

    // Get audit log statistics
    const auditStats = await dbManager.get(`
      SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN timestamp > datetime('now', '-1 day') THEN 1 ELSE 0 END) as last_24h
      FROM audit_logs
    `);

    if (auditStats) {
      stats.audit_logs.total = auditStats.total;
      stats.audit_logs.last_24h = auditStats.last_24h;
    }

    res.json({
      success: true,
      stats,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('❌ Failed to get admin stats:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// GET /admin/audit-logs - Get audit logs
router.get('/audit-logs', async (req, res) => {
  try {
    const { limit = 100, offset = 0, task_id, user_id, action } = req.query;
    const dbManager = req.context.dbManager;

    let sql = 'SELECT * FROM audit_logs WHERE 1=1';
    const params: any[] = [];

    if (task_id) {
      sql += ' AND task_id = ?';
      params.push(task_id);
    }

    if (user_id) {
      sql += ' AND user_id = ?';
      params.push(user_id);
    }

    if (action) {
      sql += ' AND action = ?';
      params.push(action);
    }

    sql += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?';
    params.push(parseInt(limit as string), parseInt(offset as string));

    const logs = await dbManager.all(sql, params);

    // Get total count
    let countSql = 'SELECT COUNT(*) as total FROM audit_logs WHERE 1=1';
    const countParams: any[] = [];

    if (task_id) {
      countSql += ' AND task_id = ?';
      countParams.push(task_id);
    }

    if (user_id) {
      countSql += ' AND user_id = ?';
      countParams.push(user_id);
    }

    if (action) {
      countSql += ' AND action = ?';
      countParams.push(action);
    }

    const countResult = await dbManager.get(countSql, countParams);
    const total = countResult?.total || 0;

    res.json({
      success: true,
      logs,
      pagination: {
        total,
        limit: parseInt(limit as string),
        offset: parseInt(offset as string),
        has_more: (parseInt(offset as string) + parseInt(limit as string)) < total
      }
    });

  } catch (error: any) {
    console.error('❌ Failed to get audit logs:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// GET /admin/users - Get all users
router.get('/users', async (req, res) => {
  try {
    const { limit = 50, offset = 0, active_only } = req.query;
    const dbManager = req.context.dbManager;

    let sql = 'SELECT id, username, email, permissions, is_active, created_at, last_login FROM users';
    const params: any[] = [];

    if (active_only === 'true') {
      sql += ' WHERE is_active = 1';
    }

    sql += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
    params.push(parseInt(limit as string), parseInt(offset as string));

    const users = await dbManager.all(sql, params);

    // Parse permissions for each user
    users.forEach((user: any) => {
      try {
        user.permissions = JSON.parse(user.permissions);
      } catch {
        user.permissions = [];
      }
    });

    res.json({
      success: true,
      users,
      count: users.length
    });

  } catch (error: any) {
    console.error('❌ Failed to get users:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// POST /admin/users/:id/permissions - Update user permissions
router.post('/users/:id/permissions', async (req, res) => {
  try {
    const { id } = req.params;
    const { permissions } = req.body;

    if (!Array.isArray(permissions)) {
      return res.status(400).json({
        error: 'Permissions must be an array'
      });
    }

    const dbManager = req.context.dbManager;

    // Check if user exists
    const user = await dbManager.getUserById(id);
    if (!user) {
      return res.status(404).json({
        error: 'User not found'
      });
    }

    // Update permissions
    await dbManager.run(
      'UPDATE users SET permissions = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      [JSON.stringify(permissions), id]
    );

    // Log permission change
    await req.context.auditLogger.logEvent({
      user_id: id,
      action: 'permissions_updated',
      details: { permissions }
    });

    res.json({
      success: true,
      message: 'Permissions updated successfully'
    });

  } catch (error: any) {
    console.error('❌ Failed to update permissions:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// POST /admin/users/:id/toggle - Toggle user active status
router.post('/users/:id/toggle', async (req, res) => {
  try {
    const { id } = req.params;
    const dbManager = req.context.dbManager;

    // Get current user status
    const user = await dbManager.getUserById(id);
    if (!user) {
      return res.status(404).json({
        error: 'User not found'
      });
    }

    const newStatus = !user.is_active;

    // Update status
    await dbManager.run(
      'UPDATE users SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      [newStatus, id]
    );

    // Log status change
    await req.context.auditLogger.logEvent({
      user_id: id,
      action: 'user_status_changed',
      details: { new_status: newStatus }
    });

    res.json({
      success: true,
      message: `User ${newStatus ? 'activated' : 'deactivated'} successfully`,
      is_active: newStatus
    });

  } catch (error: any) {
    console.error('❌ Failed to toggle user status:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

// GET /admin/system-info - Get system information
router.get('/system-info', (req, res) => {
  try {
    const systemInfo = {
      node_version: process.version,
      platform: process.platform,
      architecture: process.arch,
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      cpu_usage: process.cpuUsage(),
      environment: process.env.NODE_ENV || 'development',
      version: process.env.npm_package_version || '1.0.0'
    };

    res.json({
      success: true,
      system: systemInfo,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('❌ Failed to get system info:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

export default router;
