/**
 * JarvisX Approval Service
 * Smart decision making and user approval system
 * Port: 8013
 */

import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import { ApprovalService } from './ApprovalService';
import dotenv from 'dotenv';

dotenv.config();

class JarvisXApprovalService {
  private app: express.Application;
  private server: any;
  private wss: WebSocketServer;
  private approvalService: ApprovalService;

  constructor() {
    this.app = express();
    this.server = createServer(this.app);
    this.wss = new WebSocketServer({ server: this.server });
    this.approvalService = new ApprovalService();
    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
  }

  private setupMiddleware(): void {
    this.app.use(cors());
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
  }

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        service: 'jarvisx-approval',
        timestamp: new Date().toISOString(),
        initialized: this.approvalService.isReady(),
        capabilities: {
          riskAssessment: this.approvalService.isReady(),
          approvalManagement: this.approvalService.isReady(),
          smartRecommendations: this.approvalService.isReady(),
          userPreferences: this.approvalService.isReady()
        }
      });
    });

    // Assess risk for action
    this.app.post('/approval/assess-risk', async (req, res) => {
      try {
        const { action, parameters, context = {} } = req.body;

        if (!action) {
          return res.status(400).json({
            success: false,
            error: 'Action description required'
          });
        }

        console.log('🔍 Assessing risk for action:', action);

        const assessment = await this.approvalService.assessRisk(action, parameters, context);

        res.json({
          success: true,
          data: assessment
        });

      } catch (error: any) {
        console.error('❌ Risk assessment failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Create approval request
    this.app.post('/approval/request', async (req, res) => {
      try {
        const { action, description, parameters, context = {}, userId, deviceId } = req.body;

        if (!action || !description) {
          return res.status(400).json({
            success: false,
            error: 'Action and description required'
          });
        }

        console.log('📝 Creating approval request for action:', action);

        const request = await this.approvalService.createApprovalRequest(
          action,
          description,
          parameters,
          context,
          userId,
          deviceId
        );

        // Notify via WebSocket if pending
        if (request.status === 'pending') {
          this.broadcastApprovalRequest(request);
        }

        res.json({
          success: true,
          data: request
        });

      } catch (error: any) {
        console.error('❌ Approval request creation failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Make approval decision
    this.app.post('/approval/decision', async (req, res) => {
      try {
        const { requestId, decision, reason, userId, suggestedModifications } = req.body;

        if (!requestId || !decision || !reason) {
          return res.status(400).json({
            success: false,
            error: 'Request ID, decision, and reason required'
          });
        }

        console.log(`🤔 Making decision for request ${requestId}: ${decision}`);

        const approvalDecision = await this.approvalService.makeDecision(
          requestId,
          decision,
          reason,
          userId,
          suggestedModifications
        );

        // Notify via WebSocket
        this.broadcastApprovalDecision(approvalDecision);

        res.json({
          success: true,
          data: approvalDecision
        });

      } catch (error: any) {
        console.error('❌ Decision making failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get smart recommendation
    this.app.post('/approval/recommendation', async (req, res) => {
      try {
        const { requestId } = req.body;

        if (!requestId) {
          return res.status(400).json({
            success: false,
            error: 'Request ID required'
          });
        }

        console.log(`🧠 Generating smart recommendation for request ${requestId}`);

        const recommendation = await this.approvalService.getSmartRecommendation(requestId);

        res.json({
          success: true,
          data: recommendation
        });

      } catch (error: any) {
        console.error('❌ Smart recommendation failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get approval request
    this.app.get('/approval/request/:requestId', (req, res) => {
      try {
        const { requestId } = req.params;

        const request = this.approvalService.getRequest(requestId);

        if (!request) {
          return res.status(404).json({
            success: false,
            error: 'Request not found'
          });
        }

        res.json({
          success: true,
          data: request
        });

      } catch (error: any) {
        console.error('❌ Get request failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get approval decision
    this.app.get('/approval/decision/:requestId', (req, res) => {
      try {
        const { requestId } = req.params;

        const decision = this.approvalService.getDecision(requestId);

        if (!decision) {
          return res.status(404).json({
            success: false,
            error: 'Decision not found'
          });
        }

        res.json({
          success: true,
          data: decision
        });

      } catch (error: any) {
        console.error('❌ Get decision failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get pending requests
    this.app.get('/approval/pending', (req, res) => {
      try {
        const pendingRequests = this.approvalService.getPendingRequests();

        res.json({
          success: true,
          data: {
            requests: pendingRequests,
            count: pendingRequests.length
          }
        });

      } catch (error: any) {
        console.error('❌ Get pending requests failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get requests by user
    this.app.get('/approval/user/:userId', (req, res) => {
      try {
        const { userId } = req.params;

        const requests = this.approvalService.getRequestsByUser(userId);

        res.json({
          success: true,
          data: {
            requests,
            count: requests.length
          }
        });

      } catch (error: any) {
        console.error('❌ Get user requests failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Set user preferences
    this.app.post('/approval/preferences', (req, res) => {
      try {
        const { userId, preferences } = req.body;

        if (!userId || !preferences) {
          return res.status(400).json({
            success: false,
            error: 'User ID and preferences required'
          });
        }

        this.approvalService.setUserPreferences(userId, preferences);

        res.json({
          success: true,
          message: 'User preferences updated successfully'
        });

      } catch (error: any) {
        console.error('❌ Set preferences failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get user preferences
    this.app.get('/approval/preferences/:userId', (req, res) => {
      try {
        const { userId } = req.params;

        const preferences = this.approvalService.getUserPreferences(userId);

        if (!preferences) {
          return res.status(404).json({
            success: false,
            error: 'User preferences not found'
          });
        }

        res.json({
          success: true,
          data: preferences
        });

      } catch (error: any) {
        console.error('❌ Get preferences failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get approval statistics
    this.app.get('/approval/stats', (req, res) => {
      try {
        const stats = this.approvalService.getApprovalStats();

        res.json({
          success: true,
          data: stats
        });

      } catch (error: any) {
        console.error('❌ Get stats failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Service info
    this.app.get('/info', (req, res) => {
      res.json({
        success: true,
        data: {
          service: 'JarvisX Approval Service',
          version: '1.0.0',
          port: 8013,
          status: this.approvalService.isReady() ? 'ready' : 'initializing',
          features: [
            'Intelligent risk assessment',
            'Smart approval recommendations',
            'User preference management',
            'Real-time notifications',
            'Multi-device support',
            'Audit logging',
            'Timeout management'
          ]
        }
      });
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
          service: 'jarvisx-approval',
          timestamp: new Date().toISOString(),
          capabilities: {
            riskAssessment: this.approvalService.isReady(),
            approvalManagement: this.approvalService.isReady(),
            smartRecommendations: this.approvalService.isReady()
          }
        }
      }));
    });
  }

  private async handleWebSocketMessage(ws: any, message: any): Promise<void> {
    switch (message.type) {
      case 'subscribe_approvals':
        // Client wants to receive approval notifications
        ws.subscribeApprovals = true;
        ws.send(JSON.stringify({
          type: 'subscribed',
          data: { notifications: 'approvals' }
        }));
        break;

      case 'get_pending_requests':
        try {
          const pendingRequests = this.approvalService.getPendingRequests();
          ws.send(JSON.stringify({
            type: 'pending_requests',
            data: { requests: pendingRequests }
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

  private broadcastApprovalRequest(request: any): void {
    const message = JSON.stringify({
      type: 'approval_request',
      data: request
    });

    this.wss.clients.forEach((ws: any) => {
      if (ws.subscribeApprovals && ws.readyState === ws.OPEN) {
        ws.send(message);
      }
    });
  }

  private broadcastApprovalDecision(decision: any): void {
    const message = JSON.stringify({
      type: 'approval_decision',
      data: decision
    });

    this.wss.clients.forEach((ws: any) => {
      if (ws.subscribeApprovals && ws.readyState === ws.OPEN) {
        ws.send(message);
      }
    });
  }

  public async start(): Promise<void> {
    const PORT = process.env.APPROVAL_PORT || 8013;
    
    this.server.listen(PORT, '0.0.0.0', () => {
      console.log(`🚀 JarvisX Approval Service running on port ${PORT}`);
      console.log(`🤔 Risk Assessment: ${this.approvalService.isReady() ? 'Ready' : 'Initializing...'}`);
      console.log(`📋 Approval Management: Active`);
    });
  }
}

// Start the Approval service
const approvalService = new JarvisXApprovalService();

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('🛑 Shutting down Approval service...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('🛑 Shutting down Approval service...');
  process.exit(0);
});

approvalService.start().catch((error) => {
  console.error('Failed to start Approval service:', error);
  process.exit(1);
});

export default approvalService;
