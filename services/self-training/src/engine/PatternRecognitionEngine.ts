/**
 * Pattern Recognition Engine - Autonomous pattern discovery and learning
 */

import { EventEmitter } from 'events';
import * as natural from 'natural';
import * as compromise from 'compromise';
import { v4 as uuidv4 } from 'uuid';

export interface RecognizedPattern {
  id: string;
  type: 'conversation' | 'behavior' | 'preference' | 'emotional' | 'cultural' | 'temporal';
  pattern: string;
  confidence: number;
  frequency: number;
  context: any;
  examples: string[];
  lastSeen: Date;
  improvements: number;
  metadata: {
    source: string;
    reliability: number;
    complexity: number;
    impact: number;
  };
}

export interface PatternCluster {
  id: string;
  patterns: RecognizedPattern[];
  centroid: number[];
  coherence: number;
  significance: number;
  insights: string[];
}

export interface BehavioralPattern {
  userId: string;
  timePatterns: Map<string, number>;
  interactionPatterns: Map<string, number>;
  preferencePatterns: Map<string, any>;
  emotionalPatterns: Map<string, number>;
  culturalPatterns: Map<string, number>;
}

export class PatternRecognitionEngine extends EventEmitter {
  private patterns: Map<string, RecognizedPattern>;
  private clusters: Map<string, PatternCluster>;
  private behavioralPatterns: Map<string, BehavioralPattern>;
  private trainingCore: any;
  private tokenizer: natural.WordTokenizer;
  private stemmer: natural.PorterStemmer;
  private patternHistory: any[];
  private lastAnalysisTime: Date;

  constructor() {
    super();
    this.patterns = new Map();
    this.clusters = new Map();
    this.behavioralPatterns = new Map();
    this.tokenizer = new natural.WordTokenizer();
    this.stemmer = natural.PorterStemmer;
    this.patternHistory = [];
    this.lastAnalysisTime = new Date();
  }

  public setTrainingCore(trainingCore: any): void {
    this.trainingCore = trainingCore;
  }

  public async analyzePatterns(): Promise<RecognizedPattern[]> {
    console.log('🔍 Starting comprehensive pattern analysis...');
    
    const newPatterns: RecognizedPattern[] = [];

    try {
      // Analyze conversation patterns
      const conversationPatterns = await this.analyzeConversationPatterns();
      newPatterns.push(...conversationPatterns);

      // Analyze behavioral patterns
      const behavioralPatterns = await this.analyzeBehavioralPatterns();
      newPatterns.push(...behavioralPatterns);

      // Analyze emotional patterns
      const emotionalPatterns = await this.analyzeEmotionalPatterns();
      newPatterns.push(...emotionalPatterns);

      // Analyze cultural patterns
      const culturalPatterns = await this.analyzeCulturalPatterns();
      newPatterns.push(...culturalPatterns);

      // Analyze temporal patterns
      const temporalPatterns = await this.analyzeTemporalPatterns();
      newPatterns.push(...temporalPatterns);

      // Process and validate patterns
      const validatedPatterns = this.validatePatterns(newPatterns);
      
      // Store new patterns
      for (const pattern of validatedPatterns) {
        this.patterns.set(pattern.id, pattern);
        this.emit('patternDiscovered', pattern);
      }

      // Create pattern clusters
      await this.createPatternClusters();

      // Generate insights
      await this.generatePatternInsights();

      this.lastAnalysisTime = new Date();
      
      console.log(`✅ Pattern analysis completed: ${validatedPatterns.length} new patterns discovered`);
      
      return validatedPatterns;

    } catch (error) {
      console.error('❌ Pattern analysis failed:', error);
      throw error;
    }
  }

  private async analyzeConversationPatterns(): Promise<RecognizedPattern[]> {
    const patterns: RecognizedPattern[] = [];
    
    // Get conversation data from training core
    const conversations = await this.getConversationData();
    
    // Analyze input-output patterns
    const inputOutputMap = new Map<string, { outputs: string[]; quality: number[] }>();
    
    conversations.forEach(conv => {
      const inputKey = this.extractInputKey(conv.input);
      const existing = inputOutputMap.get(inputKey);
      
      if (existing) {
        existing.outputs.push(conv.output);
        existing.quality.push(conv.quality_score || 0.5);
      } else {
        inputOutputMap.set(inputKey, {
          outputs: [conv.output],
          quality: [conv.quality_score || 0.5]
        });
      }
    });

    // Create patterns from frequent input-output pairs
    inputOutputMap.forEach((data, inputKey) => {
      if (data.outputs.length > 3) {
        const avgQuality = data.quality.reduce((sum, q) => sum + q, 0) / data.quality.length;
        const confidence = Math.min(0.95, avgQuality * (data.outputs.length / 10));
        
        if (confidence > 0.6) {
          patterns.push({
            id: uuidv4(),
            type: 'conversation',
            pattern: `Input: ${inputKey} → Output: ${this.findMostCommonOutput(data.outputs)}`,
            confidence,
            frequency: data.outputs.length,
            context: {
              inputType: this.classifyInputType(inputKey),
              outputType: this.classifyOutputType(data.outputs[0]),
              avgQuality,
              examples: data.outputs.slice(0, 3)
            },
            examples: data.outputs.slice(0, 5),
            lastSeen: new Date(),
            improvements: 0,
            metadata: {
              source: 'conversation_analysis',
              reliability: confidence,
              complexity: this.calculateComplexity(inputKey),
              impact: avgQuality * data.outputs.length
            }
          });
        }
      }
    });

    return patterns;
  }

  private async analyzeBehavioralPatterns(): Promise<RecognizedPattern[]> {
    const patterns: RecognizedPattern[] = [];
    
    // Get behavioral data
    const behaviors = await this.getBehavioralData();
    
    // Analyze user interaction patterns
    const userPatterns = new Map<string, Map<string, number>>();
    
    behaviors.forEach(behavior => {
      const userId = behavior.userId || 'default';
      if (!userPatterns.has(userId)) {
        userPatterns.set(userId, new Map());
      }
      
      const userPattern = userPatterns.get(userId)!;
      const behaviorKey = this.normalizeBehavior(behavior.action);
      userPattern.set(behaviorKey, (userPattern.get(behaviorKey) || 0) + 1);
    });

    // Create behavioral patterns
    userPatterns.forEach((userPattern, userId) => {
      const topBehaviors = Array.from(userPattern.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      
      if (topBehaviors.length > 0) {
        const confidence = Math.min(0.9, topBehaviors[0][1] / 20);
        
        patterns.push({
          id: uuidv4(),
          type: 'behavior',
          pattern: `User ${userId} frequently: ${topBehaviors.map(b => b[0]).join(', ')}`,
          confidence,
          frequency: topBehaviors.reduce((sum, b) => sum + b[1], 0),
          context: {
            userId,
            topBehaviors: topBehaviors.map(b => ({ action: b[0], count: b[1] })),
            behaviorDiversity: userPattern.size
          },
          examples: topBehaviors.map(b => `${b[0]} (${b[1]} times)`),
          lastSeen: new Date(),
          improvements: 0,
          metadata: {
            source: 'behavioral_analysis',
            reliability: confidence,
            complexity: userPattern.size / 10,
            impact: topBehaviors[0][1] / 5
          }
        });
      }
    });

    return patterns;
  }

  private async analyzeEmotionalPatterns(): Promise<RecognizedPattern[]> {
    const patterns: RecognizedPattern[] = [];
    
    // Get emotional data
    const emotions = await this.getEmotionalData();
    
    // Analyze emotional triggers and responses
    const emotionalTriggers = new Map<string, { emotions: string[]; intensities: number[] }>();
    
    emotions.forEach(emotion => {
      const trigger = emotion.trigger || 'unknown';
      const existing = emotionalTriggers.get(trigger);
      
      if (existing) {
        existing.emotions.push(emotion.emotion);
        existing.intensities.push(emotion.intensity);
      } else {
        emotionalTriggers.set(trigger, {
          emotions: [emotion.emotion],
          intensities: [emotion.intensity]
        });
      }
    });

    // Create emotional patterns
    emotionalTriggers.forEach((data, trigger) => {
      if (data.emotions.length > 2) {
        const mostCommonEmotion = this.findMostCommonEmotion(data.emotions);
        const avgIntensity = data.intensities.reduce((sum, i) => sum + i, 0) / data.intensities.length;
        const confidence = Math.min(0.9, data.emotions.length / 10);
        
        patterns.push({
          id: uuidv4(),
          type: 'emotional',
          pattern: `Trigger: ${trigger} → Emotion: ${mostCommonEmotion} (intensity: ${avgIntensity.toFixed(1)})`,
          confidence,
          frequency: data.emotions.length,
          context: {
            trigger,
            primaryEmotion: mostCommonEmotion,
            avgIntensity,
            emotionalRange: this.calculateEmotionalRange(data.emotions),
            triggerType: this.classifyTriggerType(trigger)
          },
          examples: data.emotions.slice(0, 5),
          lastSeen: new Date(),
          improvements: 0,
          metadata: {
            source: 'emotional_analysis',
            reliability: confidence,
            complexity: data.emotions.length / 5,
            impact: avgIntensity * data.emotions.length
          }
        });
      }
    });

    return patterns;
  }

  private async analyzeCulturalPatterns(): Promise<RecognizedPattern[]> {
    const patterns: RecognizedPattern[] = [];
    
    // Get cultural data
    const culturalData = await this.getCulturalData();
    
    // Analyze language usage patterns
    const languagePatterns = new Map<string, { count: number; contexts: string[] }>();
    
    culturalData.forEach(data => {
      const language = data.language || 'unknown';
      const existing = languagePatterns.get(language);
      
      if (existing) {
        existing.count += 1;
        existing.contexts.push(data.context || 'general');
      } else {
        languagePatterns.set(language, {
          count: 1,
          contexts: [data.context || 'general']
        });
      }
    });

    // Create cultural patterns
    languagePatterns.forEach((data, language) => {
      if (data.count > 5) {
        const confidence = Math.min(0.9, data.count / 20);
        const commonContexts = this.findMostCommonContexts(data.contexts);
        
        patterns.push({
          id: uuidv4(),
          type: 'cultural',
          pattern: `Language: ${language} used in contexts: ${commonContexts.join(', ')}`,
          confidence,
          frequency: data.count,
          context: {
            language,
            contexts: commonContexts,
            usageDistribution: this.calculateUsageDistribution(data.contexts),
            culturalSignificance: this.assessCulturalSignificance(language, data.contexts)
          },
          examples: data.contexts.slice(0, 5),
          lastSeen: new Date(),
          improvements: 0,
          metadata: {
            source: 'cultural_analysis',
            reliability: confidence,
            complexity: data.contexts.length / 10,
            impact: data.count / 10
          }
        });
      }
    });

    return patterns;
  }

  private async analyzeTemporalPatterns(): Promise<RecognizedPattern[]> {
    const patterns: RecognizedPattern[] = [];
    
    // Get temporal data
    const temporalData = await this.getTemporalData();
    
    // Analyze time-based patterns
    const timePatterns = new Map<string, { counts: number[]; hours: number[] }>();
    
    temporalData.forEach(data => {
      const hour = new Date(data.timestamp).getHours();
      const dayType = this.getDayType(data.timestamp);
      const key = `${dayType}_${Math.floor(hour / 4)}`; // 6-hour blocks
      
      const existing = timePatterns.get(key);
      if (existing) {
        existing.counts.push(1);
        existing.hours.push(hour);
      } else {
        timePatterns.set(key, {
          counts: [1],
          hours: [hour]
        });
      }
    });

    // Create temporal patterns
    timePatterns.forEach((data, timeKey) => {
      if (data.counts.length > 10) {
        const confidence = Math.min(0.9, data.counts.length / 50);
        const avgHour = data.hours.reduce((sum, h) => sum + h, 0) / data.hours.length;
        
        patterns.push({
          id: uuidv4(),
          type: 'temporal',
          pattern: `Peak activity: ${timeKey} (avg hour: ${avgHour.toFixed(1)})`,
          confidence,
          frequency: data.counts.length,
          context: {
            timeBlock: timeKey,
            avgHour,
            activityLevel: data.counts.length,
            consistency: this.calculateConsistency(data.hours)
          },
          examples: data.hours.slice(0, 5).map(h => `Hour ${h}`),
          lastSeen: new Date(),
          improvements: 0,
          metadata: {
            source: 'temporal_analysis',
            reliability: confidence,
            complexity: 1,
            impact: data.counts.length / 20
          }
        });
      }
    });

    return patterns;
  }

  private validatePatterns(patterns: RecognizedPattern[]): RecognizedPattern[] {
    return patterns.filter(pattern => {
      // Filter out low-confidence patterns
      if (pattern.confidence < 0.5) return false;
      
      // Filter out patterns with too few examples
      if (pattern.frequency < 3) return false;
      
      // Check for pattern uniqueness
      const existingPattern = Array.from(this.patterns.values())
        .find(p => p.pattern === pattern.pattern);
      
      if (existingPattern) {
        // Update existing pattern instead of creating duplicate
        existingPattern.confidence = Math.max(existingPattern.confidence, pattern.confidence);
        existingPattern.frequency += pattern.frequency;
        existingPattern.lastSeen = new Date();
        return false;
      }
      
      return true;
    });
  }

  private async createPatternClusters(): Promise<void> {
    const allPatterns = Array.from(this.patterns.values());
    
    // Group patterns by type
    const patternGroups = new Map<string, RecognizedPattern[]>();
    
    allPatterns.forEach(pattern => {
      const type = pattern.type;
      if (!patternGroups.has(type)) {
        patternGroups.set(type, []);
      }
      patternGroups.get(type)!.push(pattern);
    });

    // Create clusters for each type
    patternGroups.forEach((patterns, type) => {
      if (patterns.length > 2) {
        const cluster = this.createCluster(patterns, type);
        this.clusters.set(cluster.id, cluster);
      }
    });
  }

  private createCluster(patterns: RecognizedPattern[], type: string): PatternCluster {
    const clusterId = uuidv4();
    
    // Calculate cluster metrics
    const avgConfidence = patterns.reduce((sum, p) => sum + p.confidence, 0) / patterns.length;
    const totalFrequency = patterns.reduce((sum, p) => sum + p.frequency, 0);
    const coherence = this.calculateCoherence(patterns);
    const significance = avgConfidence * totalFrequency / patterns.length;
    
    // Generate insights
    const insights = this.generateClusterInsights(patterns, type);
    
    return {
      id: clusterId,
      patterns,
      centroid: this.calculateCentroid(patterns),
      coherence,
      significance,
      insights
    };
  }

  private async generatePatternInsights(): Promise<void> {
    const insights: string[] = [];
    
    // Generate insights from clusters
    this.clusters.forEach(cluster => {
      if (cluster.significance > 0.7) {
        insights.push(`High-significance ${cluster.patterns[0].type} cluster: ${cluster.insights.join(', ')}`);
      }
    });

    // Generate insights from individual patterns
    const highConfidencePatterns = Array.from(this.patterns.values())
      .filter(p => p.confidence > 0.8)
      .sort((a, b) => b.frequency - a.frequency)
      .slice(0, 5);

    highConfidencePatterns.forEach(pattern => {
      insights.push(`Strong pattern: ${pattern.pattern} (confidence: ${pattern.confidence.toFixed(2)}, frequency: ${pattern.frequency})`);
    });

    // Store insights
    this.patternHistory.push({
      timestamp: new Date(),
      insights,
      patternCount: this.patterns.size,
      clusterCount: this.clusters.size
    });

    this.emit('insightsGenerated', { insights, patternCount: this.patterns.size });
  }

  public async runScheduledAnalysis(): Promise<void> {
    console.log('🔍 Running scheduled pattern analysis...');
    await this.analyzePatterns();
  }

  // Helper methods
  private extractInputKey(input: string): string {
    const tokens = this.tokenizer.tokenize(input.toLowerCase());
    const stemmedTokens = tokens.map(token => this.stemmer.stem(token));
    return stemmedTokens.slice(0, 5).join(' '); // First 5 words
  }

  private findMostCommonOutput(outputs: string[]): string {
    const counts = new Map<string, number>();
    outputs.forEach(output => {
      counts.set(output, (counts.get(output) || 0) + 1);
    });
    
    let mostCommon = '';
    let maxCount = 0;
    counts.forEach((count, output) => {
      if (count > maxCount) {
        maxCount = count;
        mostCommon = output;
      }
    });
    
    return mostCommon;
  }

  private findMostCommonEmotion(emotions: string[]): string {
    const counts = new Map<string, number>();
    emotions.forEach(emotion => {
      counts.set(emotion, (counts.get(emotion) || 0) + 1);
    });
    
    let mostCommon = '';
    let maxCount = 0;
    counts.forEach((count, emotion) => {
      if (count > maxCount) {
        maxCount = count;
        mostCommon = emotion;
      }
    });
    
    return mostCommon;
  }

  private findMostCommonContexts(contexts: string[]): string[] {
    const counts = new Map<string, number>();
    contexts.forEach(context => {
      counts.set(context, (counts.get(context) || 0) + 1);
    });
    
    return Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([context]) => context);
  }

  private classifyInputType(input: string): string {
    if (input.includes('?')) return 'question';
    if (input.includes('please') || input.includes('can you')) return 'request';
    if (input.includes('thank')) return 'gratitude';
    if (input.includes('hello') || input.includes('hi')) return 'greeting';
    return 'statement';
  }

  private classifyOutputType(output: string): string {
    if (output.includes('?')) return 'question';
    if (output.includes('I will') || output.includes('I can')) return 'action';
    if (output.includes('I understand') || output.includes('I see')) return 'acknowledgment';
    return 'response';
  }

  private normalizeBehavior(action: string): string {
    return action.toLowerCase().replace(/[^a-z\s]/g, '').trim();
  }

  private calculateComplexity(input: string): number {
    const words = input.split(' ').length;
    const sentences = input.split(/[.!?]+/).length;
    return Math.min(1, words / 20 + sentences / 5);
  }

  private calculateEmotionalRange(emotions: string[]): number {
    const uniqueEmotions = new Set(emotions);
    return uniqueEmotions.size / 10; // Normalize to 0-1
  }

  private classifyTriggerType(trigger: string): string {
    if (trigger.includes('success') || trigger.includes('completed')) return 'positive';
    if (trigger.includes('error') || trigger.includes('failed')) return 'negative';
    if (trigger.includes('question') || trigger.includes('help')) return 'support';
    return 'neutral';
  }

  private calculateUsageDistribution(contexts: string[]): Map<string, number> {
    const distribution = new Map<string, number>();
    contexts.forEach(context => {
      distribution.set(context, (distribution.get(context) || 0) + 1);
    });
    return distribution;
  }

  private assessCulturalSignificance(language: string, contexts: string[]): number {
    if (language === 'sinhala') return 0.9;
    if (language === 'english') return 0.7;
    if (contexts.includes('formal') || contexts.includes('business')) return 0.8;
    return 0.5;
  }

  private getDayType(timestamp: string): string {
    const date = new Date(timestamp);
    const day = date.getDay();
    return day === 0 || day === 6 ? 'weekend' : 'weekday';
  }

  private calculateConsistency(hours: number[]): number {
    const variance = this.calculateVariance(hours);
    return Math.max(0, 1 - variance / 100); // Higher consistency = lower variance
  }

  private calculateVariance(numbers: number[]): number {
    const mean = numbers.reduce((sum, num) => sum + num, 0) / numbers.length;
    const variance = numbers.reduce((sum, num) => sum + Math.pow(num - mean, 2), 0) / numbers.length;
    return variance;
  }

  private calculateCoherence(patterns: RecognizedPattern[]): number {
    const avgConfidence = patterns.reduce((sum, p) => sum + p.confidence, 0) / patterns.length;
    const confidenceVariance = patterns.reduce((sum, p) => sum + Math.pow(p.confidence - avgConfidence, 2), 0) / patterns.length;
    return Math.max(0, 1 - confidenceVariance);
  }

  private calculateCentroid(patterns: RecognizedPattern[]): number[] {
    // Simple centroid calculation based on confidence and frequency
    const avgConfidence = patterns.reduce((sum, p) => sum + p.confidence, 0) / patterns.length;
    const avgFrequency = patterns.reduce((sum, p) => sum + p.frequency, 0) / patterns.length;
    const avgComplexity = patterns.reduce((sum, p) => sum + p.metadata.complexity, 0) / patterns.length;
    
    return [avgConfidence, avgFrequency, avgComplexity];
  }

  private generateClusterInsights(patterns: RecognizedPattern[], type: string): string[] {
    const insights: string[] = [];
    
    const avgConfidence = patterns.reduce((sum, p) => sum + p.confidence, 0) / patterns.length;
    const totalFrequency = patterns.reduce((sum, p) => sum + p.frequency, 0);
    
    insights.push(`${type} patterns show ${avgConfidence.toFixed(2)} average confidence`);
    insights.push(`Total frequency: ${totalFrequency} interactions`);
    
    if (type === 'conversation') {
      const inputTypes = new Set(patterns.map(p => p.context.inputType));
      insights.push(`Covers ${inputTypes.size} different input types`);
    }
    
    if (type === 'emotional') {
      const emotions = new Set(patterns.map(p => p.context.primaryEmotion));
      insights.push(`Recognizes ${emotions.size} different emotions`);
    }
    
    return insights;
  }

  // Data access methods (would connect to actual data sources)
  private async getConversationData(): Promise<any[]> {
    // This would connect to the training core's database
    return [];
  }

  private async getBehavioralData(): Promise<any[]> {
    // This would connect to behavioral tracking data
    return [];
  }

  private async getEmotionalData(): Promise<any[]> {
    // This would connect to emotional tracking data
    return [];
  }

  private async getCulturalData(): Promise<any[]> {
    // This would connect to cultural usage data
    return [];
  }

  private async getTemporalData(): Promise<any[]> {
    // This would connect to temporal tracking data
    return [];
  }

  // Public getters
  public getPatternCount(): number {
    return this.patterns.size;
  }

  public getPatterns(): Map<string, RecognizedPattern> {
    return new Map(this.patterns);
  }

  public getClusters(): Map<string, PatternCluster> {
    return new Map(this.clusters);
  }

  public getPatternHistory(): any[] {
    return [...this.patternHistory];
  }

  public getLastAnalysisTime(): Date {
    return this.lastAnalysisTime;
  }
}
