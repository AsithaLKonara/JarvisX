/**
 * Trading Strategy for JarvisX Trading Service
 * Implements various trading strategies and signal generation
 */

import { EventEmitter } from 'events';

export interface TradingSignal {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reason: string;
  suggestedQuantity: number;
  suggestedPrice?: number;
  timestamp: number;
}

export interface StrategyConfig {
  name: string;
  enabled: boolean;
  parameters: Record<string, any>;
}

export interface MarketData {
  symbol: string;
  price: number;
  volume: number;
  change24h: number;
  changePercent24h: number;
  timestamp: number;
}

export class TradingStrategy extends EventEmitter {
  private strategies: Map<string, StrategyConfig> = new Map();
  private signalHistory: TradingSignal[] = [];
  private maxHistorySize: number = 1000;

  constructor() {
    super();
    this.initializeDefaultStrategies();
  }

  private initializeDefaultStrategies(): void {
    // Moving Average Crossover Strategy
    this.strategies.set('ma_crossover', {
      name: 'Moving Average Crossover',
      enabled: true,
      parameters: {
        shortPeriod: 10,
        longPeriod: 20,
        minConfidence: 0.6
      }
    });

    // Momentum Strategy
    this.strategies.set('momentum', {
      name: 'Momentum Strategy',
      enabled: true,
      parameters: {
        lookbackPeriod: 14,
        threshold: 0.05,
        minConfidence: 0.7
      }
    });

    // RSI Strategy
    this.strategies.set('rsi', {
      name: 'RSI Strategy',
      enabled: true,
      parameters: {
        period: 14,
        oversoldThreshold: 30,
        overboughtThreshold: 70,
        minConfidence: 0.8
      }
    });

    console.log('✅ Trading strategies initialized');
  }

  public async analyze(data: MarketData): Promise<TradingSignal[]> {
    const signals: TradingSignal[] = [];

    try {
      // Run each enabled strategy
      for (const [strategyId, config] of this.strategies) {
        if (config.enabled) {
          const strategySignals = await this.runStrategy(strategyId, data, config);
          signals.push(...strategySignals);
        }
      }

      // Store signals in history
      this.signalHistory.push(...signals);
      
      // Maintain history size limit
      if (this.signalHistory.length > this.maxHistorySize) {
        this.signalHistory = this.signalHistory.slice(-this.maxHistorySize);
      }

      // Emit signals
      signals.forEach(signal => {
        this.emit('signal', signal);
      });

      return signals;

    } catch (error) {
      console.error('❌ Strategy analysis failed:', error);
      return [];
    }
  }

  private async runStrategy(
    strategyId: string, 
    data: MarketData, 
    config: StrategyConfig
  ): Promise<TradingSignal[]> {
    switch (strategyId) {
      case 'ma_crossover':
        return this.movingAverageCrossover(data, config.parameters);
      
      case 'momentum':
        return this.momentumStrategy(data, config.parameters);
      
      case 'rsi':
        return this.rsiStrategy(data, config.parameters);
      
      default:
        console.warn(`⚠️ Unknown strategy: ${strategyId}`);
        return [];
    }
  }

  private async movingAverageCrossover(
    data: MarketData, 
    params: any
  ): Promise<TradingSignal[]> {
    // Simplified moving average crossover logic
    // In a real implementation, you would need historical price data
    
    const signals: TradingSignal[] = [];
    
    // Simulate MA calculation (would need historical data)
    const shortMA = data.price * (1 + Math.random() * 0.02 - 0.01); // Simulated
    const longMA = data.price * (1 + Math.random() * 0.02 - 0.01); // Simulated
    
    let action: 'BUY' | 'SELL' | 'HOLD' = 'HOLD';
    let confidence = 0;
    let reason = '';

    if (shortMA > longMA && data.changePercent24h > 0) {
      action = 'BUY';
      confidence = Math.min(0.9, 0.5 + Math.abs(data.changePercent24h) / 10);
      reason = `Short MA (${shortMA.toFixed(4)}) crossed above Long MA (${longMA.toFixed(4)})`;
    } else if (shortMA < longMA && data.changePercent24h < 0) {
      action = 'SELL';
      confidence = Math.min(0.9, 0.5 + Math.abs(data.changePercent24h) / 10);
      reason = `Short MA (${shortMA.toFixed(4)}) crossed below Long MA (${longMA.toFixed(4)})`;
    }

    if (action !== 'HOLD' && confidence >= params.minConfidence) {
      signals.push({
        symbol: data.symbol,
        action,
        confidence,
        reason,
        suggestedQuantity: this.calculateQuantity(data.price, confidence),
        timestamp: Date.now()
      });
    }

    return signals;
  }

  private async momentumStrategy(
    data: MarketData, 
    params: any
  ): Promise<TradingSignal[]> {
    const signals: TradingSignal[] = [];
    
    const momentum = Math.abs(data.changePercent24h);
    let action: 'BUY' | 'SELL' | 'HOLD' = 'HOLD';
    let confidence = 0;
    let reason = '';

    if (data.changePercent24h > params.threshold && momentum > 0.02) {
      action = 'BUY';
      confidence = Math.min(0.95, momentum * 10);
      reason = `Strong upward momentum: ${data.changePercent24h.toFixed(2)}%`;
    } else if (data.changePercent24h < -params.threshold && momentum > 0.02) {
      action = 'SELL';
      confidence = Math.min(0.95, momentum * 10);
      reason = `Strong downward momentum: ${data.changePercent24h.toFixed(2)}%`;
    }

    if (action !== 'HOLD' && confidence >= params.minConfidence) {
      signals.push({
        symbol: data.symbol,
        action,
        confidence,
        reason,
        suggestedQuantity: this.calculateQuantity(data.price, confidence),
        timestamp: Date.now()
      });
    }

    return signals;
  }

  private async rsiStrategy(
    data: MarketData, 
    params: any
  ): Promise<TradingSignal[]> {
    const signals: TradingSignal[] = [];
    
    // Simulate RSI calculation (would need historical data)
    const rsi = 30 + Math.random() * 40; // Simulated RSI between 30-70
    
    let action: 'BUY' | 'SELL' | 'HOLD' = 'HOLD';
    let confidence = 0;
    let reason = '';

    if (rsi < params.oversoldThreshold) {
      action = 'BUY';
      confidence = 0.8 + (params.oversoldThreshold - rsi) / 100;
      reason = `RSI oversold: ${rsi.toFixed(1)} (threshold: ${params.oversoldThreshold})`;
    } else if (rsi > params.overboughtThreshold) {
      action = 'SELL';
      confidence = 0.8 + (rsi - params.overboughtThreshold) / 100;
      reason = `RSI overbought: ${rsi.toFixed(1)} (threshold: ${params.overboughtThreshold})`;
    }

    if (action !== 'HOLD' && confidence >= params.minConfidence) {
      signals.push({
        symbol: data.symbol,
        action,
        confidence,
        reason,
        suggestedQuantity: this.calculateQuantity(data.price, confidence),
        timestamp: Date.now()
      });
    }

    return signals;
  }

  private calculateQuantity(price: number, confidence: number): number {
    // Simple quantity calculation based on confidence
    // In a real implementation, this would consider account balance, risk management, etc.
    const baseQuantity = 100; // Base quantity
    const confidenceMultiplier = confidence * 2; // Scale by confidence
    return Math.round(baseQuantity * confidenceMultiplier);
  }

  public getStrategies(): Map<string, StrategyConfig> {
    return this.strategies;
  }

  public updateStrategy(strategyId: string, config: Partial<StrategyConfig>): void {
    const existing = this.strategies.get(strategyId);
    if (existing) {
      this.strategies.set(strategyId, { ...existing, ...config });
      console.log(`✅ Strategy ${strategyId} updated`);
    } else {
      console.warn(`⚠️ Strategy ${strategyId} not found`);
    }
  }

  public enableStrategy(strategyId: string): void {
    this.updateStrategy(strategyId, { enabled: true });
  }

  public disableStrategy(strategyId: string): void {
    this.updateStrategy(strategyId, { enabled: false });
  }

  public getSignalHistory(limit?: number): TradingSignal[] {
    if (limit) {
      return this.signalHistory.slice(-limit);
    }
    return [...this.signalHistory];
  }

  public getStrategyPerformance(strategyId: string): any {
    const strategySignals = this.signalHistory.filter(signal => 
      signal.reason.includes(this.strategies.get(strategyId)?.name || '')
    );

    if (strategySignals.length === 0) {
      return { totalSignals: 0, accuracy: 0, averageConfidence: 0 };
    }

    // Simplified performance calculation
    // In a real implementation, you would track actual trade outcomes
    const totalSignals = strategySignals.length;
    const averageConfidence = strategySignals.reduce((sum, signal) => 
      sum + signal.confidence, 0) / totalSignals;
    
    // Simulate accuracy based on confidence
    const estimatedAccuracy = averageConfidence * 0.8; // Assume 80% of confidence translates to accuracy

    return {
      totalSignals,
      accuracy: estimatedAccuracy,
      averageConfidence,
      lastSignal: strategySignals[strategySignals.length - 1]
    };
  }

  public clearHistory(): void {
    this.signalHistory = [];
    console.log('🗑️ Trading signal history cleared');
  }
}
