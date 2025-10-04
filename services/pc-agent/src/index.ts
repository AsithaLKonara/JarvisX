/**
 * JarvisX PC Agent
 * Handles WebRTC screen publishing, action events, and local system control
 */

import express from 'express';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import dotenv from 'dotenv';
import { v4 as uuidv4 } from 'uuid';

// Import modules
import { ScreenCaptureService } from './services/ScreenCaptureService';
import { ActionEventService } from './services/ActionEventService';
import { WebRTCService } from './services/WebRTCService';
import { OrchestratorClient } from './clients/OrchestratorClient';
import { SystemController } from './controllers/SystemController';

dotenv.config();

class JarvisXPCAgent {
  private app: express.Application;
  private server: any;
  private wss: WebSocketServer;
  private screenCaptureService: ScreenCaptureService;
  private actionEventService: ActionEventService;
  private webRTCService: WebRTCService;
  private orchestratorClient: OrchestratorClient;
  private systemController: SystemController;
  private activeSessions: Map<string, any> = new Map();

  constructor() {
    this.app = express();
    this.server = createServer(this.app);
    this.wss = new WebSocketServer({ server: this.server });
    
    this.initializeServices();
    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
    this.setupSystemHooks();
  }

  private async initializeServices(): Promise<void> {
    console.log('🚀 Initializing JarvisX PC Agent...');

    try {
      // Initialize core services
      this.screenCaptureService = new ScreenCaptureService();
      this.actionEventService = new ActionEventService();
      this.webRTCService = new WebRTCService();
      this.orchestratorClient = new OrchestratorClient();
      this.systemController = new SystemController();

      // Initialize WebRTC service
      await this.webRTCService.initialize();

      console.log('✅ PC Agent services initialized successfully');

    } catch (error) {
      console.error('❌ Failed to initialize PC Agent services:', error);
      process.exit(1);
    }
  }

  private setupMiddleware(): void {
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));

    // CORS middleware
    this.app.use((req, res, next) => {
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
      if (req.method === 'OPTIONS') {
        res.sendStatus(200);
      } else {
        next();
      }
    });
  }

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        service: 'jarvisx-pc-agent',
        timestamp: new Date().toISOString(),
        activeSessions: this.activeSessions.size,
        capabilities: {
          screenCapture: this.screenCaptureService.isAvailable(),
          webRTC: this.webRTCService.isInitialized(),
          systemControl: true
        }
      });
    });

    // Start session endpoint
    this.app.post('/session/:id/start', async (req, res) => {
      try {
        const sessionId = req.params.id;
        const { screenShare, audioShare, options } = req.body;

        console.log(`🎬 Starting session ${sessionId}`);

        // Create session
        const session = {
          id: sessionId,
          screenShare: screenShare || false,
          audioShare: audioShare || false,
          options: options || {},
          startTime: new Date(),
          status: 'starting'
        };

        this.activeSessions.set(sessionId, session);

        // Start screen capture if requested
        if (screenShare) {
          await this.screenCaptureService.startCapture(sessionId);
        }

        // Initialize WebRTC connection
        const peerConnection = await this.webRTCService.createPeerConnection(sessionId);
        
        // Set up action event streaming
        this.actionEventService.onActionEvent((event) => {
          this.webRTCService.sendActionEvent(sessionId, event);
        });

        session.status = 'active';
        this.activeSessions.set(sessionId, session);

        // Notify orchestrator
        await this.orchestratorClient.notifySessionStart(sessionId, {
          capabilities: {
            screenShare: screenShare,
            audioShare: audioShare,
            systemControl: true
          }
        });

        res.json({
          success: true,
          sessionId,
          status: 'active',
          webRTC: {
            localDescription: await peerConnection.createOffer(),
            iceCandidates: []
          }
        });

      } catch (error: any) {
        console.error('❌ Failed to start session:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // End session endpoint
    this.app.post('/session/:id/end', async (req, res) => {
      try {
        const sessionId = req.params.id;
        
        console.log(`🛑 Ending session ${sessionId}`);

        const session = this.activeSessions.get(sessionId);
        if (session) {
          session.status = 'ending';
          
          // Stop screen capture
          await this.screenCaptureService.stopCapture(sessionId);
          
          // Close WebRTC connection
          await this.webRTCService.closePeerConnection(sessionId);
          
          // Notify orchestrator
          await this.orchestratorClient.notifySessionEnd(sessionId);
          
          this.activeSessions.delete(sessionId);
        }

        res.json({
          success: true,
          sessionId,
          status: 'ended'
        });

      } catch (error: any) {
        console.error('❌ Failed to end session:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get session status
    this.app.get('/session/:id/status', (req, res) => {
      const sessionId = req.params.id;
      const session = this.activeSessions.get(sessionId);
      
      if (!session) {
        return res.status(404).json({
          success: false,
          error: 'Session not found'
        });
      }

      res.json({
        success: true,
        session
      });
    });

    // List active sessions
    this.app.get('/sessions', (req, res) => {
      const sessions = Array.from(this.activeSessions.values());
      res.json({
        success: true,
        sessions,
        count: sessions.length
      });
    });

    // System control endpoints
    this.app.post('/system/execute', async (req, res) => {
      try {
        const { command, params, sessionId } = req.body;
        
        const result = await this.systemController.executeCommand(command, params, sessionId);
        
        res.json({
          success: true,
          result
        });

      } catch (error: any) {
        console.error('❌ System execution failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Screen capture control
    this.app.post('/screen/start', async (req, res) => {
      try {
        const { sessionId, options } = req.body;
        
        await this.screenCaptureService.startCapture(sessionId, options);
        
        res.json({
          success: true,
          message: 'Screen capture started'
        });

      } catch (error: any) {
        console.error('❌ Screen capture failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.post('/screen/stop', async (req, res) => {
      try {
        const { sessionId } = req.body;
        
        await this.screenCaptureService.stopCapture(sessionId);
        
        res.json({
          success: true,
          message: 'Screen capture stopped'
        });

      } catch (error: any) {
        console.error('❌ Screen capture stop failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });
  }

  private setupWebSocket(): void {
    this.wss.on('connection', (ws, req) => {
      console.log('🔌 New WebSocket connection from:', req.socket.remoteAddress);

      ws.on('message', async (data) => {
        try {
          const message = JSON.parse(data.toString());
          await this.handleWebSocketMessage(ws, message);
        } catch (error) {
          console.error('❌ Failed to handle WebSocket message:', error);
          ws.send(JSON.stringify({
            type: 'error',
            error: 'Invalid message format'
          }));
        }
      });

      ws.on('close', () => {
        console.log('🔌 WebSocket connection closed');
      });

      ws.on('error', (error) => {
        console.error('❌ WebSocket error:', error);
      });

      // Send welcome message
      ws.send(JSON.stringify({
        type: 'welcome',
        data: {
          service: 'jarvisx-pc-agent',
          timestamp: new Date().toISOString(),
          capabilities: {
            screenCapture: this.screenCaptureService.isAvailable(),
            webRTC: this.webRTCService.isInitialized(),
            systemControl: true
          }
        }
      }));
    });
  }

  private async handleWebSocketMessage(ws: any, message: any): Promise<void> {
    switch (message.type) {
      case 'start_session':
        try {
          const { sessionId, options } = message.data;
          
          // Create session
          const session = {
            id: sessionId,
            options: options || {},
            startTime: new Date(),
            status: 'active',
            ws
          };

          this.activeSessions.set(sessionId, session);

          // Start screen capture
          await this.screenCaptureService.startCapture(sessionId, options);

          // Initialize WebRTC
          const peerConnection = await this.webRTCService.createPeerConnection(sessionId);

          ws.send(JSON.stringify({
            type: 'session_started',
            data: {
              sessionId,
              webRTC: {
                localDescription: await peerConnection.createOffer()
              }
            }
          }));

        } catch (error: any) {
          ws.send(JSON.stringify({
            type: 'error',
            error: error.message
          }));
        }
        break;

      case 'end_session':
        try {
          const { sessionId } = message.data;
          
          await this.screenCaptureService.stopCapture(sessionId);
          await this.webRTCService.closePeerConnection(sessionId);
          
          this.activeSessions.delete(sessionId);

          ws.send(JSON.stringify({
            type: 'session_ended',
            data: { sessionId }
          }));

        } catch (error: any) {
          ws.send(JSON.stringify({
            type: 'error',
            error: error.message
          }));
        }
        break;

      case 'system_command':
        try {
          const { command, params, sessionId } = message.data;
          
          const result = await this.systemController.executeCommand(command, params, sessionId);
          
          ws.send(JSON.stringify({
            type: 'system_result',
            data: {
              command,
              result
            }
          }));

        } catch (error: any) {
          ws.send(JSON.stringify({
            type: 'error',
            error: error.message
          }));
        }
        break;

      default:
        console.log('📨 Unknown WebSocket message type:', message.type);
    }
  }

  private setupSystemHooks(): void {
    // Monitor system events and emit action events
    process.on('SIGINT', async () => {
      console.log('🛑 Shutting down PC Agent...');
      
      // End all active sessions
      for (const [sessionId] of this.activeSessions) {
        try {
          await this.screenCaptureService.stopCapture(sessionId);
          await this.webRTCService.closePeerConnection(sessionId);
        } catch (error) {
          console.error('❌ Error stopping session:', sessionId, error);
        }
      }
      
      process.exit(0);
    });
  }

  public async start(): Promise<void> {
    const PORT = process.env.PC_AGENT_PORT || 8005;
    
    try {
      this.server.listen(PORT, '0.0.0.0', () => {
        console.log(`🚀 JarvisX PC Agent running on port ${PORT}`);
        console.log(`📺 Screen capture: ${this.screenCaptureService.isAvailable() ? 'Available' : 'Unavailable'}`);
        console.log(`🌐 WebRTC: ${this.webRTCService.isInitialized() ? 'Initialized' : 'Not initialized'}`);
        console.log(`🎮 System control: Active`);
      });
    } catch (error) {
      console.error('Failed to start PC Agent:', error);
      process.exit(1);
    }
  }
}

// Start the PC Agent
const pcAgent = new JarvisXPCAgent();
pcAgent.start().catch((error) => {
  console.error('Failed to start PC Agent:', error);
  process.exit(1);
});

export default pcAgent;
