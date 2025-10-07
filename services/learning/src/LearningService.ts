/**
 * JarvisX Learning Service
 * Autonomous learning and adaptation capabilities
 */

import OpenAI from 'openai';
import fs from 'fs-extra';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

export interface LearningPattern {
  id: string;
  type: 'command' | 'workflow' | 'preference' | 'behavior' | 'schedule';
  pattern: string;
  context: any;
  frequency: number;
  successRate: number;
  lastUsed: Date;
  createdAt: Date;
  confidence: number;
  metadata: any;
}

export interface LearningInsight {
  id: string;
  type: 'automation' | 'optimization' | 'prediction' | 'recommendation';
  title: string;
  description: string;
  confidence: number;
  impact: 'low' | 'medium' | 'high';
  category: string;
  data: any;
  createdAt: Date;
  status: 'pending' | 'applied' | 'rejected' | 'expired';
}

export interface UserBehavior {
  userId: string;
  commandPatterns: Map<string, number>;
  timePatterns: Map<string, number>;
  contextPatterns: Map<string, number>;
  successPatterns: Map<string, number>;
  failurePatterns: Map<string, number>;
  preferences: Map<string, any>;
  lastUpdated: Date;
}

export interface LearningMetrics {
  totalPatterns: number;
  activePatterns: number;
  successRate: number;
  automationRate: number;
  userSatisfaction: number;
  learningVelocity: number;
  adaptationScore: number;
}

export class LearningService {
  private openai: OpenAI;
  private patterns: Map<string, LearningPattern> = new Map();
  private insights: Map<string, LearningInsight> = new Map();
  private userBehaviors: Map<string, UserBehavior> = new Map();
  private isInitialized: boolean = false;
  private dataPath: string;

  constructor() {
    this.dataPath = process.env.LEARNING_DATA_PATH || './data/learning';
    this.initializeOpenAI();
    this.initializeDataDirectory();
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
      console.log('✅ Learning Service OpenAI client initialized');
      
    } catch (error) {
      console.error('❌ Failed to initialize Learning Service OpenAI client:', error);
      this.isInitialized = false;
    }
  }

  private async initializeDataDirectory(): Promise<void> {
    try {
      await fs.ensureDir(this.dataPath);
      await this.loadStoredData();
      console.log('✅ Learning data directory initialized');
    } catch (error) {
      console.error('❌ Failed to initialize learning data directory:', error);
    }
  }

  private async loadStoredData(): Promise<void> {
    try {
      // Load patterns
      const patternsFile = path.join(this.dataPath, 'patterns.json');
      if (await fs.pathExists(patternsFile)) {
        const patternsData = await fs.readJson(patternsFile);
        patternsData.forEach((pattern: any) => {
          this.patterns.set(pattern.id, {
            ...pattern,
            lastUsed: new Date(pattern.lastUsed),
            createdAt: new Date(pattern.createdAt)
          });
        });
      }

      // Load insights
      const insightsFile = path.join(this.dataPath, 'insights.json');
      if (await fs.pathExists(insightsFile)) {
        const insightsData = await fs.readJson(insightsFile);
        insightsData.forEach((insight: any) => {
          this.insights.set(insight.id, {
            ...insight,
            createdAt: new Date(insight.createdAt)
          });
        });
      }

      // Load user behaviors
      const behaviorsFile = path.join(this.dataPath, 'behaviors.json');
      if (await fs.pathExists(behaviorsFile)) {
        const behaviorsData = await fs.readJson(behaviorsFile);
        behaviorsData.forEach((behavior: any) => {
          this.userBehaviors.set(behavior.userId, {
            ...behavior,
            commandPatterns: new Map(behavior.commandPatterns),
            timePatterns: new Map(behavior.timePatterns),
            contextPatterns: new Map(behavior.contextPatterns),
            successPatterns: new Map(behavior.successPatterns),
            failurePatterns: new Map(behavior.failurePatterns),
            preferences: new Map(behavior.preferences),
            lastUpdated: new Date(behavior.lastUpdated)
          });
        });
      }

      console.log('✅ Learning data loaded successfully');
    } catch (error) {
      console.error('❌ Failed to load stored data:', error);
    }
  }

  private async saveStoredData(): Promise<void> {
    try {
      // Save patterns
      const patternsData = Array.from(this.patterns.values()).map(pattern => ({
        ...pattern,
        lastUsed: pattern.lastUsed.toISOString(),
        createdAt: pattern.createdAt.toISOString()
      }));
      await fs.writeJson(path.join(this.dataPath, 'patterns.json'), patternsData, { spaces: 2 });

      // Save insights
      const insightsData = Array.from(this.insights.values()).map(insight => ({
        ...insight,
        createdAt: insight.createdAt.toISOString()
      }));
      await fs.writeJson(path.join(this.dataPath, 'insights.json'), insightsData, { spaces: 2 });

      // Save user behaviors
      const behaviorsData = Array.from(this.userBehaviors.values()).map(behavior => ({
        ...behavior,
        commandPatterns: Array.from(behavior.commandPatterns.entries()),
        timePatterns: Array.from(behavior.timePatterns.entries()),
        contextPatterns: Array.from(behavior.contextPatterns.entries()),
        successPatterns: Array.from(behavior.successPatterns.entries()),
        failurePatterns: Array.from(behavior.failurePatterns.entries()),
        preferences: Array.from(behavior.preferences.entries()),
        lastUpdated: behavior.lastUpdated.toISOString()
      }));
      await fs.writeJson(path.join(this.dataPath, 'behaviors.json'), behaviorsData, { spaces: 2 });

      console.log('✅ Learning data saved successfully');
    } catch (error) {
      console.error('❌ Failed to save stored data:', error);
    }
  }

  public async learnFromInteraction(
    userId: string,
    command: string,
    context: any,
    success: boolean,
    feedback?: number
  ): Promise<void> {
    try {
      console.log(`🧠 Learning from interaction: ${command} (${success ? 'success' : 'failure'})`);

      // Update user behavior
      await this.updateUserBehavior(userId, command, context, success, feedback);

      // Detect patterns
      await this.detectPatterns(userId, command, context, success);

      // Generate insights
      await this.generateInsights(userId);

      // Save data
      await this.saveStoredData();

    } catch (error) {
      console.error('❌ Learning from interaction failed:', error);
    }
  }

  private async updateUserBehavior(
    userId: string,
    command: string,
    context: any,
    success: boolean,
    feedback?: number
  ): Promise<void> {
    let behavior = this.userBehaviors.get(userId);
    
    if (!behavior) {
      behavior = {
        userId,
        commandPatterns: new Map(),
        timePatterns: new Map(),
        contextPatterns: new Map(),
        successPatterns: new Map(),
        failurePatterns: new Map(),
        preferences: new Map(),
        lastUpdated: new Date()
      };
      this.userBehaviors.set(userId, behavior);
    }

    // Update command patterns
    const commandCount = behavior.commandPatterns.get(command) || 0;
    behavior.commandPatterns.set(command, commandCount + 1);

    // Update time patterns
    const hour = new Date().getHours();
    const timeKey = `${hour}:00`;
    const timeCount = behavior.timePatterns.get(timeKey) || 0;
    behavior.timePatterns.set(timeKey, timeCount + 1);

    // Update context patterns
    const contextKey = JSON.stringify(context);
    const contextCount = behavior.contextPatterns.get(contextKey) || 0;
    behavior.contextPatterns.set(contextKey, contextCount + 1);

    // Update success/failure patterns
    if (success) {
      const successCount = behavior.successPatterns.get(command) || 0;
      behavior.successPatterns.set(command, successCount + 1);
    } else {
      const failureCount = behavior.failurePatterns.get(command) || 0;
      behavior.failurePatterns.set(command, failureCount + 1);
    }

    // Update preferences based on feedback
    if (feedback !== undefined) {
      behavior.preferences.set('satisfaction', feedback);
    }

    behavior.lastUpdated = new Date();
  }

  private async detectPatterns(
    userId: string,
    command: string,
    context: any,
    success: boolean
  ): Promise<void> {
    try {
      const behavior = this.userBehaviors.get(userId);
      if (!behavior) return;

      // Detect command frequency patterns
      const commandFrequency = behavior.commandPatterns.get(command) || 0;
      if (commandFrequency >= 3) {
        const patternId = `cmd_${command}_${userId}`;
        let pattern = this.patterns.get(patternId);
        
        if (!pattern) {
          pattern = {
            id: patternId,
            type: 'command',
            pattern: command,
            context,
            frequency: commandFrequency,
            successRate: success ? 100 : 0,
            lastUsed: new Date(),
            createdAt: new Date(),
            confidence: 0.5,
            metadata: { userId }
          };
          this.patterns.set(patternId, pattern);
        } else {
          pattern.frequency = commandFrequency;
          pattern.lastUsed = new Date();
          pattern.confidence = Math.min(1.0, pattern.confidence + 0.1);
        }
      }

      // Detect time-based patterns
      const hour = new Date().getHours();
      const timeKey = `${hour}:00`;
      const timeFrequency = behavior.timePatterns.get(timeKey) || 0;
      
      if (timeFrequency >= 5) {
        const patternId = `time_${hour}_${userId}`;
        let pattern = this.patterns.get(patternId);
        
        if (!pattern) {
          pattern = {
            id: patternId,
            type: 'schedule',
            pattern: `User active at ${timeKey}`,
            context: { hour, userId },
            frequency: timeFrequency,
            successRate: 100,
            lastUsed: new Date(),
            createdAt: new Date(),
            confidence: 0.6,
            metadata: { userId, hour }
          };
          this.patterns.set(patternId, pattern);
        }
      }

      // Detect workflow patterns
      const recentCommands = Array.from(behavior.commandPatterns.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([cmd]) => cmd);

      if (recentCommands.length >= 3) {
        const workflowPattern = recentCommands.join(' -> ');
        const patternId = `workflow_${workflowPattern}_${userId}`;
        
        if (!this.patterns.has(patternId)) {
          const pattern: LearningPattern = {
            id: patternId,
            type: 'workflow',
            pattern: workflowPattern,
            context: { commands: recentCommands },
            frequency: 1,
            successRate: 100,
            lastUsed: new Date(),
            createdAt: new Date(),
            confidence: 0.7,
            metadata: { userId, commands: recentCommands }
          };
          this.patterns.set(patternId, pattern);
        }
      }

    } catch (error) {
      console.error('❌ Pattern detection failed:', error);
    }
  }

  public async generateInsights(userId: string): Promise<LearningInsight[]> {
    if (!this.isInitialized) {
      throw new Error('Learning Service not initialized');
    }

    try {
      console.log(`💡 Generating insights for user: ${userId}`);

      const behavior = this.userBehaviors.get(userId);
      if (!behavior) return [];

      const patterns = Array.from(this.patterns.values())
        .filter(p => p.metadata.userId === userId);

      const prompt = `Analyze the following user behavior patterns and generate actionable insights.

User Behavior Data:
- Command Patterns: ${JSON.stringify(Array.from(behavior.commandPatterns.entries()))}
- Time Patterns: ${JSON.stringify(Array.from(behavior.timePatterns.entries()))}
- Success Patterns: ${JSON.stringify(Array.from(behavior.successPatterns.entries()))}
- Failure Patterns: ${JSON.stringify(Array.from(behavior.failurePatterns.entries()))}

Detected Patterns:
${patterns.map(p => `- ${p.type}: ${p.pattern} (frequency: ${p.frequency}, confidence: ${p.confidence})`).join('\n')}

Generate insights for:
1. Automation opportunities
2. Workflow optimizations
3. Predictive suggestions
4. User experience improvements

Respond in JSON format:
{
  "insights": [
    {
      "type": "automation",
      "title": "Automate Morning Routine",
      "description": "User consistently runs these commands at 9 AM",
      "confidence": 85,
      "impact": "high",
      "category": "productivity",
      "data": {
        "commands": ["open_chrome", "check_email", "open_calendar"],
        "time": "09:00",
        "frequency": 15
      }
    }
  ]
}`;

      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an AI learning analyst. Generate actionable insights from user behavior patterns."
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
      const result = JSON.parse(content);

      const insights: LearningInsight[] = result.insights.map((insight: any) => ({
        id: uuidv4(),
        type: insight.type,
        title: insight.title,
        description: insight.description,
        confidence: insight.confidence,
        impact: insight.impact,
        category: insight.category,
        data: insight.data,
        createdAt: new Date(),
        status: 'pending'
      }));

      // Store insights
      insights.forEach(insight => {
        this.insights.set(insight.id, insight);
      });

      console.log(`✅ Generated ${insights.length} insights for user ${userId}`);

      return insights;

    } catch (error) {
      console.error('❌ Insight generation failed:', error);
      throw error;
    }
  }

  public async getPredictions(userId: string, context: any = {}): Promise<{
    nextCommands: string[];
    optimalTime: string;
    suggestions: string[];
    confidence: number;
  }> {
    try {
      console.log(`🔮 Generating predictions for user: ${userId}`);

      const behavior = this.userBehaviors.get(userId);
      if (!behavior) {
        return {
          nextCommands: [],
          optimalTime: '',
          suggestions: [],
          confidence: 0
        };
      }

      // Get most frequent commands
      const commandFrequencies = Array.from(behavior.commandPatterns.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([cmd]) => cmd);

      // Get optimal time based on patterns
      const timeFrequencies = Array.from(behavior.timePatterns.entries())
        .sort((a, b) => b[1] - a[1]);
      const optimalTime = timeFrequencies.length > 0 ? timeFrequencies[0][0] : '';

      // Generate suggestions based on context
      const suggestions = await this.generateContextualSuggestions(userId, context);

      const confidence = this.calculatePredictionConfidence(behavior);

      return {
        nextCommands: commandFrequencies,
        optimalTime,
        suggestions,
        confidence
      };

    } catch (error) {
      console.error('❌ Prediction generation failed:', error);
      throw error;
    }
  }

  private async generateContextualSuggestions(userId: string, context: any): Promise<string[]> {
    // This would use AI to generate contextual suggestions
    // For now, return basic suggestions based on patterns
    const behavior = this.userBehaviors.get(userId);
    if (!behavior) return [];

    const suggestions: string[] = [];
    
    // Suggest based on time of day
    const hour = new Date().getHours();
    if (hour >= 9 && hour <= 17) {
      suggestions.push('Check email', 'Open calendar', 'Review tasks');
    } else if (hour >= 18 && hour <= 22) {
      suggestions.push('Close work apps', 'Open entertainment', 'Check social media');
    }

    // Suggest based on recent commands
    const recentCommands = Array.from(behavior.commandPatterns.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([cmd]) => cmd);

    if (recentCommands.includes('open_chrome')) {
      suggestions.push('Search for something', 'Check news', 'Open social media');
    }

    return suggestions.slice(0, 3);
  }

  private calculatePredictionConfidence(behavior: UserBehavior): number {
    const totalCommands = Array.from(behavior.commandPatterns.values())
      .reduce((sum, count) => sum + count, 0);
    
    const uniqueCommands = behavior.commandPatterns.size;
    
    if (totalCommands === 0) return 0;
    
    // Higher confidence with more data and patterns
    const dataConfidence = Math.min(1.0, totalCommands / 50);
    const patternConfidence = Math.min(1.0, uniqueCommands / 10);
    
    return (dataConfidence + patternConfidence) / 2;
  }

  public getLearningMetrics(): LearningMetrics {
    const totalPatterns = this.patterns.size;
    const activePatterns = Array.from(this.patterns.values())
      .filter(p => p.confidence > 0.5).length;
    
    const totalSuccesses = Array.from(this.patterns.values())
      .reduce((sum, p) => sum + (p.successRate * p.frequency), 0);
    const totalAttempts = Array.from(this.patterns.values())
      .reduce((sum, p) => sum + p.frequency, 0);
    const successRate = totalAttempts > 0 ? totalSuccesses / totalAttempts : 0;
    
    const automationRate = activePatterns / Math.max(totalPatterns, 1);
    const userSatisfaction = this.calculateAverageSatisfaction();
    const learningVelocity = this.calculateLearningVelocity();
    const adaptationScore = this.calculateAdaptationScore();

    return {
      totalPatterns,
      activePatterns,
      successRate: Math.round(successRate * 100),
      automationRate: Math.round(automationRate * 100),
      userSatisfaction: Math.round(userSatisfaction),
      learningVelocity: Math.round(learningVelocity),
      adaptationScore: Math.round(adaptationScore)
    };
  }

  private calculateAverageSatisfaction(): number {
    const satisfactions = Array.from(this.userBehaviors.values())
      .map(b => b.preferences.get('satisfaction'))
      .filter(s => s !== undefined);
    
    if (satisfactions.length === 0) return 50; // Default neutral
    
    return satisfactions.reduce((sum, s) => sum + s, 0) / satisfactions.length;
  }

  private calculateLearningVelocity(): number {
    // Calculate how quickly new patterns are being learned
    const now = new Date();
    const recentPatterns = Array.from(this.patterns.values())
      .filter(p => (now.getTime() - p.createdAt.getTime()) < 7 * 24 * 60 * 60 * 1000); // Last 7 days
    
    return recentPatterns.length;
  }

  private calculateAdaptationScore(): number {
    // Calculate how well the system adapts to user behavior
    const patterns = Array.from(this.patterns.values());
    const highConfidencePatterns = patterns.filter(p => p.confidence > 0.8).length;
    const totalPatterns = patterns.length;
    
    if (totalPatterns === 0) return 0;
    
    return (highConfidencePatterns / totalPatterns) * 100;
  }

  public getPatterns(userId?: string): LearningPattern[] {
    if (userId) {
      return Array.from(this.patterns.values())
        .filter(p => p.metadata.userId === userId);
    }
    return Array.from(this.patterns.values());
  }

  public getInsights(userId?: string): LearningInsight[] {
    if (userId) {
      return Array.from(this.insights.values())
        .filter(i => i.data.userId === userId);
    }
    return Array.from(this.insights.values());
  }

  public isReady(): boolean {
    return this.isInitialized;
  }
}
