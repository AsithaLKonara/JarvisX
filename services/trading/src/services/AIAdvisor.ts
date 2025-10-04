/**
 * AI Advisor for JarvisX Trading Service
 * Provides AI-powered trading recommendations using GPT-5
 */

import { EventEmitter } from 'events';
import axios from 'axios';

export interface TradingRecommendation {
  id: string;
  symbol: string;
  action: 'buy' | 'sell' | 'hold';
  confidence: number;
  reason: string;
  suggestedSize: number;
  riskLevel: 'low' | 'medium' | 'high';
  timestamp: string;
  priceTarget?: number;
  stopLoss?: number;
  takeProfit?: number;
}

export interface MarketAnalysis {
  symbol: string;
  trend: 'bullish' | 'bearish' | 'neutral';
  sentiment: number; // -1 to 1
  volatility: 'low' | 'medium' | 'high';
  volume: 'low' | 'medium' | 'high';
  technicalIndicators: {
    rsi: number;
    macd: number;
    movingAverage: number;
    support: number;
    resistance: number;
  };
  fundamentalAnalysis: {
    marketCap: number;
    newsSentiment: number;
    analystRatings: string[];
  };
}

export class AIAdvisor extends EventEmitter {
  private openaiApiKey: string;
  private recommendations: TradingRecommendation[] = [];
  private marketData: Map<string, any> = new Map();
  private maxRecommendations: number = 100;

  constructor(openaiApiKey: string) {
    super();
    this.openaiApiKey = openaiApiKey;
    console.log('🤖 AI Advisor initialized');
  }

  public async getRecommendations(): Promise<TradingRecommendation[]> {
    try {
      console.log('🔍 Generating AI trading recommendations...');

      const recommendations: TradingRecommendation[] = [];

      // Analyze each symbol in market data
      for (const [symbol, data] of this.marketData) {
        try {
          const analysis = await this.analyzeSymbol(symbol, data);
          const recommendation = await this.generateRecommendation(symbol, analysis);
          
          if (recommendation) {
            recommendations.push(recommendation);
          }
        } catch (error) {
          console.error(`❌ Failed to analyze ${symbol}:`, error);
        }
      }

      // Store recommendations
      this.recommendations = recommendations.slice(-this.maxRecommendations);

      console.log(`✅ Generated ${recommendations.length} recommendations`);
      return recommendations;

    } catch (error) {
      console.error('❌ Failed to generate recommendations:', error);
      return [];
    }
  }

  public async updateMarketData(data: any): Promise<void> {
    try {
      // Update market data for the symbol
      this.marketData.set(data.symbol, {
        ...this.marketData.get(data.symbol),
        ...data,
        timestamp: Date.now()
      });

      // Emit market data update
      this.emit('marketDataUpdated', data);

    } catch (error) {
      console.error('❌ Failed to update market data:', error);
    }
  }

  private async analyzeSymbol(symbol: string, data: any): Promise<MarketAnalysis> {
    try {
      // Call GPT-5 for market analysis
      const prompt = this.createAnalysisPrompt(symbol, data);
      const analysis = await this.callGPT5(prompt);

      return {
        symbol,
        trend: analysis.trend || 'neutral',
        sentiment: analysis.sentiment || 0,
        volatility: analysis.volatility || 'medium',
        volume: analysis.volume || 'medium',
        technicalIndicators: {
          rsi: analysis.rsi || 50,
          macd: analysis.macd || 0,
          movingAverage: analysis.movingAverage || data.price,
          support: analysis.support || data.price * 0.95,
          resistance: analysis.resistance || data.price * 1.05
        },
        fundamentalAnalysis: {
          marketCap: data.marketCap || 0,
          newsSentiment: analysis.newsSentiment || 0,
          analystRatings: analysis.analystRatings || []
        }
      };

    } catch (error) {
      console.error(`❌ Failed to analyze ${symbol}:`, error);
      
      // Return default analysis
      return {
        symbol,
        trend: 'neutral',
        sentiment: 0,
        volatility: 'medium',
        volume: 'medium',
        technicalIndicators: {
          rsi: 50,
          macd: 0,
          movingAverage: data.price,
          support: data.price * 0.95,
          resistance: data.price * 1.05
        },
        fundamentalAnalysis: {
          marketCap: 0,
          newsSentiment: 0,
          analystRatings: []
        }
      };
    }
  }

  private async generateRecommendation(
    symbol: string, 
    analysis: MarketAnalysis
  ): Promise<TradingRecommendation | null> {
    try {
      // Call GPT-5 for trading recommendation
      const prompt = this.createRecommendationPrompt(symbol, analysis);
      const recommendation = await this.callGPT5(prompt);

      if (!recommendation || recommendation.action === 'hold') {
        return null;
      }

      return {
        id: `rec_${Date.now()}_${symbol}`,
        symbol,
        action: recommendation.action,
        confidence: Math.min(1.0, Math.max(0.0, recommendation.confidence || 0.5)),
        reason: recommendation.reason || 'AI analysis based on market conditions',
        suggestedSize: this.calculateSuggestedSize(symbol, analysis, recommendation),
        riskLevel: this.calculateRiskLevel(analysis, recommendation),
        timestamp: new Date().toISOString(),
        priceTarget: recommendation.priceTarget,
        stopLoss: recommendation.stopLoss,
        takeProfit: recommendation.takeProfit
      };

    } catch (error) {
      console.error(`❌ Failed to generate recommendation for ${symbol}:`, error);
      return null;
    }
  }

  private createAnalysisPrompt(symbol: string, data: any): string {
    return `
Analyze the following cryptocurrency market data and provide a comprehensive technical and fundamental analysis.

Symbol: ${symbol}
Current Price: $${data.price}
24h Change: ${data.changePercent24h}%
Volume: ${data.volume}
Market Cap: $${data.marketCap || 'Unknown'}

Please provide analysis in the following JSON format:
{
  "trend": "bullish|bearish|neutral",
  "sentiment": -1.0 to 1.0,
  "volatility": "low|medium|high",
  "volume": "low|medium|high",
  "rsi": number,
  "macd": number,
  "movingAverage": number,
  "support": number,
  "resistance": number,
  "newsSentiment": -1.0 to 1.0,
  "analystRatings": ["buy", "hold", "sell"],
  "keyFactors": ["factor1", "factor2"],
  "riskAssessment": "low|medium|high"
}

Focus on:
1. Technical indicators and patterns
2. Market sentiment and momentum
3. Volume analysis
4. Support and resistance levels
5. Risk factors and opportunities
`;
  }

  private createRecommendationPrompt(symbol: string, analysis: MarketAnalysis): string {
    return `
Based on the following market analysis for ${symbol}, provide a trading recommendation.

Analysis:
- Trend: ${analysis.trend}
- Sentiment: ${analysis.sentiment}
- Volatility: ${analysis.volatility}
- Volume: ${analysis.volume}
- RSI: ${analysis.technicalIndicators.rsi}
- Support: $${analysis.technicalIndicators.support}
- Resistance: $${analysis.technicalIndicators.resistance}

Please provide recommendation in the following JSON format:
{
  "action": "buy|sell|hold",
  "confidence": 0.0 to 1.0,
  "reason": "detailed explanation",
  "priceTarget": number,
  "stopLoss": number,
  "takeProfit": number,
  "riskFactors": ["risk1", "risk2"],
  "opportunityFactors": ["opp1", "opp2"]
}

Consider:
1. Current market conditions
2. Risk-reward ratio
3. Technical indicators
4. Market sentiment
5. Volatility levels
6. Support/resistance levels

Only recommend buy/sell if confidence is above 0.6 and there's a clear opportunity.
`;
  }

  private async callGPT5(prompt: string): Promise<any> {
    try {
      const response = await axios.post('https://api.openai.com/v1/chat/completions', {
        model: 'gpt-4', // Using GPT-4 as GPT-5 is not yet available
        messages: [
          {
            role: 'system',
            content: 'You are an expert cryptocurrency trading analyst. Provide accurate, data-driven analysis and recommendations. Always respond with valid JSON format.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.3,
        max_tokens: 1000
      }, {
        headers: {
          'Authorization': `Bearer ${this.openaiApiKey}`,
          'Content-Type': 'application/json'
        }
      });

      const content = response.data.choices[0].message.content;
      
      try {
        return JSON.parse(content);
      } catch (parseError) {
        console.error('❌ Failed to parse GPT response:', parseError);
        return null;
      }

    } catch (error) {
      console.error('❌ GPT API call failed:', error);
      return null;
    }
  }

  private calculateSuggestedSize(symbol: string, analysis: MarketAnalysis, recommendation: any): number {
    // Calculate suggested position size based on confidence and risk level
    const baseSize = 100; // Base position size
    const confidenceMultiplier = recommendation.confidence || 0.5;
    const riskMultiplier = analysis.volatility === 'high' ? 0.5 : 
                          analysis.volatility === 'medium' ? 0.8 : 1.0;
    
    return Math.round(baseSize * confidenceMultiplier * riskMultiplier);
  }

  private calculateRiskLevel(analysis: MarketAnalysis, recommendation: any): 'low' | 'medium' | 'high' {
    const confidence = recommendation.confidence || 0.5;
    const volatility = analysis.volatility;
    const sentiment = Math.abs(analysis.sentiment);

    // High risk if low confidence, high volatility, or extreme sentiment
    if (confidence < 0.6 || volatility === 'high' || sentiment > 0.8) {
      return 'high';
    }

    // Medium risk for moderate conditions
    if (confidence < 0.8 || volatility === 'medium' || sentiment > 0.5) {
      return 'medium';
    }

    // Low risk for favorable conditions
    return 'low';
  }

  public getRecommendations(): TradingRecommendation[] {
    return [...this.recommendations];
  }

  public getRecommendationById(id: string): TradingRecommendation | null {
    return this.recommendations.find(rec => rec.id === id) || null;
  }

  public getRecommendationsBySymbol(symbol: string): TradingRecommendation[] {
    return this.recommendations.filter(rec => rec.symbol === symbol);
  }

  public getLatestRecommendations(limit: number = 10): TradingRecommendation[] {
    return this.recommendations.slice(-limit);
  }

  public clearRecommendations(): void {
    this.recommendations = [];
    console.log('🗑️ AI recommendations cleared');
  }

  public getMarketData(symbol?: string): any {
    if (symbol) {
      return this.marketData.get(symbol);
    }
    return Object.fromEntries(this.marketData);
  }

  public getAnalysisSummary(): any {
    const recommendations = this.getRecommendations();
    const buyRecommendations = recommendations.filter(r => r.action === 'buy').length;
    const sellRecommendations = recommendations.filter(r => r.action === 'sell').length;
    const holdRecommendations = recommendations.filter(r => r.action === 'hold').length;

    const avgConfidence = recommendations.length > 0 ? 
      recommendations.reduce((sum, r) => sum + r.confidence, 0) / recommendations.length : 0;

    const riskDistribution = {
      low: recommendations.filter(r => r.riskLevel === 'low').length,
      medium: recommendations.filter(r => r.riskLevel === 'medium').length,
      high: recommendations.filter(r => r.riskLevel === 'high').length
    };

    return {
      totalRecommendations: recommendations.length,
      buyRecommendations,
      sellRecommendations,
      holdRecommendations,
      averageConfidence: avgConfidence,
      riskDistribution,
      lastUpdated: new Date().toISOString()
    };
  }
}
