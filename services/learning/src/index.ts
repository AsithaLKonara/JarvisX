/**
 * JarvisX Learning Service
 * Autonomous learning and adaptation capabilities
 * Port: 8014
 */

import express from 'express';
import cors from 'cors';
import { LearningService } from './LearningService';
import dotenv from 'dotenv';

dotenv.config();

class JarvisXLearningService {
  private app: express.Application;
  private learningService: LearningService;

  constructor() {
    this.app = express();
    this.learningService = new LearningService();
    this.setupMiddleware();
    this.setupRoutes();
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
        service: 'jarvisx-learning',
        timestamp: new Date().toISOString(),
        initialized: this.learningService.isReady(),
        capabilities: {
          patternLearning: this.learningService.isReady(),
          insightGeneration: this.learningService.isReady(),
          prediction: this.learningService.isReady(),
          adaptation: this.learningService.isReady()
        }
      });
    });

    // Learn from interaction
    this.app.post('/learning/interaction', async (req, res) => {
      try {
        const { userId, command, context = {}, success, feedback } = req.body;

        if (!userId || !command || typeof success !== 'boolean') {
          return res.status(400).json({
            success: false,
            error: 'User ID, command, and success status required'
          });
        }

        console.log(`🧠 Learning from interaction: ${command} (${success ? 'success' : 'failure'})`);

        await this.learningService.learnFromInteraction(userId, command, context, success, feedback);

        res.json({
          success: true,
          message: 'Interaction learned successfully'
        });

      } catch (error: any) {
        console.error('❌ Learning from interaction failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Generate insights
    this.app.post('/learning/insights', async (req, res) => {
      try {
        const { userId } = req.body;

        if (!userId) {
          return res.status(400).json({
            success: false,
            error: 'User ID required'
          });
        }

        console.log(`💡 Generating insights for user: ${userId}`);

        const insights = await this.learningService.generateInsights(userId);

        res.json({
          success: true,
          data: {
            insights,
            count: insights.length
          }
        });

      } catch (error: any) {
        console.error('❌ Insight generation failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get predictions
    this.app.post('/learning/predictions', async (req, res) => {
      try {
        const { userId, context = {} } = req.body;

        if (!userId) {
          return res.status(400).json({
            success: false,
            error: 'User ID required'
          });
        }

        console.log(`🔮 Generating predictions for user: ${userId}`);

        const predictions = await this.learningService.getPredictions(userId, context);

        res.json({
          success: true,
          data: predictions
        });

      } catch (error: any) {
        console.error('❌ Prediction generation failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get learning patterns
    this.app.get('/learning/patterns', (req, res) => {
      try {
        const { userId } = req.query;

        const patterns = this.learningService.getPatterns(userId as string);

        res.json({
          success: true,
          data: {
            patterns,
            count: patterns.length
          }
        });

      } catch (error: any) {
        console.error('❌ Get patterns failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get insights
    this.app.get('/learning/insights', (req, res) => {
      try {
        const { userId } = req.query;

        const insights = this.learningService.getInsights(userId as string);

        res.json({
          success: true,
          data: {
            insights,
            count: insights.length
          }
        });

      } catch (error: any) {
        console.error('❌ Get insights failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get learning metrics
    this.app.get('/learning/metrics', (req, res) => {
      try {
        const metrics = this.learningService.getLearningMetrics();

        res.json({
          success: true,
          data: metrics
        });

      } catch (error: any) {
        console.error('❌ Get metrics failed:', error);
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
          service: 'JarvisX Learning Service',
          version: '1.0.0',
          port: 8014,
          status: this.learningService.isReady() ? 'ready' : 'initializing',
          features: [
            'Pattern recognition and learning',
            'Behavioral analysis',
            'Predictive suggestions',
            'Automation recommendations',
            'User preference learning',
            'Adaptive responses',
            'Performance optimization'
          ]
        }
      });
    });
  }

  public async start(): Promise<void> {
    const PORT = process.env.LEARNING_PORT || 8014;
    
    this.app.listen(PORT, '0.0.0.0', () => {
      console.log(`🚀 JarvisX Learning Service running on port ${PORT}`);
      console.log(`🧠 Pattern Learning: ${this.learningService.isReady() ? 'Ready' : 'Initializing...'}`);
      console.log(`💡 Insight Generation: Active`);
    });
  }
}

// Start the Learning service
const learningService = new JarvisXLearningService();

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('🛑 Shutting down Learning service...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('🛑 Shutting down Learning service...');
  process.exit(0);
});

learningService.start().catch((error) => {
  console.error('Failed to start Learning service:', error);
  process.exit(1);
});

export default learningService;
