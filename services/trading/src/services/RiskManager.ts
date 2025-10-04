/**
 * Risk Manager for JarvisX Trading Service
 * Manages position limits, exposure controls, and risk assessment
 */

import { EventEmitter } from 'events';

export interface RiskLimits {
  maxPositionSize: number;
  maxDailyLoss: number;
  maxExposure: number;
  maxLeverage?: number;
  stopLossPercentage: number;
  takeProfitPercentage: number;
}

export interface Position {
  symbol: string;
  side: 'long' | 'short';
  size: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercentage: number;
  timestamp: string;
}

export interface TradeValidation {
  approved: boolean;
  reason?: string;
  riskLevel: 'low' | 'medium' | 'high';
  suggestedAdjustments?: string[];
}

export interface RiskMetrics {
  currentExposure: number;
  dailyPnL: number;
  openPositions: number;
  riskUtilization: number;
  maxDrawdown: number;
  sharpeRatio: number;
}

export class RiskManager extends EventEmitter {
  private riskLimits: RiskLimits;
  private positions: Position[] = [];
  private dailyPnL: number = 0;
  private tradeHistory: any[] = [];
  private maxHistorySize: number = 10000;

  constructor(initialLimits?: Partial<RiskLimits>) {
    super();
    
    this.riskLimits = {
      maxPositionSize: 1000,
      maxDailyLoss: 500,
      maxExposure: 5000,
      maxLeverage: 10,
      stopLossPercentage: 5,
      takeProfitPercentage: 10,
      ...initialLimits
    };

    console.log('🛡️ Risk Manager initialized with limits:', this.riskLimits);
  }

  public async validateTrade(tradeData: any): Promise<TradeValidation> {
    try {
      console.log('🔍 Validating trade:', tradeData);

      const validation: TradeValidation = {
        approved: true,
        riskLevel: 'low',
        suggestedAdjustments: []
      };

      // Check position size limit
      if (tradeData.quantity > this.riskLimits.maxPositionSize) {
        validation.approved = false;
        validation.reason = `Position size ${tradeData.quantity} exceeds limit ${this.riskLimits.maxPositionSize}`;
        validation.riskLevel = 'high';
        return validation;
      }

      // Check daily loss limit
      if (this.dailyPnL < -this.riskLimits.maxDailyLoss) {
        validation.approved = false;
        validation.reason = `Daily loss ${Math.abs(this.dailyPnL)} exceeds limit ${this.riskLimits.maxDailyLoss}`;
        validation.riskLevel = 'high';
        return validation;
      }

      // Check exposure limit
      const newExposure = this.getCurrentExposure() + (tradeData.quantity * tradeData.price);
      if (newExposure > this.riskLimits.maxExposure) {
        validation.approved = false;
        validation.reason = `Total exposure ${newExposure} would exceed limit ${this.riskLimits.maxExposure}`;
        validation.riskLevel = 'high';
        return validation;
      }

      // Check concentration risk (single position size vs total portfolio)
      const concentrationRatio = (tradeData.quantity * tradeData.price) / this.getCurrentExposure();
      if (concentrationRatio > 0.3) { // 30% concentration limit
        validation.riskLevel = 'medium';
        validation.suggestedAdjustments?.push('Consider reducing position size to limit concentration risk');
      }

      // Check leverage (if applicable)
      if (tradeData.leverage && tradeData.leverage > this.riskLimits.maxLeverage) {
        validation.approved = false;
        validation.reason = `Leverage ${tradeData.leverage} exceeds limit ${this.riskLimits.maxLeverage}`;
        validation.riskLevel = 'high';
        return validation;
      }

      // Check volatility (simplified)
      if (Math.abs(tradeData.changePercent24h) > 20) { // 20% daily change threshold
        validation.riskLevel = 'high';
        validation.suggestedAdjustments?.push('High volatility detected - consider smaller position size');
      }

      console.log(`✅ Trade validation: ${validation.approved ? 'APPROVED' : 'REJECTED'} (${validation.riskLevel} risk)`);
      
      return validation;

    } catch (error) {
      console.error('❌ Trade validation failed:', error);
      return {
        approved: false,
        reason: 'Validation error occurred',
        riskLevel: 'high'
      };
    }
  }

  public updatePositions(positions: Position[]): void {
    this.positions = positions;
    this.calculateDailyPnL();
    this.emit('positionsUpdated', positions);
  }

  public addPosition(position: Position): void {
    this.positions.push(position);
    this.calculateDailyPnL();
    this.emit('positionAdded', position);
  }

  public removePosition(symbol: string, side: 'long' | 'short'): void {
    const index = this.positions.findIndex(p => p.symbol === symbol && p.side === side);
    if (index !== -1) {
      const position = this.positions[index];
      this.positions.splice(index, 1);
      this.calculateDailyPnL();
      this.emit('positionRemoved', position);
    }
  }

  private calculateDailyPnL(): void {
    this.dailyPnL = this.positions.reduce((total, position) => total + position.pnl, 0);
  }

  public getCurrentExposure(): number {
    return this.positions.reduce((total, position) => 
      total + (position.size * position.currentPrice), 0);
  }

  public getRiskMetrics(): RiskMetrics {
    const currentExposure = this.getCurrentExposure();
    const openPositions = this.positions.length;
    const riskUtilization = (currentExposure / this.riskLimits.maxExposure) * 100;
    
    // Calculate max drawdown (simplified)
    const maxDrawdown = this.calculateMaxDrawdown();
    
    // Calculate Sharpe ratio (simplified)
    const sharpeRatio = this.calculateSharpeRatio();

    return {
      currentExposure,
      dailyPnL: this.dailyPnL,
      openPositions,
      riskUtilization,
      maxDrawdown,
      sharpeRatio
    };
  }

  private calculateMaxDrawdown(): number {
    if (this.tradeHistory.length === 0) return 0;
    
    let peak = 0;
    let maxDrawdown = 0;
    
    // Simplified calculation - would need proper portfolio value history
    this.tradeHistory.forEach(trade => {
      const portfolioValue = trade.portfolioValue || 0;
      if (portfolioValue > peak) {
        peak = portfolioValue;
      }
      const drawdown = (peak - portfolioValue) / peak;
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown;
      }
    });
    
    return maxDrawdown * 100; // Return as percentage
  }

  private calculateSharpeRatio(): number {
    if (this.tradeHistory.length < 2) return 0;
    
    // Simplified Sharpe ratio calculation
    // In practice, you would need risk-free rate and proper return calculations
    const returns = this.tradeHistory.map(trade => trade.return || 0);
    const avgReturn = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
    const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length;
    const stdDev = Math.sqrt(variance);
    
    return stdDev > 0 ? avgReturn / stdDev : 0;
  }

  public getRiskLimits(): RiskLimits {
    return { ...this.riskLimits };
  }

  public updateRiskLimits(newLimits: Partial<RiskLimits>): void {
    this.riskLimits = { ...this.riskLimits, ...newLimits };
    console.log('✅ Risk limits updated:', this.riskLimits);
    this.emit('riskLimitsUpdated', this.riskLimits);
  }

  public checkRiskAlerts(): string[] {
    const alerts: string[] = [];
    const metrics = this.getRiskMetrics();

    // Check exposure utilization
    if (metrics.riskUtilization > 80) {
      alerts.push(`High exposure utilization: ${metrics.riskUtilization.toFixed(1)}%`);
    }

    // Check daily loss
    if (metrics.dailyPnL < -this.riskLimits.maxDailyLoss * 0.8) {
      alerts.push(`Approaching daily loss limit: ${Math.abs(metrics.dailyPnL).toFixed(2)}`);
    }

    // Check position count
    if (metrics.openPositions > 20) {
      alerts.push(`High number of open positions: ${metrics.openPositions}`);
    }

    // Check drawdown
    if (metrics.maxDrawdown > 20) {
      alerts.push(`High drawdown: ${metrics.maxDrawdown.toFixed(1)}%`);
    }

    if (alerts.length > 0) {
      this.emit('riskAlerts', alerts);
    }

    return alerts;
  }

  public emergencyStop(): void {
    console.log('🛑 EMERGENCY STOP TRIGGERED');
    
    // Close all positions
    this.positions.forEach(position => {
      this.emit('emergencyClose', position);
    });
    
    // Clear positions
    this.positions = [];
    
    // Reset daily P&L
    this.dailyPnL = 0;
    
    this.emit('emergencyStopExecuted');
  }

  public addTradeToHistory(trade: any): void {
    this.tradeHistory.push({
      ...trade,
      timestamp: new Date().toISOString()
    });
    
    // Maintain history size limit
    if (this.tradeHistory.length > this.maxHistorySize) {
      this.tradeHistory = this.tradeHistory.slice(-this.maxHistorySize);
    }
  }

  public getTradeHistory(limit?: number): any[] {
    if (limit) {
      return this.tradeHistory.slice(-limit);
    }
    return [...this.tradeHistory];
  }

  public calculatePositionSize(
    symbol: string, 
    price: number, 
    riskPercentage: number = 2
  ): number {
    // Calculate position size based on risk percentage
    const accountValue = this.getCurrentExposure() || 10000; // Default account value
    const riskAmount = accountValue * (riskPercentage / 100);
    const stopLossDistance = price * (this.riskLimits.stopLossPercentage / 100);
    
    const positionSize = riskAmount / stopLossDistance;
    
    // Apply position size limit
    return Math.min(positionSize, this.riskLimits.maxPositionSize);
  }

  public getStopLossPrice(entryPrice: number, side: 'long' | 'short'): number {
    const stopLossDistance = entryPrice * (this.riskLimits.stopLossPercentage / 100);
    
    if (side === 'long') {
      return entryPrice - stopLossDistance;
    } else {
      return entryPrice + stopLossDistance;
    }
  }

  public getTakeProfitPrice(entryPrice: number, side: 'long' | 'short'): number {
    const takeProfitDistance = entryPrice * (this.riskLimits.takeProfitPercentage / 100);
    
    if (side === 'long') {
      return entryPrice + takeProfitDistance;
    } else {
      return entryPrice - takeProfitDistance;
    }
  }

  public clearHistory(): void {
    this.tradeHistory = [];
    this.dailyPnL = 0;
    console.log('🗑️ Risk manager history cleared');
  }
}
