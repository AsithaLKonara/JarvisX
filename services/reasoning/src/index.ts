/**
 * JarvisX Reasoning Service
 * Advanced AI reasoning with chain-of-thought planning
 * Port: 8016
 */

import express from 'express';
import cors from 'cors';
import { ReasoningEngine } from './ReasoningEngine';
import dotenv from 'dotenv';

dotenv.config();

class JarvisXReasoningService {
  private app: express.Application;
  private reasoningEngine: ReasoningEngine;

  constructor() {
    this.app = express();
    this.reasoningEngine = new ReasoningEngine();
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
        service: 'jarvisx-reasoning',
        timestamp: new Date().toISOString(),
        initialized: this.reasoningEngine.isReady(),
        capabilities: {
          chainOfThought: this.reasoningEngine.isReady(),
          planGeneration: this.reasoningEngine.isReady(),
          planExecution: this.reasoningEngine.isReady(),
          reasoningAnalysis: this.reasoningEngine.isReady()
        }
      });
    });

    // Generate chain of thought
    this.app.post('/reasoning/chain-of-thought', async (req, res) => {
      try {
        const { problem, context = {} } = req.body;

        if (!problem) {
          return res.status(400).json({
            success: false,
            error: 'Problem description required'
          });
        }

        console.log('🧠 Generating chain of thought...');

        const chainOfThought = await this.reasoningEngine.generateChainOfThought(problem, context);

        res.json({
          success: true,
          data: chainOfThought
        });

      } catch (error: any) {
        console.error('❌ Chain of thought generation failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Create reasoning plan
    this.app.post('/reasoning/create-plan', async (req, res) => {
      try {
        const { goal, context = {} } = req.body;

        if (!goal) {
          return res.status(400).json({
            success: false,
            error: 'Goal description required'
          });
        }

        console.log('📋 Creating reasoning plan...');

        const plan = await this.reasoningEngine.createReasoningPlan(goal, context);

        res.json({
          success: true,
          data: plan
        });

      } catch (error: any) {
        console.error('❌ Plan creation failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Execute reasoning plan
    this.app.post('/reasoning/execute-plan', async (req, res) => {
      try {
        const { planId } = req.body;

        if (!planId) {
          return res.status(400).json({
            success: false,
            error: 'Plan ID required'
          });
        }

        console.log(`🚀 Executing reasoning plan: ${planId}`);

        const result = await this.reasoningEngine.executePlan(planId);

        res.json({
          success: result.success,
          data: result
        });

      } catch (error: any) {
        console.error('❌ Plan execution failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get reasoning plan
    this.app.get('/reasoning/plan/:planId', (req, res) => {
      try {
        const { planId } = req.params;

        const plan = this.reasoningEngine.getPlan(planId);

        if (!plan) {
          return res.status(404).json({
            success: false,
            error: 'Plan not found'
          });
        }

        res.json({
          success: true,
          data: plan
        });

      } catch (error: any) {
        console.error('❌ Get plan failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get all plans
    this.app.get('/reasoning/plans', (req, res) => {
      try {
        const plans = this.reasoningEngine.getAllPlans();

        res.json({
          success: true,
          data: {
            plans,
            count: plans.length
          }
        });

      } catch (error: any) {
        console.error('❌ Get plans failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Update reasoning plan
    this.app.put('/reasoning/plan/:planId', (req, res) => {
      try {
        const { planId } = req.params;
        const updates = req.body;

        const success = this.reasoningEngine.updatePlan(planId, updates);

        if (!success) {
          return res.status(404).json({
            success: false,
            error: 'Plan not found'
          });
        }

        res.json({
          success: true,
          message: 'Plan updated successfully'
        });

      } catch (error: any) {
        console.error('❌ Update plan failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Delete reasoning plan
    this.app.delete('/reasoning/plan/:planId', (req, res) => {
      try {
        const { planId } = req.params;

        const success = this.reasoningEngine.deletePlan(planId);

        if (!success) {
          return res.status(404).json({
            success: false,
            error: 'Plan not found'
          });
        }

        res.json({
          success: true,
          message: 'Plan deleted successfully'
        });

      } catch (error: any) {
        console.error('❌ Delete plan failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get plan statistics
    this.app.get('/reasoning/stats', (req, res) => {
      try {
        const stats = this.reasoningEngine.getPlanStats();

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
          service: 'JarvisX Reasoning Service',
          version: '1.0.0',
          port: 8016,
          status: this.reasoningEngine.isReady() ? 'ready' : 'initializing',
          features: [
            'Chain-of-thought reasoning',
            'Intelligent plan generation',
            'Multi-step plan execution',
            'Context-aware analysis',
            'Adaptive planning',
            'Risk assessment',
            'Performance evaluation'
          ]
        }
      });
    });
  }

  public async start(): Promise<void> {
    const PORT = process.env.REASONING_PORT || 8016;
    
    this.app.listen(PORT, '0.0.0.0', () => {
      console.log(`🚀 JarvisX Reasoning Service running on port ${PORT}`);
      console.log(`🧠 Chain-of-thought: ${this.reasoningEngine.isReady() ? 'Ready' : 'Initializing...'}`);
      console.log(`📋 Plan Generation: Active`);
    });
  }
}

// Start the Reasoning service
const reasoningService = new JarvisXReasoningService();

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('🛑 Shutting down Reasoning service...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('🛑 Shutting down Reasoning service...');
  process.exit(0);
});

reasoningService.start().catch((error) => {
  console.error('Failed to start Reasoning service:', error);
  process.exit(1);
});

export default reasoningService;
