/**
 * JarvisX Orchestrator Service
 * Core coordination service that manages tasks, permissions, and execution
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import dotenv from 'dotenv';
import path from 'path';

// Import modules
import { DatabaseManager } from './database/DatabaseManager';
import { PermissionManager } from './security/PermissionManager';
import { AuditLogger } from './audit/AuditLogger';
import { TaskManager } from './tasks/TaskManager';
import { LLMService } from './ai/LLMService';
import { ExecutorRegistry } from './executors/ExecutorRegistry';
import { WebSocketManager } from './websocket/WebSocketManager';
import { AuthService } from './auth/AuthService';

// Import routes
import taskRoutes from './routes/tasks';
import authRoutes from './routes/auth';
import adminRoutes from './routes/admin';
import healthRoutes from './routes/health';

dotenv.config();

class OrchestratorService {
  private app: express.Application;
  private server: any;
  private wss: WebSocketServer;
  private dbManager: DatabaseManager;
  private permissionManager: PermissionManager;
  private auditLogger: AuditLogger;
  private taskManager: TaskManager;
  private llmService: LLMService;
  private executorRegistry: ExecutorRegistry;
  private wsManager: WebSocketManager;
  private authService: AuthService;

  constructor() {
    this.app = express();
    this.server = createServer(this.app);
    this.wss = new WebSocketServer({ server: this.server });
    
    this.initializeServices();
    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
  }

  private async initializeServices(): Promise<void> {
    console.log('Initializing JarvisX Orchestrator services...');

    try {
      // Initialize database
      this.dbManager = new DatabaseManager();
      await this.dbManager.initialize();

      // Initialize core services
      this.auditLogger = new AuditLogger(this.dbManager);
      this.permissionManager = new PermissionManager(this.dbManager);
      this.llmService = new LLMService();
      this.executorRegistry = new ExecutorRegistry();
      this.authService = new AuthService(this.dbManager);

      // Initialize task manager with dependencies
      this.taskManager = new TaskManager(
        this.dbManager,
        this.auditLogger,
        this.permissionManager,
        this.llmService,
        this.executorRegistry
      );

      // Initialize WebSocket manager
      this.wsManager = new WebSocketManager(this.wss, this.taskManager);

      console.log('✅ All services initialized successfully');

    } catch (error) {
      console.error('❌ Failed to initialize services:', error);
      process.exit(1);
    }
  }

  private setupMiddleware(): void {
    // Security middleware
    this.app.use(helmet());
    this.app.use(cors({
      origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
      credentials: true
    }));

    // Logging
    this.app.use(morgan('combined'));

    // Body parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Request context middleware
    this.app.use((req, res, next) => {
      req.context = {
        dbManager: this.dbManager,
        auditLogger: this.auditLogger,
        permissionManager: this.permissionManager,
        taskManager: this.taskManager,
        authService: this.authService
      };
      next();
    });
  }

  private setupRoutes(): void {
    // Health and status routes
    this.app.use('/health', healthRoutes);

    // Authentication routes
    this.app.use('/auth', authRoutes);

    // Task management routes
    this.app.use('/tasks', taskRoutes);

    // Admin routes (protected)
    this.app.use('/admin', adminRoutes);

    // WebSocket endpoint info
    this.app.get('/ws', (req, res) => {
      res.json({
        websocket_url: `ws://${req.get('host')}/ws`,
        status: 'available'
      });
    });

    // 404 handler
    this.app.use('*', (req, res) => {
      res.status(404).json({
        error: 'Not found',
        path: req.originalUrl,
        method: req.method
      });
    });

    // Global error handler
    this.app.use((error: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
      console.error('Unhandled error:', error);
      
      this.auditLogger?.logError({
        error: error.message,
        stack: error.stack,
        url: req.url,
        method: req.method,
        user_id: req.user?.id
      });

      res.status(500).json({
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
      });
    });
  }

  private setupWebSocket(): void {
    this.wss.on('connection', (ws, req) => {
      this.wsManager.handleConnection(ws, req);
    });

    console.log('WebSocket server configured');
  }

  public async start(): Promise<void> {
    const PORT = process.env.PORT || 3000;
    
    try {
      this.server.listen(PORT, '0.0.0.0', () => {
        console.log(`🚀 JarvisX Orchestrator running on port ${PORT}`);
        console.log(`📊 WebSocket server available at ws://localhost:${PORT}/ws`);
        console.log(`🔐 Authentication: ${this.authService.isConfigured() ? 'Enabled' : 'Disabled'}`);
        console.log(`🤖 LLM Service: ${this.llmService.isConfigured() ? 'Configured' : 'Not configured'}`);
        console.log(`📝 Audit logging: Active`);
        console.log(`🛡️  Permission system: Active`);
      });
    } catch (error) {
      console.error('Failed to start server:', error);
      process.exit(1);
    }
  }

  public async shutdown(): Promise<void> {
    console.log('Shutting down JarvisX Orchestrator...');
    
    try {
      // Close WebSocket connections
      this.wss.close();
      
      // Close HTTP server
      this.server.close();
      
      // Close database connections
      await this.dbManager?.close();
      
      console.log('✅ Orchestrator shut down successfully');
    } catch (error) {
      console.error('❌ Error during shutdown:', error);
    }
  }
}

// Start the service
const orchestrator = new OrchestratorService();

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\nReceived SIGINT, shutting down gracefully...');
  await orchestrator.shutdown();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\nReceived SIGTERM, shutting down gracefully...');
  await orchestrator.shutdown();
  process.exit(0);
});

// Start the service
orchestrator.start().catch((error) => {
  console.error('Failed to start orchestrator:', error);
  process.exit(1);
});

export default orchestrator;
