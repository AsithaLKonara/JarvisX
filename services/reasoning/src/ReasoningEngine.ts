/**
 * JarvisX Advanced Reasoning Engine
 * Chain-of-thought planning and intelligent decision making
 */

import OpenAI from 'openai';
import axios from 'axios';

export interface ReasoningStep {
  id: string;
  type: 'analysis' | 'planning' | 'execution' | 'evaluation' | 'adaptation';
  description: string;
  input: any;
  output: any;
  confidence: number;
  timestamp: Date;
  dependencies: string[];
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped';
}

export interface ReasoningPlan {
  id: string;
  goal: string;
  context: any;
  steps: ReasoningStep[];
  status: 'draft' | 'approved' | 'executing' | 'completed' | 'failed' | 'cancelled';
  confidence: number;
  estimatedDuration: number; // in minutes
  priority: 'low' | 'medium' | 'high' | 'critical';
  createdAt: Date;
  updatedAt: Date;
  completedAt?: Date;
}

export interface ChainOfThought {
  problem: string;
  context: any;
  reasoning: string[];
  considerations: string[];
  alternatives: string[];
  decision: string;
  confidence: number;
  reasoning_quality: 'poor' | 'fair' | 'good' | 'excellent';
}

export class ReasoningEngine {
  private openai: OpenAI;
  private plans: Map<string, ReasoningPlan> = new Map();
  private isInitialized: boolean = false;

  constructor() {
    this.initializeOpenAI();
  }

  private initializeOpenAI(): void {
    try {
      if (!process.env.OPENAI_API_KEY) {
        throw new Error('OPENAI_API_KEY not found in environment variables');
      }

      this.openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
      });

      this.isInitialized = true;
      console.log('✅ Reasoning Engine OpenAI client initialized');
      
    } catch (error) {
      console.error('❌ Failed to initialize Reasoning Engine OpenAI client:', error);
      this.isInitialized = false;
    }
  }

  public async generateChainOfThought(problem: string, context: any = {}): Promise<ChainOfThought> {
    if (!this.isInitialized) {
      throw new Error('Reasoning Engine not initialized');
    }

    try {
      console.log('🧠 Generating chain of thought for problem:', problem);

      const prompt = `You are an advanced AI reasoning system. Analyze the following problem and provide a detailed chain of thought.

Problem: ${problem}

Context: ${JSON.stringify(context, null, 2)}

Please provide a comprehensive analysis following this structure:

1. PROBLEM ANALYSIS: Break down the problem into its core components
2. CONTEXT CONSIDERATION: Analyze the given context and its implications
3. REASONING CHAIN: Step-by-step logical reasoning process
4. CONSIDERATIONS: Important factors to consider
5. ALTERNATIVES: Different approaches or solutions
6. DECISION: Your recommended approach with justification
7. CONFIDENCE: Rate your confidence (0-100)
8. REASONING QUALITY: Assess the quality of your reasoning (poor/fair/good/excellent)

Respond in JSON format:
{
  "problem": "restated problem",
  "context": "context analysis",
  "reasoning": ["step1", "step2", "step3", ...],
  "considerations": ["factor1", "factor2", ...],
  "alternatives": ["approach1", "approach2", ...],
  "decision": "recommended approach with justification",
  "confidence": 85,
  "reasoning_quality": "good"
}`;

      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an advanced AI reasoning system specializing in chain-of-thought analysis and problem-solving. Provide detailed, logical, and well-structured reasoning."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        max_tokens: 2000,
        temperature: 0.3
      });

      const content = response.choices[0].message.content || '{}';
      const chainOfThought = JSON.parse(content);

      console.log('✅ Chain of thought generated successfully');
      return chainOfThought;

    } catch (error) {
      console.error('❌ Chain of thought generation failed:', error);
      throw error;
    }
  }

  public async createReasoningPlan(goal: string, context: any = {}): Promise<ReasoningPlan> {
    try {
      console.log('📋 Creating reasoning plan for goal:', goal);

      // Generate chain of thought first
      const chainOfThought = await this.generateChainOfThought(goal, context);

      // Create detailed plan based on reasoning
      const planPrompt = `Based on the following chain of thought analysis, create a detailed execution plan.

Chain of Thought:
${JSON.stringify(chainOfThought, null, 2)}

Create a step-by-step execution plan with:
1. Clear, actionable steps
2. Dependencies between steps
3. Estimated time for each step
4. Risk assessment for each step
5. Success criteria for each step

Respond in JSON format:
{
  "steps": [
    {
      "id": "step1",
      "type": "analysis",
      "description": "Analyze the current situation",
      "input": "context data",
      "output": "analysis results",
      "confidence": 90,
      "dependencies": [],
      "estimatedTime": 5,
      "riskLevel": "low",
      "successCriteria": "Complete analysis with 90%+ confidence"
    }
  ],
  "estimatedDuration": 30,
  "priority": "medium",
  "confidence": 85
}`;

      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an expert project planner. Create detailed, executable plans based on reasoning analysis."
          },
          {
            role: "user",
            content: planPrompt
          }
        ],
        max_tokens: 3000,
        temperature: 0.2
      });

      const content = response.choices[0].message.content || '{}';
      const planData = JSON.parse(content);

      const plan: ReasoningPlan = {
        id: this.generateId(),
        goal,
        context,
        steps: planData.steps.map((step: any) => ({
          ...step,
          timestamp: new Date(),
          status: 'pending' as const
        })),
        status: 'draft',
        confidence: planData.confidence || 85,
        estimatedDuration: planData.estimatedDuration || 30,
        priority: planData.priority || 'medium',
        createdAt: new Date(),
        updatedAt: new Date()
      };

      this.plans.set(plan.id, plan);
      console.log(`✅ Reasoning plan created: ${plan.id}`);

      return plan;

    } catch (error) {
      console.error('❌ Reasoning plan creation failed:', error);
      throw error;
    }
  }

  public async executePlan(planId: string): Promise<{ success: boolean; results: any[]; errors: any[] }> {
    const plan = this.plans.get(planId);
    if (!plan) {
      throw new Error(`Plan ${planId} not found`);
    }

    try {
      console.log(`🚀 Executing reasoning plan: ${planId}`);
      
      plan.status = 'executing';
      plan.updatedAt = new Date();

      const results: any[] = [];
      const errors: any[] = [];

      // Execute steps in dependency order
      const executedSteps = new Set<string>();
      let hasChanges = true;

      while (hasChanges) {
        hasChanges = false;

        for (const step of plan.steps) {
          if (step.status === 'pending' && this.canExecuteStep(step, executedSteps)) {
            try {
              console.log(`⚡ Executing step: ${step.description}`);
              
              step.status = 'in_progress';
              step.timestamp = new Date();

              // Execute the step
              const result = await this.executeStep(step, plan.context);
              
              step.output = result;
              step.status = 'completed';
              step.timestamp = new Date();
              
              executedSteps.add(step.id);
              results.push({ stepId: step.id, result });
              hasChanges = true;

              console.log(`✅ Step completed: ${step.description}`);

            } catch (error) {
              console.error(`❌ Step failed: ${step.description}`, error);
              
              step.status = 'failed';
              step.timestamp = new Date();
              
              errors.push({ stepId: step.id, error: error.message });
              hasChanges = true;
            }
          }
        }
      }

      // Check if all steps completed
      const allCompleted = plan.steps.every(step => 
        step.status === 'completed' || step.status === 'skipped'
      );

      if (allCompleted) {
        plan.status = 'completed';
        plan.completedAt = new Date();
        console.log(`🎉 Plan completed successfully: ${planId}`);
      } else {
        plan.status = 'failed';
        console.log(`❌ Plan failed: ${planId}`);
      }

      plan.updatedAt = new Date();

      return {
        success: allCompleted,
        results,
        errors
      };

    } catch (error) {
      console.error(`❌ Plan execution failed: ${planId}`, error);
      plan.status = 'failed';
      plan.updatedAt = new Date();
      
      return {
        success: false,
        results: [],
        errors: [{ error: error.message }]
      };
    }
  }

  private canExecuteStep(step: ReasoningStep, executedSteps: Set<string>): boolean {
    return step.dependencies.every(depId => executedSteps.has(depId));
  }

  private async executeStep(step: ReasoningStep, context: any): Promise<any> {
    // This would integrate with actual services based on step type
    switch (step.type) {
      case 'analysis':
        return await this.performAnalysis(step, context);
      case 'planning':
        return await this.performPlanning(step, context);
      case 'execution':
        return await this.performExecution(step, context);
      case 'evaluation':
        return await this.performEvaluation(step, context);
      case 'adaptation':
        return await this.performAdaptation(step, context);
      default:
        throw new Error(`Unknown step type: ${step.type}`);
    }
  }

  private async performAnalysis(step: ReasoningStep, context: any): Promise<any> {
    // Simulate analysis - in real implementation, this would call actual services
    return {
      analysis: `Analyzed ${step.description}`,
      findings: ['Finding 1', 'Finding 2'],
      confidence: step.confidence
    };
  }

  private async performPlanning(step: ReasoningStep, context: any): Promise<any> {
    // Simulate planning - in real implementation, this would create detailed plans
    return {
      plan: `Planned ${step.description}`,
      subSteps: ['Sub-step 1', 'Sub-step 2'],
      timeline: '5 minutes'
    };
  }

  private async performExecution(step: ReasoningStep, context: any): Promise<any> {
    // Simulate execution - in real implementation, this would call PC Agent or other services
    return {
      execution: `Executed ${step.description}`,
      result: 'Success',
      duration: '2 minutes'
    };
  }

  private async performEvaluation(step: ReasoningStep, context: any): Promise<any> {
    // Simulate evaluation - in real implementation, this would assess results
    return {
      evaluation: `Evaluated ${step.description}`,
      score: 85,
      feedback: 'Good performance'
    };
  }

  private async performAdaptation(step: ReasoningStep, context: any): Promise<any> {
    // Simulate adaptation - in real implementation, this would adjust plans
    return {
      adaptation: `Adapted ${step.description}`,
      changes: ['Change 1', 'Change 2'],
      reason: 'Based on evaluation results'
    };
  }

  public getPlan(planId: string): ReasoningPlan | undefined {
    return this.plans.get(planId);
  }

  public getAllPlans(): ReasoningPlan[] {
    return Array.from(this.plans.values());
  }

  public updatePlan(planId: string, updates: Partial<ReasoningPlan>): boolean {
    const plan = this.plans.get(planId);
    if (!plan) return false;

    Object.assign(plan, updates);
    plan.updatedAt = new Date();
    return true;
  }

  public deletePlan(planId: string): boolean {
    return this.plans.delete(planId);
  }

  public getPlanStats(): any {
    const plans = this.getAllPlans();
    return {
      total: plans.length,
      draft: plans.filter(p => p.status === 'draft').length,
      approved: plans.filter(p => p.status === 'approved').length,
      executing: plans.filter(p => p.status === 'executing').length,
      completed: plans.filter(p => p.status === 'completed').length,
      failed: plans.filter(p => p.status === 'failed').length,
      cancelled: plans.filter(p => p.status === 'cancelled').length
    };
  }

  private generateId(): string {
    return `plan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  public isReady(): boolean {
    return this.isInitialized;
  }
}
