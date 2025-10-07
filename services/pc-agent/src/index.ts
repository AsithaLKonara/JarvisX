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
import { InputCaptureService } from './services/InputCaptureService';
import { OrchestratorClient } from './clients/OrchestratorClient';
import { SystemController } from './controllers/SystemController';
import { ScreenAnalysisService } from './services/ScreenAnalysisService';
import { BrowserAutomationService } from './services/BrowserAutomationService';
import { SafetyService } from './services/SafetyService';

dotenv.config();

class JarvisXPCAgent {
  private app: express.Application;
  private server: any;
  private wss: WebSocketServer;
  private screenCaptureService: ScreenCaptureService;
  private actionEventService: ActionEventService;
  private webRTCService: WebRTCService;
  private inputCaptureService: InputCaptureService;
  private orchestratorClient: OrchestratorClient;
  private systemController: SystemController;
  private screenAnalysisService: ScreenAnalysisService;
  private browserAutomationService: BrowserAutomationService;
  private safetyService: SafetyService;
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
      this.inputCaptureService = new InputCaptureService();
      this.orchestratorClient = new OrchestratorClient({
        baseUrl: process.env.ORCHESTRATOR_URL || 'http://localhost:3000',
        wsUrl: process.env.ORCHESTRATOR_WS_URL || 'ws://localhost:3000',
        apiKey: process.env.ORCHESTRATOR_API_KEY
      });
      this.systemController = new SystemController();
      this.screenAnalysisService = new ScreenAnalysisService();
      this.browserAutomationService = new BrowserAutomationService();
      this.safetyService = new SafetyService();

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
          systemControl: true,
          screenAnalysis: this.screenAnalysisService.isReady(),
          browserAutomation: this.browserAutomationService.isReady(),
          safetyFeatures: true
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

    // Screen analysis endpoints
    this.app.post('/screen/analyze', async (req, res) => {
      try {
        const { image, options } = req.body;
        
        if (!image) {
          return res.status(400).json({
            success: false,
            error: 'No image provided'
          });
        }

        const analysis = await this.screenAnalysisService.analyzeScreen(image, options);
        
        res.json({
          success: true,
          data: analysis
        });

      } catch (error: any) {
        console.error('❌ Screen analysis failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.post('/screen/find-element', async (req, res) => {
      try {
        const { image, description } = req.body;
        
        if (!image || !description) {
          return res.status(400).json({
            success: false,
            error: 'Image and description required'
          });
        }

        const element = await this.screenAnalysisService.findElement(image, description);
        
        res.json({
          success: true,
          data: {
            found: !!element,
            element: element
          }
        });

      } catch (error: any) {
        console.error('❌ Element finding failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.post('/screen/clickable-elements', async (req, res) => {
      try {
        const { image } = req.body;
        
        if (!image) {
          return res.status(400).json({
            success: false,
            error: 'Image required'
          });
        }

        const elements = await this.screenAnalysisService.getClickableElements(image);
        
        res.json({
          success: true,
          data: {
            elements,
            count: elements.length
          }
        });

      } catch (error: any) {
        console.error('❌ Clickable elements detection failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.post('/screen/click-element', async (req, res) => {
      try {
        const { image, elementDescription } = req.body;
        
        if (!image || !elementDescription) {
          return res.status(400).json({
            success: false,
            error: 'Image and element description required'
          });
        }

        const success = await this.screenAnalysisService.clickElement(image, elementDescription);
        
        res.json({
          success: success,
          message: success ? 'Element clicked successfully' : 'Failed to click element'
        });

      } catch (error: any) {
        console.error('❌ Element clicking failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.post('/screen/text', async (req, res) => {
      try {
        const { image } = req.body;
        
        if (!image) {
          return res.status(400).json({
            success: false,
            error: 'Image required'
          });
        }

        const text = await this.screenAnalysisService.getScreenText(image);
        
        res.json({
          success: true,
          data: {
            text: text
          }
        });

      } catch (error: any) {
        console.error('❌ Text extraction failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.post('/screen/description', async (req, res) => {
      try {
        const { image } = req.body;
        
        if (!image) {
          return res.status(400).json({
            success: false,
            error: 'Image required'
          });
        }

        const description = await this.screenAnalysisService.getScreenDescription(image);
        
        res.json({
          success: true,
          data: {
            description: description
          }
        });

      } catch (error: any) {
        console.error('❌ Description generation failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Browser automation endpoints
    this.app.post('/browser/create-session', async (req, res) => {
      try {
        const { sessionId } = req.body;
        
        if (!sessionId) {
          return res.status(400).json({
            success: false,
            error: 'Session ID required'
          });
        }

        const session = await this.browserAutomationService.createSession(sessionId);
        
        res.json({
          success: true,
          data: {
            sessionId: session.id,
            status: session.status,
            startTime: session.startTime
          }
        });

      } catch (error: any) {
        console.error('❌ Browser session creation failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.post('/browser/execute-action', async (req, res) => {
      try {
        const { sessionId, action } = req.body;
        
        if (!sessionId || !action) {
          return res.status(400).json({
            success: false,
            error: 'Session ID and action required'
          });
        }

        const result = await this.browserAutomationService.executeAction(sessionId, action);
        
        res.json({
          success: true,
          data: result
        });

      } catch (error: any) {
        console.error('❌ Browser action execution failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.get('/browser/page-content/:sessionId', async (req, res) => {
      try {
        const { sessionId } = req.params;
        
        const result = await this.browserAutomationService.getPageContent(sessionId);
        
        res.json(result);

      } catch (error: any) {
        console.error('❌ Get page content failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.get('/browser/elements/:sessionId', async (req, res) => {
      try {
        const { sessionId } = req.params;
        const { selector } = req.query;
        
        const result = await this.browserAutomationService.getElements(sessionId, selector as string);
        
        res.json(result);

      } catch (error: any) {
        console.error('❌ Get elements failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.post('/browser/close-session', async (req, res) => {
      try {
        const { sessionId } = req.body;
        
        if (!sessionId) {
          return res.status(400).json({
            success: false,
            error: 'Session ID required'
          });
        }

        await this.browserAutomationService.closeSession(sessionId);
        
        res.json({
          success: true,
          message: 'Session closed successfully'
        });

      } catch (error: any) {
        console.error('❌ Close session failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.get('/browser/sessions', (req, res) => {
      try {
        const sessions = this.browserAutomationService.getActiveSessions();
        const stats = this.browserAutomationService.getSessionStats();
        
        res.json({
          success: true,
          data: {
            sessions: sessions.map(s => ({
              id: s.id,
              status: s.status,
              startTime: s.startTime
            })),
            stats
          }
        });

      } catch (error: any) {
        console.error('❌ Get sessions failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Safety and security endpoints
    this.app.post('/safety/privacy-mode', (req, res) => {
      try {
        const { enabled } = req.body;
        
        if (enabled) {
          this.safetyService.enablePrivacyMode();
        } else {
          this.safetyService.disablePrivacyMode();
        }
        
        res.json({
          success: true,
          message: `Privacy mode ${enabled ? 'enabled' : 'disabled'}`,
          privacyMode: this.safetyService.isPrivacyModeEnabled()
        });

      } catch (error: any) {
        console.error('❌ Privacy mode toggle failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.post('/safety/emergency-stop', (req, res) => {
      try {
        const { action } = req.body;
        
        if (action === 'stop') {
          this.safetyService.emergencyStop();
          res.json({
            success: true,
            message: 'Emergency stop activated',
            emergencyStop: true
          });
        } else if (action === 'resume') {
          this.safetyService.resumeFromEmergencyStop();
          res.json({
            success: true,
            message: 'Emergency stop cleared',
            emergencyStop: false
          });
        } else {
          res.status(400).json({
            success: false,
            error: 'Invalid action. Use "stop" or "resume"'
          });
        }

      } catch (error: any) {
        console.error('❌ Emergency stop failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.post('/safety/autonomy-level', (req, res) => {
      try {
        const { level } = req.body;
        
        if (!['SUPERVISED', 'SEMI_AUTO', 'AUTONOMOUS', 'LEARNING'].includes(level)) {
          return res.status(400).json({
            success: false,
            error: 'Invalid autonomy level'
          });
        }
        
        this.safetyService.setAutonomyLevel(level);
        
        res.json({
          success: true,
          message: `Autonomy level set to ${level}`,
          autonomyLevel: level
        });

      } catch (error: any) {
        console.error('❌ Autonomy level change failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.post('/safety/assess-action', (req, res) => {
      try {
        const { action, params } = req.body;
        
        if (!action) {
          return res.status(400).json({
            success: false,
            error: 'Action required'
          });
        }
        
        const risk = this.safetyService.assessActionRisk(action, params);
        const canExecute = this.safetyService.canExecuteAction(action, params);
        
        res.json({
          success: true,
          data: {
            risk,
            canExecute: canExecute.allowed,
            reason: canExecute.reason
          }
        });

      } catch (error: any) {
        console.error('❌ Action assessment failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.post('/safety/approve-action', (req, res) => {
      try {
        const { action, approved } = req.body;
        
        if (!action || typeof approved !== 'boolean') {
          return res.status(400).json({
            success: false,
            error: 'Action and approved status required'
          });
        }
        
        this.safetyService.approveAction(action, approved);
        
        res.json({
          success: true,
          message: `Action "${action}" ${approved ? 'approved' : 'rejected'}`
        });

      } catch (error: any) {
        console.error('❌ Action approval failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.get('/safety/status', (req, res) => {
      try {
        const status = this.safetyService.getSafetyStatus();
        
        res.json({
          success: true,
          data: status
        });

      } catch (error: any) {
        console.error('❌ Get safety status failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    this.app.get('/safety/history', (req, res) => {
      try {
        const history = this.safetyService.getActionHistory();
        
        res.json({
          success: true,
          data: {
            history,
            count: history.length
          }
        });

      } catch (error: any) {
        console.error('❌ Get action history failed:', error);
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
