/**
 * JarvisX Trading Service
 * Binance integration with safety controls and AI recommendations
 */

import express from 'express';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import dotenv from 'dotenv';
import { v4 as uuidv4 } from 'uuid';

// Import modules
import { BinanceClient } from './clients/BinanceClient';
import { TradingStrategy } from './strategies/TradingStrategy';
import { RiskManager } from './services/RiskManager';
import { AIAdvisor } from './services/AIAdvisor';

dotenv.config();

class JarvisXTradingService {
  private app: express.Application;
  private server: any;
  private wss: WebSocketServer;
  private binanceClient: BinanceClient;
  private tradingStrategy: TradingStrategy;
  private riskManager: RiskManager;
  private aiAdvisor: AIAdvisor;
  private activePositions: Map<string, any> = new Map();
  private pendingApprovals: Map<string, any> = new Map();

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
    console.log('🚀 Initializing JarvisX Trading Service...');

    try {
      // Initialize core services
      this.binanceClient = new BinanceClient();
      this.tradingStrategy = new TradingStrategy();
      this.riskManager = new RiskManager();
      this.aiAdvisor = new AIAdvisor();

      // Initialize Binance client
      await this.binanceClient.initialize();

      // Start market data streaming
      await this.binanceClient.startMarketDataStream((data) => {
        this.handleMarketData(data);
      });

      console.log('✅ Trading Service initialized successfully');

    } catch (error) {
      console.error('❌ Failed to initialize Trading Service:', error);
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
        service: 'jarvisx-trading',
        timestamp: new Date().toISOString(),
        activePositions: this.activePositions.size,
        pendingApprovals: this.pendingApprovals.size,
        binanceConnected: this.binanceClient.isConnected()
      });
    });

    // Get trading summary
    this.app.get('/trade/summary', async (req, res) => {
      try {
        const positions = await this.binanceClient.getPositions();
        const recommendations = await this.aiAdvisor.getRecommendations();
        const currentExposure = this.riskManager.getCurrentExposure();

        res.json({
          success: true,
          positions,
          recommendations,
          currentExposure,
          riskLimits: this.riskManager.getRiskLimits()
        });

      } catch (error: any) {
        console.error('❌ Failed to get trading summary:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Execute trade
    this.app.post('/trade/execute', async (req, res) => {
      try {
        const { recommendation, dry_run = false, auto_approve = false } = req.body;

        console.log(`🎯 Executing trade: ${recommendation.symbol} ${recommendation.action}`);

        // Risk check
        const riskCheck = await this.riskManager.validateTrade(recommendation);
        if (!riskCheck.approved) {
          return res.status(400).json({
            success: false,
            error: riskCheck.reason
          });
        }

        if (dry_run) {
          return res.json({
            success: true,
            dry_run: true,
            message: 'Trade validated successfully (dry run)',
            recommendation,
            riskCheck
          });
        }

        // Check if approval is required
        if (recommendation.riskLevel === 'high' && !auto_approve) {
          const approvalId = uuidv4();
          this.pendingApprovals.set(approvalId, {
            id: approvalId,
            recommendation,
            timestamp: new Date(),
            status: 'pending'
          });

          // Notify clients for approval
          this.notifyApprovalRequest(approvalId, recommendation);

          return res.json({
            success: true,
            requires_approval: true,
            approval_id: approvalId,
            message: 'High-risk trade requires approval'
          });
        }

        // Execute trade
        const result = await this.binanceClient.executeTrade(recommendation);

        // Update positions
        await this.updatePositions();

        // Log trade
        await this.logTrade(recommendation, result);

        res.json({
          success: true,
          result,
          recommendation
        });

      } catch (error: any) {
        console.error('❌ Trade execution failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Handle approval
    this.app.post('/trade/approve', async (req, res) => {
      try {
        const { approvalId, approved } = req.body;

        const approval = this.pendingApprovals.get(approvalId);
        if (!approval) {
          return res.status(404).json({
            success: false,
            error: 'Approval not found'
          });
        }

        if (approved) {
          // Execute the approved trade
          const result = await this.binanceClient.executeTrade(approval.recommendation);
          
          // Update positions
          await this.updatePositions();

          // Log trade
          await this.logTrade(approval.recommendation, result);

          res.json({
            success: true,
            message: 'Trade executed successfully',
            result
          });
        } else {
          res.json({
            success: true,
            message: 'Trade rejected'
          });
        }

        // Remove approval
        this.pendingApprovals.delete(approvalId);

      } catch (error: any) {
        console.error('❌ Approval handling failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get market data
    this.app.get('/market/:symbol', async (req, res) => {
      try {
        const { symbol } = req.params;
        const marketData = await this.binanceClient.getMarketData(symbol);

        res.json({
          success: true,
          symbol,
          data: marketData
        });

      } catch (error: any) {
        console.error('❌ Failed to get market data:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Risk management endpoints
    this.app.get('/risk/limits', (req, res) => {
      res.json({
        success: true,
        limits: this.riskManager.getRiskLimits()
      });
    });

    this.app.post('/risk/limits', (req, res) => {
      try {
        const limits = req.body;
        this.riskManager.updateRiskLimits(limits);

        res.json({
          success: true,
          message: 'Risk limits updated',
          limits: this.riskManager.getRiskLimits()
        });

      } catch (error: any) {
        console.error('❌ Failed to update risk limits:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });
  }

  private setupWebSocket(): void {
    this.wss.on('connection', (ws, req) => {
      console.log('🔌 New WebSocket connection to trading service');

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
          service: 'jarvisx-trading',
          timestamp: new Date().toISOString(),
          connected: this.binanceClient.isConnected()
        }
      }));
    });
  }

  private async handleWebSocketMessage(ws: any, message: any): Promise<void> {
    switch (message.type) {
      case 'subscribe_market_data':
        // Subscribe to market data updates
        ws.marketDataSubscription = true;
        break;

      case 'get_positions':
        try {
          const positions = await this.binanceClient.getPositions();
          ws.send(JSON.stringify({
            type: 'positions_update',
            data: positions
          }));
        } catch (error) {
          ws.send(JSON.stringify({
            type: 'error',
            error: 'Failed to get positions'
          }));
        }
        break;

      case 'get_recommendations':
        try {
          const recommendations = await this.aiAdvisor.getRecommendations();
          ws.send(JSON.stringify({
            type: 'recommendations_update',
            data: recommendations
          }));
        } catch (error) {
          ws.send(JSON.stringify({
            type: 'error',
            error: 'Failed to get recommendations'
          }));
        }
        break;

      default:
        console.log('📨 Unknown WebSocket message type:', message.type);
    }
  }

  private async handleMarketData(data: any): Promise<void> {
    // Update AI advisor with new market data
    await this.aiAdvisor.updateMarketData(data);

    // Check for strategy signals
    const signals = await this.tradingStrategy.analyze(data);

    // Broadcast to connected clients
    this.wss.clients.forEach((client) => {
      if (client.marketDataSubscription && client.readyState === 1) {
        client.send(JSON.stringify({
          type: 'market_data',
          data
        }));

        if (signals.length > 0) {
          client.send(JSON.stringify({
            type: 'trading_signals',
            data: signals
          }));
        }
      }
    });
  }

  private async updatePositions(): Promise<void> {
    try {
      const positions = await this.binanceClient.getPositions();
      this.activePositions.clear();
      
      positions.forEach((position: any) => {
        this.activePositions.set(position.symbol, position);
      });

      // Update risk manager
      this.riskManager.updatePositions(positions);

    } catch (error) {
      console.error('❌ Failed to update positions:', error);
    }
  }

  private async logTrade(recommendation: any, result: any): Promise<void> {
    const tradeLog = {
      id: uuidv4(),
      timestamp: new Date().toISOString(),
      recommendation,
      result,
      status: result.success ? 'executed' : 'failed'
    };

    console.log('📊 Trade logged:', tradeLog);
    // Here you would save to database or audit log
  }

  private notifyApprovalRequest(approvalId: string, recommendation: any): void {
    const approvalRequest = {
      type: 'approval_request',
      data: {
        id: approvalId,
        action: `${recommendation.action} ${recommendation.symbol}`,
        recommendation,
        timestamp: new Date().toISOString()
      }
    };

    // Broadcast to all connected clients
    this.wss.clients.forEach((client) => {
      if (client.readyState === 1) {
        client.send(JSON.stringify(approvalRequest));
      }
    });
  }

  public async start(): Promise<void> {
    const PORT = process.env.TRADING_SERVICE_PORT || 8006;
    
    try {
      this.server.listen(PORT, '0.0.0.0', () => {
        console.log(`🚀 JarvisX Trading Service running on port ${PORT}`);
        console.log(`📊 Binance API: ${this.binanceClient.isConnected() ? 'Connected' : 'Disconnected'}`);
        console.log(`🛡️ Risk Management: Active`);
        console.log(`🤖 AI Advisor: Active`);
      });
    } catch (error) {
      console.error('Failed to start Trading Service:', error);
      process.exit(1);
    }
  }
}

// Start the Trading Service
const tradingService = new JarvisXTradingService();
tradingService.start().catch((error) => {
  console.error('Failed to start Trading Service:', error);
  process.exit(1);
});

export default tradingService;
