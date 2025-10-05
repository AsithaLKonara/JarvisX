/**
 * JarvisX Self-Training Engine
 * Autonomous learning and self-improvement system
 */

import express from 'express';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import dotenv from 'dotenv';
import cron from 'node-cron';

// Import self-training modules
import { SelfTrainingCore } from './core/SelfTrainingCore';
import { PatternRecognitionEngine } from './engine/PatternRecognitionEngine';
import { FeedbackLoopSystem } from './system/FeedbackLoopSystem';
import { AutonomousExperimenter } from './experimenter/AutonomousExperimenter';
import { KnowledgeSynthesizer } from './synthesizer/KnowledgeSynthesizer';
import { PerformanceOptimizer } from './optimizer/PerformanceOptimizer';

dotenv.config();

class JarvisXSelfTrainingService {
  private app: express.Application;
  private server: any;
  private wss: WebSocketServer;
  private selfTrainingCore: SelfTrainingCore;
  private patternRecognition: PatternRecognitionEngine;
  private feedbackLoop: FeedbackLoopSystem;
  private experimenter: AutonomousExperimenter;
  private synthesizer: KnowledgeSynthesizer;
  private optimizer: PerformanceOptimizer;

  constructor() {
    this.app = express();
    this.server = createServer(this.app);
    this.wss = new WebSocketServer({ server: this.server });
    
    this.initializeSelfTraining();
    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
    this.setupScheduledTraining();
  }

  private async initializeSelfTraining(): Promise<void> {
    console.log('🧠 Initializing JarvisX Self-Training Engine...');

    try {
      // Initialize self-training components
      this.selfTrainingCore = new SelfTrainingCore();
      this.patternRecognition = new PatternRecognitionEngine();
      this.feedbackLoop = new FeedbackLoopSystem();
      this.experimenter = new AutonomousExperimenter();
      this.synthesizer = new KnowledgeSynthesizer();
      this.optimizer = new PerformanceOptimizer();

      // Initialize training systems
      await this.selfTrainingCore.initialize({
        learningRate: 0.01,
        trainingFrequency: 'hourly',
        autoOptimization: true,
        experimentMode: true,
        knowledgeSynthesis: true
      });

      // Connect components
      this.patternRecognition.setTrainingCore(this.selfTrainingCore);
      this.feedbackLoop.setTrainingCore(this.selfTrainingCore);
      this.feedbackLoop.setPatternRecognition(this.patternRecognition);
      this.experimenter.setTrainingCore(this.selfTrainingCore);
      this.synthesizer.setTrainingCore(this.selfTrainingCore);
      this.optimizer.setTrainingCore(this.selfTrainingCore);

      console.log('✅ JarvisX Self-Training Engine initialized successfully');
      console.log('🤖 JarvisX is now capable of autonomous learning and self-improvement!');

    } catch (error) {
      console.error('❌ Failed to initialize Self-Training Engine:', error);
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
        service: 'jarvisx-self-training',
        timestamp: new Date().toISOString(),
        training: {
          isTraining: this.selfTrainingCore.isTraining(),
          lastTraining: this.selfTrainingCore.getLastTrainingTime(),
          trainingProgress: this.selfTrainingCore.getTrainingProgress(),
          patternsLearned: this.patternRecognition.getPatternCount(),
          experimentsRun: this.experimenter.getExperimentCount(),
          knowledgeSynthesized: this.synthesizer.getKnowledgeCount()
        }
      });
    });

    // Training status
    this.app.get('/training/status', (req, res) => {
      res.json({
        isTraining: this.selfTrainingCore.isTraining(),
        trainingProgress: this.selfTrainingCore.getTrainingProgress(),
        lastTraining: this.selfTrainingCore.getLastTrainingTime(),
        nextTraining: this.selfTrainingCore.getNextTrainingTime(),
        patternsLearned: this.patternRecognition.getPatternCount(),
        performanceMetrics: this.optimizer.getPerformanceMetrics(),
        experiments: this.experimenter.getRecentExperiments(10),
        knowledgeBase: this.synthesizer.getKnowledgeSummary()
      });
    });

    // Start training
    this.app.post('/training/start', async (req, res) => {
      try {
        const { mode = 'full', priority = 'normal' } = req.body;
        
        const trainingId = await this.selfTrainingCore.startTraining(mode, priority);
        
        res.json({
          success: true,
          trainingId,
          message: 'Training started successfully'
        });

      } catch (error: any) {
        console.error('❌ Failed to start training:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Stop training
    this.app.post('/training/stop', async (req, res) => {
      try {
        await this.selfTrainingCore.stopTraining();
        
        res.json({
          success: true,
          message: 'Training stopped successfully'
        });

      } catch (error: any) {
        console.error('❌ Failed to stop training:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Training results
    this.app.get('/training/results', async (req, res) => {
      try {
        const limit = parseInt(req.query.limit as string) || 20;
        const results = await this.selfTrainingCore.getTrainingResults(limit);
        
        res.json({
          success: true,
          results
        });

      } catch (error: any) {
        console.error('❌ Failed to get training results:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Pattern analysis
    this.app.get('/patterns/analyze', async (req, res) => {
      try {
        const analysis = await this.patternRecognition.analyzePatterns();
        
        res.json({
          success: true,
          analysis
        });

      } catch (error: any) {
        console.error('❌ Failed to analyze patterns:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Performance optimization
    this.app.post('/optimization/run', async (req, res) => {
      try {
        const { target = 'response_quality' } = req.body;
        
        const optimizationResult = await this.optimizer.runOptimization(target);
        
        res.json({
          success: true,
          result: optimizationResult
        });

      } catch (error: any) {
        console.error('❌ Failed to run optimization:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Knowledge synthesis
    this.app.post('/knowledge/synthesize', async (req, res) => {
      try {
        const { source = 'all', depth = 'medium' } = req.body;
        
        const synthesis = await this.synthesizer.synthesizeKnowledge(source, depth);
        
        res.json({
          success: true,
          synthesis
        });

      } catch (error: any) {
        console.error('❌ Failed to synthesize knowledge:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Experiment management
    this.app.get('/experiments', (req, res) => {
      const limit = parseInt(req.query.limit as string) || 20;
      const experiments = this.experimenter.getRecentExperiments(limit);
      
      res.json({
        success: true,
        experiments
      });
    });

    this.app.post('/experiments/run', async (req, res) => {
      try {
        const { type = 'response_improvement', parameters = {} } = req.body;
        
        const experiment = await this.experimenter.runExperiment(type, parameters);
        
        res.json({
          success: true,
          experiment
        });

      } catch (error: any) {
        console.error('❌ Failed to run experiment:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Learning progress
    this.app.get('/learning/progress', (req, res) => {
      res.json({
        success: true,
        progress: {
          totalInteractions: this.selfTrainingCore.getTotalInteractions(),
          patternsLearned: this.patternRecognition.getPatternCount(),
          experimentsRun: this.experimenter.getExperimentCount(),
          knowledgeSynthesized: this.synthesizer.getKnowledgeCount(),
          performanceImprovements: this.optimizer.getImprovementHistory(),
          learningRate: this.selfTrainingCore.getLearningRate(),
          lastImprovement: this.selfTrainingCore.getLastImprovementTime()
        }
      });
    });

    // Export training data
    this.app.get('/export/training-data', async (req, res) => {
      try {
        const format = req.query.format as string || 'json';
        const data = await this.selfTrainingCore.exportTrainingData(format);
        
        res.setHeader('Content-Type', format === 'csv' ? 'text/csv' : 'application/json');
        res.setHeader('Content-Disposition', `attachment; filename=jarvisx-training-data.${format}`);
        res.send(data);

      } catch (error: any) {
        console.error('❌ Failed to export training data:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });
  }

  private setupWebSocket(): void {
    this.wss.on('connection', (ws, req) => {
      console.log('🔌 New WebSocket connection to self-training service');

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

      // Send training status
      ws.send(JSON.stringify({
        type: 'training_status',
        data: {
          isTraining: this.selfTrainingCore.isTraining(),
          progress: this.selfTrainingCore.getTrainingProgress(),
          lastTraining: this.selfTrainingCore.getLastTrainingTime(),
          patternsLearned: this.patternRecognition.getPatternCount(),
          timestamp: new Date().toISOString()
        }
      }));
    });
  }

  private async handleWebSocketMessage(ws: any, message: any): Promise<void> {
    switch (message.type) {
      case 'start_training':
        try {
          const { mode, priority } = message.data;
          const trainingId = await this.selfTrainingCore.startTraining(mode, priority);
          
          ws.send(JSON.stringify({
            type: 'training_started',
            data: { trainingId, mode, priority }
          }));

        } catch (error: any) {
          ws.send(JSON.stringify({
            type: 'error',
            error: error.message
          }));
        }
        break;

      case 'get_training_status':
        try {
          const status = {
            isTraining: this.selfTrainingCore.isTraining(),
            progress: this.selfTrainingCore.getTrainingProgress(),
            lastTraining: this.selfTrainingCore.getLastTrainingTime(),
            patternsLearned: this.patternRecognition.getPatternCount(),
            experimentsRun: this.experimenter.getExperimentCount()
          };
          
          ws.send(JSON.stringify({
            type: 'training_status',
            data: status
          }));

        } catch (error: any) {
          ws.send(JSON.stringify({
            type: 'error',
            error: error.message
          }));
        }
        break;

      case 'run_experiment':
        try {
          const { type, parameters } = message.data;
          const experiment = await this.experimenter.runExperiment(type, parameters);
          
          ws.send(JSON.stringify({
            type: 'experiment_result',
            data: experiment
          }));

        } catch (error: any) {
          ws.send(JSON.stringify({
            type: 'error',
            error: error.message
          }));
        }
        break;

      case 'optimize_performance':
        try {
          const { target } = message.data;
          const result = await this.optimizer.runOptimization(target);
          
          ws.send(JSON.stringify({
            type: 'optimization_result',
            data: result
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

  private setupScheduledTraining(): void {
    // Run training every hour
    cron.schedule('0 * * * *', async () => {
      console.log('🔄 Running scheduled self-training...');
      try {
        await this.selfTrainingCore.runScheduledTraining();
      } catch (error) {
        console.error('❌ Scheduled training failed:', error);
      }
    });

    // Run pattern analysis every 6 hours
    cron.schedule('0 */6 * * *', async () => {
      console.log('🔍 Running pattern analysis...');
      try {
        await this.patternRecognition.runScheduledAnalysis();
      } catch (error) {
        console.error('❌ Pattern analysis failed:', error);
      }
    });

    // Run optimization every 12 hours
    cron.schedule('0 */12 * * *', async () => {
      console.log('⚡ Running performance optimization...');
      try {
        await this.optimizer.runScheduledOptimization();
      } catch (error) {
        console.error('❌ Optimization failed:', error);
      }
    });

    // Synthesize knowledge daily
    cron.schedule('0 2 * * *', async () => {
      console.log('🧠 Synthesizing knowledge...');
      try {
        await this.synthesizer.runScheduledSynthesis();
      } catch (error) {
        console.error('❌ Knowledge synthesis failed:', error);
      }
    });

    console.log('⏰ Scheduled training tasks configured');
  }

  public async start(): Promise<void> {
    const PORT = process.env.SELF_TRAINING_PORT || 8008;
    
    try {
      this.server.listen(PORT, '0.0.0.0', () => {
        console.log(`🧠 JarvisX Self-Training Engine running on port ${PORT}`);
        console.log(`🤖 JarvisX is now capable of autonomous learning!`);
        console.log(`📊 Training status: ${this.selfTrainingCore.isTraining() ? 'Active' : 'Idle'}`);
        console.log(`🔍 Patterns learned: ${this.patternRecognition.getPatternCount()}`);
        console.log(`🧪 Experiments run: ${this.experimenter.getExperimentCount()}`);
      });
    } catch (error) {
      console.error('Failed to start Self-Training Engine:', error);
      process.exit(1);
    }
  }
}

// Start the Self-Training Engine
const selfTrainingService = new JarvisXSelfTrainingService();
selfTrainingService.start().catch((error) => {
  console.error('Failed to start Self-Training Engine:', error);
  process.exit(1);
});

export default selfTrainingService;
