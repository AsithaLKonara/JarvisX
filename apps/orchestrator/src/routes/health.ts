/**
 * Health check routes for JarvisX Orchestrator
 */

import express from 'express';

const router = express.Router();

// GET /health - Basic health check
router.get('/', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'jarvisx-orchestrator',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    uptime: process.uptime()
  });
});

// GET /health/detailed - Detailed health check
router.get('/detailed', async (req, res) => {
  try {
    const dbManager = req.context.dbManager;
    const auditLogger = req.context.auditLogger;
    const permissionManager = req.context.permissionManager;
    const taskManager = req.context.taskManager;

    const health = {
      status: 'healthy',
      service: 'jarvisx-orchestrator',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      components: {
        database: {
          status: 'healthy',
          connected: true
        },
        audit_logger: {
          status: 'healthy',
          available: !!auditLogger
        },
        permission_manager: {
          status: 'healthy',
          available: !!permissionManager
        },
        task_manager: {
          status: 'healthy',
          available: !!taskManager
        }
      }
    };

    // Test database connection
    try {
      await dbManager.get('SELECT 1');
    } catch (error) {
      health.components.database = {
        status: 'unhealthy',
        connected: false,
        error: error.message
      };
      health.status = 'degraded';
    }

    res.json(health);

  } catch (error: any) {
    res.status(500).json({
      status: 'unhealthy',
      service: 'jarvisx-orchestrator',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// GET /health/ready - Readiness probe
router.get('/ready', async (req, res) => {
  try {
    const dbManager = req.context.dbManager;

    // Test database connection
    await dbManager.get('SELECT 1');

    res.json({
      status: 'ready',
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    res.status(503).json({
      status: 'not_ready',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// GET /health/live - Liveness probe
router.get('/live', (req, res) => {
  res.json({
    status: 'alive',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

export default router;
