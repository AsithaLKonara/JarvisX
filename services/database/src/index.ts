/**
 * JarvisX Database Service
 * PostgreSQL + Redis microservice for data persistence and caching
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { connectDatabase, connectRedis, checkDatabaseHealth } from './config/database';
import CacheService from './services/CacheService';
import User from './models/User';
import Command from './models/Command';
import ApprovalRequest from './models/ApprovalRequest';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8017;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Initialize services
const cacheService = CacheService.getInstance();

// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    const health = await checkDatabaseHealth();
    const cacheStats = await cacheService.getStats();
    
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      database: health,
      cache: cacheStats,
      services: {
        postgres: health.postgres,
        redis: health.redis,
        cache: cacheService.isReady()
      }
    });
  } catch (error) {
    res.status(500).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// User endpoints
app.get('/users', async (req, res) => {
  try {
    const { page = 1, limit = 10, role, isActive } = req.query;
    const offset = (Number(page) - 1) * Number(limit);
    
    const where: any = {};
    if (role) where.role = role;
    if (isActive !== undefined) where.isActive = isActive === 'true';
    
    const users = await User.findAndCountAll({
      where,
      limit: Number(limit),
      offset,
      order: [['createdAt', 'DESC']]
    });
    
    res.json({
      users: users.rows,
      pagination: {
        page: Number(page),
        limit: Number(limit),
        total: users.count,
        pages: Math.ceil(users.count / Number(limit))
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/users/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Try cache first
    let user = await cacheService.getCachedUser(id);
    if (!user) {
      user = await User.findByPk(id);
      if (user) {
        await cacheService.cacheUser(id, user.toJSON());
      }
    }
    
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    res.json(user);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/users', async (req, res) => {
  try {
    const userData = req.body;
    const user = await User.create(userData);
    
    // Cache the new user
    await cacheService.cacheUser(user.id, user.toJSON());
    
    res.status(201).json(user.toJSON());
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.put('/users/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;
    
    const user = await User.findByPk(id);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    await user.update(updateData);
    
    // Update cache
    await cacheService.cacheUser(id, user.toJSON());
    
    res.json(user.toJSON());
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.delete('/users/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const user = await User.findByPk(id);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    await user.destroy();
    
    // Invalidate cache
    await cacheService.invalidateUserCache(id);
    
    res.json({ message: 'User deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Command endpoints
app.get('/commands', async (req, res) => {
  try {
    const { 
      page = 1, 
      limit = 10, 
      userId, 
      type, 
      status, 
      startDate, 
      endDate 
    } = req.query;
    
    const offset = (Number(page) - 1) * Number(limit);
    
    const where: any = {};
    if (userId) where.userId = userId;
    if (type) where.type = type;
    if (status) where.status = status;
    
    if (startDate || endDate) {
      where.createdAt = {};
      if (startDate) where.createdAt[Op.gte] = new Date(startDate as string);
      if (endDate) where.createdAt[Op.lte] = new Date(endDate as string);
    }
    
    const commands = await Command.findAndCountAll({
      where,
      limit: Number(limit),
      offset,
      order: [['createdAt', 'DESC']],
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'username', 'email']
        }
      ]
    });
    
    res.json({
      commands: commands.rows,
      pagination: {
        page: Number(page),
        limit: Number(limit),
        total: commands.count,
        pages: Math.ceil(commands.count / Number(limit))
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/commands/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Try cache first
    let command = await cacheService.getCachedCommand(id);
    if (!command) {
      command = await Command.findByPk(id, {
        include: [
          {
            model: User,
            as: 'user',
            attributes: ['id', 'username', 'email']
          }
        ]
      });
      if (command) {
        await cacheService.cacheCommand(id, command.toSafeJSON());
      }
    }
    
    if (!command) {
      return res.status(404).json({ error: 'Command not found' });
    }
    
    res.json(command);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/commands', async (req, res) => {
  try {
    const commandData = req.body;
    const command = await Command.create(commandData);
    
    // Cache the new command
    await cacheService.cacheCommand(command.id, command.toSafeJSON());
    
    res.status(201).json(command.toSafeJSON());
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Approval request endpoints
app.get('/approvals', async (req, res) => {
  try {
    const { 
      page = 1, 
      limit = 10, 
      userId, 
      status, 
      riskCategory, 
      priority 
    } = req.query;
    
    const offset = (Number(page) - 1) * Number(limit);
    
    const where: any = {};
    if (userId) where.userId = userId;
    if (status) where.status = status;
    if (riskCategory) where.riskCategory = riskCategory;
    if (priority) where.priority = priority;
    
    const approvals = await ApprovalRequest.findAndCountAll({
      where,
      limit: Number(limit),
      offset,
      order: [['createdAt', 'DESC']],
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'username', 'email']
        }
      ]
    });
    
    res.json({
      approvals: approvals.rows,
      pagination: {
        page: Number(page),
        limit: Number(limit),
        total: approvals.count,
        pages: Math.ceil(approvals.count / Number(limit))
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/approvals/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Try cache first
    let approval = await cacheService.getCachedApprovalRequest(id);
    if (!approval) {
      approval = await ApprovalRequest.findByPk(id, {
        include: [
          {
            model: User,
            as: 'user',
            attributes: ['id', 'username', 'email']
          }
        ]
      });
      if (approval) {
        await cacheService.cacheApprovalRequest(id, approval.toSafeJSON());
      }
    }
    
    if (!approval) {
      return res.status(404).json({ error: 'Approval request not found' });
    }
    
    res.json(approval);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/approvals', async (req, res) => {
  try {
    const approvalData = req.body;
    const approval = await ApprovalRequest.create(approvalData);
    
    // Cache the new approval request
    await cacheService.cacheApprovalRequest(approval.id, approval.toSafeJSON());
    
    res.status(201).json(approval.toSafeJSON());
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.put('/approvals/:id/approve', async (req, res) => {
  try {
    const { id } = req.params;
    const { approvedBy, reason } = req.body;
    
    const approval = await ApprovalRequest.findByPk(id);
    if (!approval) {
      return res.status(404).json({ error: 'Approval request not found' });
    }
    
    if (approval.isApproved() || approval.isRejected()) {
      return res.status(400).json({ error: 'Approval request already processed' });
    }
    
    approval.approve(approvedBy, reason);
    await approval.save();
    
    // Update cache
    await cacheService.cacheApprovalRequest(id, approval.toSafeJSON());
    
    res.json(approval.toSafeJSON());
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.put('/approvals/:id/reject', async (req, res) => {
  try {
    const { id } = req.params;
    const { rejectedBy, reason } = req.body;
    
    const approval = await ApprovalRequest.findByPk(id);
    if (!approval) {
      return res.status(404).json({ error: 'Approval request not found' });
    }
    
    if (approval.isApproved() || approval.isRejected()) {
      return res.status(400).json({ error: 'Approval request already processed' });
    }
    
    approval.reject(rejectedBy, reason);
    await approval.save();
    
    // Update cache
    await cacheService.cacheApprovalRequest(id, approval.toSafeJSON());
    
    res.json(approval.toSafeJSON());
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Cache management endpoints
app.get('/cache/stats', async (req, res) => {
  try {
    const stats = await cacheService.getStats();
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/cache/invalidate', async (req, res) => {
  try {
    const { pattern, tag } = req.body;
    
    if (pattern) {
      await cacheService.invalidateByPattern(pattern);
    } else if (tag) {
      await cacheService.invalidateByTag(tag);
    } else {
      await cacheService.invalidateAllCaches();
    }
    
    res.json({ message: 'Cache invalidated successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.delete('/cache', async (req, res) => {
  try {
    await cacheService.flush();
    res.json({ message: 'Cache flushed successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// System stats endpoint
app.get('/stats', async (req, res) => {
  try {
    const userCount = await User.count();
    const commandCount = await Command.count();
    const approvalCount = await ApprovalRequest.count();
    const pendingApprovals = await ApprovalRequest.count({ where: { status: 'pending' } });
    
    const cacheStats = await cacheService.getStats();
    
    res.json({
      users: userCount,
      commands: commandCount,
      approvals: approvalCount,
      pendingApprovals,
      cache: cacheStats,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Error handling middleware
app.use((error: any, req: any, res: any, next: any) => {
  console.error('❌ Database service error:', error);
  res.status(500).json({
    error: 'Internal server error',
    message: error.message,
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    path: req.originalUrl,
    timestamp: new Date().toISOString()
  });
});

// Start server
const startServer = async () => {
  try {
    // Connect to databases
    await connectDatabase();
    await connectRedis();
    
    // Sync database models
    await User.sync({ alter: true });
    await Command.sync({ alter: true });
    await ApprovalRequest.sync({ alter: true });
    
    // Start server
    app.listen(PORT, () => {
      console.log(`🚀 Database service running on port ${PORT}`);
      console.log(`📊 Health check: http://localhost:${PORT}/health`);
      console.log(`📈 Stats: http://localhost:${PORT}/stats`);
    });
  } catch (error) {
    console.error('❌ Failed to start database service:', error);
    process.exit(1);
  }
};

startServer();

export default app;
