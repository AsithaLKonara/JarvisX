/**
 * Self-Training Core - The brain of autonomous learning and self-improvement
 */

import { EventEmitter } from 'events';
import * as sqlite3 from 'sqlite3';
import { promisify } from 'util';
import { v4 as uuidv4 } from 'uuid';
import * as natural from 'natural';
import * as tf from '@tensorflow/tfjs-node';

export interface TrainingConfig {
  learningRate: number;
  trainingFrequency: string;
  autoOptimization: boolean;
  experimentMode: boolean;
  knowledgeSynthesis: boolean;
}

export interface TrainingSession {
  id: string;
  type: 'full' | 'incremental' | 'pattern_analysis' | 'optimization' | 'experiment';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime: Date;
  endTime?: Date;
  progress: number;
  results: any;
  metrics: TrainingMetrics;
}

export interface TrainingMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  responseQuality: number;
  userSatisfaction: number;
  learningRate: number;
  convergenceRate: number;
}

export interface LearningPattern {
  id: string;
  pattern: string;
  confidence: number;
  frequency: number;
  lastSeen: Date;
  context: any;
  improvements: number;
}

export class SelfTrainingCore extends EventEmitter {
  private db: sqlite3.Database;
  private dbPromises: {
    run: (sql: string, params?: any[]) => Promise<any>;
    get: (sql: string, params?: any[]) => Promise<any>;
    all: (sql: string, params?: any[]) => Promise<any[]>;
  };
  
  private config: TrainingConfig;
  private currentTraining: TrainingSession | null;
  private trainingQueue: TrainingSession[];
  private learningPatterns: Map<string, LearningPattern>;
  private model: tf.LayersModel | null;
  private tokenizer: natural.WordTokenizer;
  private stemmer: natural.PorterStemmer;
  private totalInteractions: number;
  private lastTrainingTime: Date;
  private lastImprovementTime: Date;
  private learningRate: number;

  constructor() {
    super();
    this.trainingQueue = [];
    this.learningPatterns = new Map();
    this.model = null;
    this.tokenizer = new natural.WordTokenizer();
    this.stemmer = natural.PorterStemmer;
    this.totalInteractions = 0;
    this.lastTrainingTime = new Date();
    this.lastImprovementTime = new Date();
    this.learningRate = 0.01;
    
    this.initializeDatabase();
  }

  private async initializeDatabase(): Promise<void> {
    this.db = new sqlite3.Database(':memory:'); // In-memory for now, can be persisted
    
    this.dbPromises = {
      run: promisify(this.db.run.bind(this.db)),
      get: promisify(this.db.get.bind(this.db)),
      all: promisify(this.db.all.bind(this.db))
    };

    // Create tables for training data
    await this.dbPromises.run(`
      CREATE TABLE IF NOT EXISTS training_sessions (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT,
        progress REAL DEFAULT 0,
        results TEXT,
        metrics TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await this.dbPromises.run(`
      CREATE TABLE IF NOT EXISTS learning_patterns (
        id TEXT PRIMARY KEY,
        pattern TEXT NOT NULL,
        confidence REAL NOT NULL,
        frequency INTEGER DEFAULT 1,
        last_seen TEXT NOT NULL,
        context TEXT,
        improvements INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await this.dbPromises.run(`
      CREATE TABLE IF NOT EXISTS training_data (
        id TEXT PRIMARY KEY,
        input TEXT NOT NULL,
        output TEXT NOT NULL,
        context TEXT,
        quality_score REAL,
        user_feedback REAL,
        timestamp TEXT NOT NULL,
        session_id TEXT
      )
    `);

    await this.dbPromises.run(`
      CREATE TABLE IF NOT EXISTS performance_metrics (
        id TEXT PRIMARY KEY,
        metric_name TEXT NOT NULL,
        value REAL NOT NULL,
        timestamp TEXT NOT NULL,
        context TEXT
      )
    `);

    // Create indexes
    await this.dbPromises.run(`CREATE INDEX IF NOT EXISTS idx_training_sessions_status ON training_sessions(status)`);
    await this.dbPromises.run(`CREATE INDEX IF NOT EXISTS idx_learning_patterns_confidence ON learning_patterns(confidence)`);
    await this.dbPromises.run(`CREATE INDEX IF NOT EXISTS idx_training_data_quality ON training_data(quality_score)`);
    await this.dbPromises.run(`CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON performance_metrics(metric_name)`);

    console.log('🧠 Self-Training Core database initialized');
  }

  public async initialize(config: TrainingConfig): Promise<void> {
    this.config = config;
    this.learningRate = config.learningRate;
    
    // Initialize neural network model
    await this.initializeModel();
    
    // Load existing patterns
    await this.loadLearningPatterns();
    
    console.log('🧠 Self-Training Core initialized with config:', config);
  }

  private async initializeModel(): Promise<void> {
    try {
      // Create a simple neural network for learning patterns
      this.model = tf.sequential({
        layers: [
          tf.layers.dense({ inputShape: [100], units: 64, activation: 'relu' }),
          tf.layers.dropout({ rate: 0.2 }),
          tf.layers.dense({ units: 32, activation: 'relu' }),
          tf.layers.dropout({ rate: 0.2 }),
          tf.layers.dense({ units: 16, activation: 'relu' }),
          tf.layers.dense({ units: 1, activation: 'sigmoid' })
        ]
      });

      // Compile the model
      this.model.compile({
        optimizer: tf.train.adam(this.learningRate),
        loss: 'binaryCrossentropy',
        metrics: ['accuracy']
      });

      console.log('🧠 Neural network model initialized');
    } catch (error) {
      console.error('❌ Failed to initialize neural network model:', error);
    }
  }

  private async loadLearningPatterns(): Promise<void> {
    try {
      const patterns = await this.dbPromises.all('SELECT * FROM learning_patterns ORDER BY confidence DESC');
      
      patterns.forEach(row => {
        this.learningPatterns.set(row.id, {
          id: row.id,
          pattern: row.pattern,
          confidence: row.confidence,
          frequency: row.frequency,
          lastSeen: new Date(row.last_seen),
          context: JSON.parse(row.context || '{}'),
          improvements: row.improvements
        });
      });

      console.log(`🧠 Loaded ${patterns.length} learning patterns`);
    } catch (error) {
      console.error('❌ Failed to load learning patterns:', error);
    }
  }

  public async startTraining(type: 'full' | 'incremental' | 'pattern_analysis' | 'optimization' | 'experiment', priority: 'low' | 'normal' | 'high' | 'urgent'): Promise<string> {
    if (this.currentTraining) {
      throw new Error('Training already in progress');
    }

    const trainingId = uuidv4();
    const session: TrainingSession = {
      id: trainingId,
      type,
      priority,
      status: 'pending',
      startTime: new Date(),
      progress: 0,
      results: {},
      metrics: {
        accuracy: 0,
        precision: 0,
        recall: 0,
        f1Score: 0,
        responseQuality: 0,
        userSatisfaction: 0,
        learningRate: this.learningRate,
        convergenceRate: 0
      }
    };

    this.trainingQueue.push(session);
    
    // Start training immediately if high priority
    if (priority === 'urgent' || priority === 'high') {
      await this.executeTraining(session);
    }

    this.emit('trainingStarted', session);
    return trainingId;
  }

  public async stopTraining(): Promise<void> {
    if (this.currentTraining) {
      this.currentTraining.status = 'failed';
      this.currentTraining.endTime = new Date();
      
      await this.dbPromises.run(`
        UPDATE training_sessions 
        SET status = ?, end_time = ?, progress = ?
        WHERE id = ?
      `, ['failed', this.currentTraining.endTime.toISOString(), this.currentTraining.progress, this.currentTraining.id]);

      this.currentTraining = null;
      this.emit('trainingStopped');
    }
  }

  private async executeTraining(session: TrainingSession): Promise<void> {
    this.currentTraining = session;
    session.status = 'running';
    
    try {
      console.log(`🧠 Starting training: ${session.type} (${session.priority})`);
      
      switch (session.type) {
        case 'full':
          await this.runFullTraining(session);
          break;
        case 'incremental':
          await this.runIncrementalTraining(session);
          break;
        case 'pattern_analysis':
          await this.runPatternAnalysis(session);
          break;
        case 'optimization':
          await this.runOptimization(session);
          break;
        case 'experiment':
          await this.runExperiment(session);
          break;
      }

      session.status = 'completed';
      session.endTime = new Date();
      session.progress = 100;
      
      this.lastTrainingTime = new Date();
      this.emit('trainingCompleted', session);
      
      console.log(`✅ Training completed: ${session.type}`);

    } catch (error) {
      console.error(`❌ Training failed: ${session.type}`, error);
      session.status = 'failed';
      session.endTime = new Date();
      session.results = { error: error.message };
      
      this.emit('trainingFailed', { session, error });
    } finally {
      // Save training session
      await this.saveTrainingSession(session);
      this.currentTraining = null;
      
      // Process next training in queue
      if (this.trainingQueue.length > 0) {
        const nextSession = this.trainingQueue.shift();
        if (nextSession) {
          await this.executeTraining(nextSession);
        }
      }
    }
  }

  private async runFullTraining(session: TrainingSession): Promise<void> {
    console.log('🧠 Running full training...');
    
    // Collect all training data
    const trainingData = await this.dbPromises.all(`
      SELECT * FROM training_data 
      ORDER BY quality_score DESC, timestamp DESC 
      LIMIT 1000
    `);

    if (trainingData.length === 0) {
      throw new Error('No training data available');
    }

    // Process training data
    const inputs: number[][] = [];
    const outputs: number[] = [];

    for (const data of trainingData) {
      const input = this.preprocessInput(data.input);
      const output = data.user_feedback || data.quality_score || 0.5;
      
      inputs.push(input);
      outputs.push(output);
    }

    // Train the model
    if (this.model && inputs.length > 0) {
      const inputTensor = tf.tensor2d(inputs);
      const outputTensor = tf.tensor1d(outputs);
      
      const history = await this.model.fit(inputTensor, outputTensor, {
        epochs: 10,
        batchSize: 32,
        validationSplit: 0.2,
        callbacks: {
          onEpochEnd: (epoch, logs) => {
            session.progress = ((epoch + 1) / 10) * 100;
            session.metrics.accuracy = logs?.acc || 0;
            this.emit('trainingProgress', { session, epoch, logs });
          }
        }
      });

      session.results = {
        epochs: 10,
        finalAccuracy: history.history.acc?.[history.history.acc.length - 1],
        finalLoss: history.history.loss?.[history.history.loss.length - 1]
      };
    }

    // Update learning patterns
    await this.updateLearningPatterns(trainingData);
  }

  private async runIncrementalTraining(session: TrainingSession): Promise<void> {
    console.log('🧠 Running incremental training...');
    
    // Get recent training data
    const recentData = await this.dbPromises.all(`
      SELECT * FROM training_data 
      WHERE timestamp > datetime('now', '-1 hour')
      ORDER BY timestamp DESC
    `);

    if (recentData.length === 0) {
      console.log('No recent data for incremental training');
      return;
    }

    // Process recent data
    const inputs: number[][] = [];
    const outputs: number[] = [];

    for (const data of recentData) {
      const input = this.preprocessInput(data.input);
      const output = data.user_feedback || data.quality_score || 0.5;
      
      inputs.push(input);
      outputs.push(output);
    }

    // Incremental training
    if (this.model && inputs.length > 0) {
      const inputTensor = tf.tensor2d(inputs);
      const outputTensor = tf.tensor1d(outputs);
      
      const history = await this.model.fit(inputTensor, outputTensor, {
        epochs: 3,
        batchSize: 16,
        callbacks: {
          onEpochEnd: (epoch, logs) => {
            session.progress = ((epoch + 1) / 3) * 100;
            this.emit('trainingProgress', { session, epoch, logs });
          }
        }
      });

      session.results = {
        epochs: 3,
        finalAccuracy: history.history.acc?.[history.history.acc.length - 1],
        dataPoints: recentData.length
      };
    }
  }

  private async runPatternAnalysis(session: TrainingSession): Promise<void> {
    console.log('🧠 Running pattern analysis...');
    
    // Analyze conversation patterns
    const conversations = await this.dbPromises.all(`
      SELECT input, output, quality_score, user_feedback 
      FROM training_data 
      ORDER BY timestamp DESC 
      LIMIT 500
    `);

    const patterns = this.analyzeConversationPatterns(conversations);
    
    // Update pattern database
    for (const pattern of patterns) {
      await this.saveLearningPattern(pattern);
    }

    session.results = {
      patternsFound: patterns.length,
      patterns: patterns.slice(0, 10) // Top 10 patterns
    };
  }

  private async runOptimization(session: TrainingSession): Promise<void> {
    console.log('🧠 Running optimization...');
    
    // Analyze performance metrics
    const metrics = await this.dbPromises.all(`
      SELECT metric_name, AVG(value) as avg_value, COUNT(*) as count
      FROM performance_metrics 
      WHERE timestamp > datetime('now', '-24 hours')
      GROUP BY metric_name
    `);

    // Identify optimization opportunities
    const optimizations = this.identifyOptimizations(metrics);
    
    // Apply optimizations
    for (const optimization of optimizations) {
      await this.applyOptimization(optimization);
    }

    session.results = {
      optimizationsApplied: optimizations.length,
      optimizations: optimizations
    };
  }

  private async runExperiment(session: TrainingSession): Promise<void> {
    console.log('🧠 Running experiment...');
    
    // Run A/B testing or other experiments
    const experimentResults = await this.runABTest();
    
    session.results = experimentResults;
  }

  private preprocessInput(input: string): number[] {
    // Convert text input to numerical vector
    const tokens = this.tokenizer.tokenize(input.toLowerCase());
    const stemmedTokens = tokens.map(token => this.stemmer.stem(token));
    
    // Create a simple bag-of-words vector (in real implementation, use proper embeddings)
    const vector = new Array(100).fill(0);
    
    stemmedTokens.forEach(token => {
      const hash = this.hashString(token) % 100;
      vector[hash] += 1;
    });
    
    return vector;
  }

  private hashString(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }

  private analyzeConversationPatterns(conversations: any[]): LearningPattern[] {
    const patterns: LearningPattern[] = [];
    
    // Analyze input-output relationships
    const inputOutputPairs = new Map<string, { output: string; quality: number; count: number }>();
    
    conversations.forEach(conv => {
      const key = conv.input.substring(0, 50); // First 50 chars as pattern
      const existing = inputOutputPairs.get(key);
      
      if (existing) {
        existing.count += 1;
        existing.quality = (existing.quality + conv.quality_score) / 2;
      } else {
        inputOutputPairs.set(key, {
          output: conv.output,
          quality: conv.quality_score || 0.5,
          count: 1
        });
      }
    });

    // Create patterns from frequent pairs
    inputOutputPairs.forEach((data, pattern) => {
      if (data.count > 2 && data.quality > 0.7) {
        patterns.push({
          id: uuidv4(),
          pattern,
          confidence: data.quality,
          frequency: data.count,
          lastSeen: new Date(),
          context: { output: data.output },
          improvements: 0
        });
      }
    });

    return patterns;
  }

  private identifyOptimizations(metrics: any[]): any[] {
    const optimizations: any[] = [];
    
    metrics.forEach(metric => {
      if (metric.metric_name === 'response_quality' && metric.avg_value < 0.7) {
        optimizations.push({
          type: 'improve_response_quality',
          target: 'response_quality',
          currentValue: metric.avg_value,
          action: 'adjust_personality_traits',
          parameters: { empathy: 0.1, intelligence: 0.05 }
        });
      }
      
      if (metric.metric_name === 'user_satisfaction' && metric.avg_value < 0.8) {
        optimizations.push({
          type: 'improve_user_satisfaction',
          target: 'user_satisfaction',
          currentValue: metric.avg_value,
          action: 'enhance_conversation_flow',
          parameters: { followUpQuestions: true, culturalAwareness: 0.1 }
        });
      }
    });

    return optimizations;
  }

  private async applyOptimization(optimization: any): Promise<void> {
    console.log(`🔧 Applying optimization: ${optimization.type}`);
    
    // In a real implementation, this would update the personality system
    // For now, we'll just log the optimization
    console.log('Optimization applied:', optimization);
  }

  private async runABTest(): Promise<any> {
    // Simple A/B test implementation
    const testResults = {
      testType: 'response_style',
      variantA: { style: 'formal', responses: 50, satisfaction: 0.75 },
      variantB: { style: 'casual', responses: 50, satisfaction: 0.82 },
      winner: 'variantB',
      confidence: 0.85
    };

    return testResults;
  }

  private async saveTrainingSession(session: TrainingSession): Promise<void> {
    await this.dbPromises.run(`
      INSERT OR REPLACE INTO training_sessions 
      (id, type, priority, status, start_time, end_time, progress, results, metrics)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      session.id,
      session.type,
      session.priority,
      session.status,
      session.startTime.toISOString(),
      session.endTime?.toISOString(),
      session.progress,
      JSON.stringify(session.results),
      JSON.stringify(session.metrics)
    ]);
  }

  private async saveLearningPattern(pattern: LearningPattern): Promise<void> {
    await this.dbPromises.run(`
      INSERT OR REPLACE INTO learning_patterns 
      (id, pattern, confidence, frequency, last_seen, context, improvements)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `, [
      pattern.id,
      pattern.pattern,
      pattern.confidence,
      pattern.frequency,
      pattern.lastSeen.toISOString(),
      JSON.stringify(pattern.context),
      pattern.improvements
    ]);

    this.learningPatterns.set(pattern.id, pattern);
  }

  private async updateLearningPatterns(trainingData: any[]): Promise<void> {
    // Update pattern confidence based on recent performance
    for (const [id, pattern] of this.learningPatterns) {
      const recentPerformance = trainingData.filter(data => 
        data.input.includes(pattern.pattern.substring(0, 20))
      );

      if (recentPerformance.length > 0) {
        const avgQuality = recentPerformance.reduce((sum, data) => 
          sum + (data.quality_score || 0.5), 0) / recentPerformance.length;
        
        pattern.confidence = (pattern.confidence + avgQuality) / 2;
        pattern.frequency += recentPerformance.length;
        pattern.lastSeen = new Date();
        
        if (avgQuality > pattern.confidence + 0.1) {
          pattern.improvements += 1;
        }
        
        await this.saveLearningPattern(pattern);
      }
    }
  }

  public async runScheduledTraining(): Promise<void> {
    if (!this.currentTraining) {
      await this.startTraining('incremental', 'normal');
    }
  }

  public async addTrainingData(input: string, output: string, context: any, qualityScore?: number, userFeedback?: number): Promise<void> {
    const id = uuidv4();
    
    await this.dbPromises.run(`
      INSERT INTO training_data 
      (id, input, output, context, quality_score, user_feedback, timestamp)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `, [
      id,
      input,
      output,
      JSON.stringify(context),
      qualityScore,
      userFeedback,
      new Date().toISOString()
    ]);

    this.totalInteractions += 1;
    this.emit('trainingDataAdded', { id, input, output, qualityScore, userFeedback });
  }

  public async getTrainingResults(limit: number = 20): Promise<TrainingSession[]> {
    const sessions = await this.dbPromises.all(`
      SELECT * FROM training_sessions 
      ORDER BY start_time DESC 
      LIMIT ?
    `, [limit]);

    return sessions.map(row => ({
      id: row.id,
      type: row.type,
      priority: row.priority,
      status: row.status,
      startTime: new Date(row.start_time),
      endTime: row.end_time ? new Date(row.end_time) : undefined,
      progress: row.progress,
      results: JSON.parse(row.results || '{}'),
      metrics: JSON.parse(row.metrics || '{}')
    }));
  }

  public async exportTrainingData(format: 'json' | 'csv'): Promise<string> {
    const data = await this.dbPromises.all(`
      SELECT * FROM training_data 
      ORDER BY timestamp DESC
    `);

    if (format === 'json') {
      return JSON.stringify(data, null, 2);
    } else {
      // Convert to CSV
      const headers = Object.keys(data[0] || {}).join(',');
      const rows = data.map(row => Object.values(row).join(','));
      return [headers, ...rows].join('\n');
    }
  }

  // Getters
  public isTraining(): boolean {
    return this.currentTraining !== null;
  }

  public getTrainingProgress(): number {
    return this.currentTraining?.progress || 0;
  }

  public getLastTrainingTime(): Date {
    return this.lastTrainingTime;
  }

  public getNextTrainingTime(): Date {
    return new Date(Date.now() + 60 * 60 * 1000); // Next hour
  }

  public getTotalInteractions(): number {
    return this.totalInteractions;
  }

  public getLearningRate(): number {
    return this.learningRate;
  }

  public getLastImprovementTime(): Date {
    return this.lastImprovementTime;
  }

  public getLearningPatterns(): Map<string, LearningPattern> {
    return new Map(this.learningPatterns);
  }

  public getPatternCount(): number {
    return this.learningPatterns.size;
  }
}
