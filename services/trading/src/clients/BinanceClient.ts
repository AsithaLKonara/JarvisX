/**
 * Binance Client for JarvisX Trading Service
 * Handles market data and trading operations with Binance API
 */

import { EventEmitter } from 'events';
import axios, { AxiosInstance } from 'axios';
import crypto from 'crypto';

export interface BinanceConfig {
  apiKey: string;
  secretKey: string;
  baseUrl?: string;
  testnet?: boolean;
}

export interface MarketData {
  symbol: string;
  price: number;
  volume: number;
  change24h: number;
  changePercent24h: number;
  timestamp: number;
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

export interface Order {
  symbol: string;
  side: 'BUY' | 'SELL';
  type: 'MARKET' | 'LIMIT' | 'STOP';
  quantity: number;
  price?: number;
  stopPrice?: number;
}

export class BinanceClient extends EventEmitter {
  private config: BinanceConfig;
  private httpClient: AxiosInstance;
  private wsClient: any = null;
  private isConnected: boolean = false;
  private marketDataStream: any = null;

  constructor(config: BinanceConfig) {
    super();
    this.config = {
      baseUrl: config.testnet ? 'https://testnet.binance.vision' : 'https://api.binance.com',
      ...config
    };

    this.httpClient = axios.create({
      baseURL: this.config.baseUrl,
      timeout: 30000,
      headers: {
        'X-MBX-APIKEY': this.config.apiKey,
        'Content-Type': 'application/json'
      }
    });

    this.setupHttpInterceptors();
  }

  private setupHttpInterceptors(): void {
    this.httpClient.interceptors.request.use(
      (config) => {
        if (config.url?.includes('/api/v3/')) {
          // Add signature for authenticated endpoints
          const timestamp = Date.now();
          const queryString = config.params ? new URLSearchParams(config.params).toString() : '';
          const signature = this.createSignature(queryString, timestamp);
          
          config.params = {
            ...config.params,
            timestamp,
            signature
          };
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  private createSignature(queryString: string, timestamp: number): string {
    const message = `${queryString}&timestamp=${timestamp}`;
    return crypto
      .createHmac('sha256', this.config.secretKey)
      .update(message)
      .digest('hex');
  }

  public async initialize(): Promise<void> {
    try {
      console.log('🔗 Initializing Binance client...');
      
      // Test connection
      const response = await this.httpClient.get('/api/v3/ping');
      if (response.status === 200) {
        this.isConnected = true;
        console.log('✅ Binance client connected successfully');
      }
    } catch (error) {
      console.error('❌ Failed to initialize Binance client:', error);
      throw error;
    }
  }

  public isConnected(): boolean {
    return this.isConnected;
  }

  public async getMarketData(symbol: string): Promise<MarketData> {
    try {
      const response = await this.httpClient.get('/api/v3/ticker/24hr', {
        params: { symbol: symbol.toUpperCase() }
      });

      const data = response.data;
      return {
        symbol: data.symbol,
        price: parseFloat(data.lastPrice),
        volume: parseFloat(data.volume),
        change24h: parseFloat(data.priceChange),
        changePercent24h: parseFloat(data.priceChangePercent),
        timestamp: data.closeTime
      };
    } catch (error) {
      console.error(`❌ Failed to get market data for ${symbol}:`, error);
      throw error;
    }
  }

  public async getPositions(): Promise<Position[]> {
    try {
      const response = await this.httpClient.get('/api/v3/account');
      const positions: Position[] = [];

      // Process account balances
      response.data.balances.forEach((balance: any) => {
        const free = parseFloat(balance.free);
        const locked = parseFloat(balance.locked);
        
        if (free > 0 || locked > 0) {
          positions.push({
            symbol: balance.asset,
            side: 'long',
            size: free + locked,
            entryPrice: 0, // Would need to track this separately
            currentPrice: 0, // Would need current market price
            pnl: 0, // Would need to calculate
            pnlPercentage: 0,
            timestamp: new Date().toISOString()
          });
        }
      });

      return positions;
    } catch (error) {
      console.error('❌ Failed to get positions:', error);
      throw error;
    }
  }

  public async executeTrade(order: Order): Promise<any> {
    try {
      console.log(`🎯 Executing trade: ${order.side} ${order.quantity} ${order.symbol}`);

      const orderData = {
        symbol: order.symbol.toUpperCase(),
        side: order.side,
        type: order.type,
        quantity: order.quantity.toString(),
        ...(order.price && { price: order.price.toString() }),
        ...(order.stopPrice && { stopPrice: order.stopPrice.toString() }),
        timestamp: Date.now()
      };

      const response = await this.httpClient.post('/api/v3/order', orderData);
      
      console.log(`✅ Trade executed successfully:`, response.data);
      return response.data;

    } catch (error: any) {
      console.error('❌ Trade execution failed:', error.response?.data || error.message);
      throw error;
    }
  }

  public async startMarketDataStream(callback: (data: MarketData) => void): Promise<void> {
    try {
      console.log('📡 Starting market data stream...');
      
      // This would implement WebSocket streaming for real-time market data
      // For now, we'll simulate with polling
      setInterval(async () => {
        try {
          const symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT'];
          
          for (const symbol of symbols) {
            const marketData = await this.getMarketData(symbol);
            callback(marketData);
          }
        } catch (error) {
          console.error('❌ Market data stream error:', error);
        }
      }, 5000); // Poll every 5 seconds

      console.log('✅ Market data stream started');

    } catch (error) {
      console.error('❌ Failed to start market data stream:', error);
      throw error;
    }
  }

  public async stopMarketDataStream(): Promise<void> {
    if (this.marketDataStream) {
      this.marketDataStream.close();
      this.marketDataStream = null;
      console.log('📡 Market data stream stopped');
    }
  }

  public async getAccountInfo(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/v3/account');
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get account info:', error);
      throw error;
    }
  }

  public async getOpenOrders(symbol?: string): Promise<any[]> {
    try {
      const params: any = {};
      if (symbol) {
        params.symbol = symbol.toUpperCase();
      }

      const response = await this.httpClient.get('/api/v3/openOrders', { params });
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get open orders:', error);
      throw error;
    }
  }

  public async cancelOrder(symbol: string, orderId: number): Promise<any> {
    try {
      const response = await this.httpClient.delete('/api/v3/order', {
        params: {
          symbol: symbol.toUpperCase(),
          orderId: orderId.toString()
        }
      });
      
      console.log(`✅ Order ${orderId} cancelled for ${symbol}`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to cancel order:', error);
      throw error;
    }
  }

  public async cancelAllOrders(symbol?: string): Promise<any> {
    try {
      const params: any = {};
      if (symbol) {
        params.symbol = symbol.toUpperCase();
      }

      const response = await this.httpClient.delete('/api/v3/openOrders', { params });
      
      console.log(`✅ All orders cancelled${symbol ? ` for ${symbol}` : ''}`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to cancel all orders:', error);
      throw error;
    }
  }

  public async getOrderHistory(symbol?: string, limit: number = 500): Promise<any[]> {
    try {
      const params: any = { limit };
      if (symbol) {
        params.symbol = symbol.toUpperCase();
      }

      const response = await this.httpClient.get('/api/v3/allOrders', { params });
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get order history:', error);
      throw error;
    }
  }

  public async getTradingFees(): Promise<any> {
    try {
      const response = await this.httpClient.get('/api/v3/account');
      return response.data.feeTier;
    } catch (error) {
      console.error('❌ Failed to get trading fees:', error);
      throw error;
    }
  }

  public disconnect(): void {
    this.isConnected = false;
    this.stopMarketDataStream();
    console.log('🔌 Binance client disconnected');
  }
}
