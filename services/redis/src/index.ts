/**
 * JarvisX Redis Service
 * High-performance caching and session management microservice
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import RedisService from './RedisService';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8018;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Initialize Redis service
const redisService = RedisService.getInstance();

// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    const stats = await redisService.getStats();
    
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      redis: {
        connected: redisService.isReady(),
        stats
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

// Cache operations
app.post('/cache/set', async (req, res) => {
  try {
    const { key, value, ttl, tags, nx, xx } = req.body;
    
    if (!key || value === undefined) {
      return res.status(400).json({ error: 'Key and value are required' });
    }

    const options = { ttl, tags, nx, xx };
    const success = await redisService.set(key, value, options);
    
    res.json({ success, key });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/cache/get/:key', async (req, res) => {
  try {
    const { key } = req.params;
    const value = await redisService.get(key);
    
    if (value === null) {
      return res.status(404).json({ error: 'Key not found' });
    }
    
    res.json({ key, value });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.delete('/cache/:key', async (req, res) => {
  try {
    const { key } = req.params;
    const success = await redisService.del(key);
    
    res.json({ success, key });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/cache/exists/:key', async (req, res) => {
  try {
    const { key } = req.params;
    const exists = await redisService.exists(key);
    
    res.json({ key, exists });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.put('/cache/expire/:key', async (req, res) => {
  try {
    const { key } = req.params;
    const { ttl } = req.body;
    
    if (!ttl || ttl <= 0) {
      return res.status(400).json({ error: 'Valid TTL is required' });
    }

    const success = await redisService.expire(key, ttl);
    res.json({ success, key, ttl });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/cache/ttl/:key', async (req, res) => {
  try {
    const { key } = req.params;
    const ttl = await redisService.ttl(key);
    
    res.json({ key, ttl });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Session management
app.post('/sessions', async (req, res) => {
  try {
    const sessionData = req.body;
    const sessionId = await redisService.createSession(sessionData);
    
    res.status(201).json({ sessionId, sessionData });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.get('/sessions/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;
    const session = await redisService.getSession(sessionId);
    
    if (!session) {
      return res.status(404).json({ error: 'Session not found' });
    }
    
    res.json(session);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.put('/sessions/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;
    const updates = req.body;
    
    const success = await redisService.updateSession(sessionId, updates);
    
    if (!success) {
      return res.status(404).json({ error: 'Session not found' });
    }
    
    res.json({ success, sessionId });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.delete('/sessions/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;
    const success = await redisService.deleteSession(sessionId);
    
    if (!success) {
      return res.status(404).json({ error: 'Session not found' });
    }
    
    res.json({ success, sessionId });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/sessions/user/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const sessionIds = await redisService.getUserSessions(userId);
    
    res.json({ userId, sessionIds });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.delete('/sessions/user/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const success = await redisService.deleteUserSessions(userId);
    
    res.json({ success, userId });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Pub/Sub messaging
app.post('/publish', async (req, res) => {
  try {
    const { channel, message } = req.body;
    
    if (!channel || message === undefined) {
      return res.status(400).json({ error: 'Channel and message are required' });
    }

    const success = await redisService.publish(channel, message);
    res.json({ success, channel });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Cache invalidation
app.post('/cache/invalidate', async (req, res) => {
  try {
    const { pattern, tag } = req.body;
    
    let success = false;
    
    if (pattern) {
      success = await redisService.invalidateByPattern(pattern);
    } else if (tag) {
      success = await redisService.invalidateByTag(tag);
    } else {
      success = await redisService.invalidateByPattern('*');
    }
    
    res.json({ success, pattern, tag });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.delete('/cache', async (req, res) => {
  try {
    const success = await redisService.flush();
    res.json({ success });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Statistics
app.get('/stats', async (req, res) => {
  try {
    const stats = await redisService.getStats();
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Error handling middleware
app.use((error: any, req: any, res: any, next: any) => {
  console.error('❌ Redis service error:', error);
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
    // Wait for Redis to be ready
    let attempts = 0;
    const maxAttempts = 10;
    
    while (!redisService.isReady() && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      attempts++;
    }
    
    if (!redisService.isReady()) {
      throw new Error('Redis connection failed after maximum attempts');
    }
    
    // Start server
    app.listen(PORT, () => {
      console.log(`🚀 Redis service running on port ${PORT}`);
      console.log(`📊 Health check: http://localhost:${PORT}/health`);
      console.log(`📈 Stats: http://localhost:${PORT}/stats`);
    });
  } catch (error) {
    console.error('❌ Failed to start Redis service:', error);
    process.exit(1);
  }
};

startServer();

export default app;
