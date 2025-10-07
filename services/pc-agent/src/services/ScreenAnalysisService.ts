/**
 * Screen Analysis Service for JarvisX PC Agent
 * Integrates with OCR, Vision, and Screen Analyzer services
 */

import axios from 'axios';

export interface ScreenElement {
  type: string;
  text?: string;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  confidence: number;
  attributes?: Record<string, any>;
  source: 'ocr' | 'vision' | 'combined';
}

export interface ScreenAnalysis {
  description: string;
  elements: ScreenElement[];
  text: string;
  actions: string[];
  context: string;
  confidence: number;
  processingTime: number;
  sources: {
    ocr: boolean;
    vision: boolean;
    combined: boolean;
  };
}

export class ScreenAnalysisService {
  private screenAnalyzerUrl: string;
  private isInitialized: boolean = false;

  constructor() {
    this.screenAnalyzerUrl = process.env.SCREEN_ANALYZER_URL || 'http://localhost:8010';
    this.initialize();
  }

  private async initialize(): Promise<void> {
    try {
      // Check if screen analyzer service is available
      await this.checkService();
      this.isInitialized = true;
      console.log('✅ Screen Analysis Service initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize Screen Analysis Service:', error);
      this.isInitialized = false;
    }
  }

  private async checkService(): Promise<void> {
    try {
      const response = await axios.get(`${this.screenAnalyzerUrl}/health`, { timeout: 5000 });
      if (!response.data.initialized) {
        throw new Error('Screen Analyzer service not initialized');
      }
      console.log('✅ Screen Analyzer service is available');
    } catch (error) {
      console.error('❌ Screen Analyzer service check failed:', error);
      throw error;
    }
  }

  public async analyzeScreen(imageData: string, options: any = {}): Promise<ScreenAnalysis | null> {
    if (!this.isInitialized) {
      console.warn('⚠️ Screen Analysis Service not initialized');
      return null;
    }

    try {
      console.log('🔍 Analyzing screen content...');

      const response = await axios.post(`${this.screenAnalyzerUrl}/analyze`, {
        image: imageData,
        options: {
          includeOCR: true,
          includeVision: true,
          language: 'eng+sin',
          confidenceThreshold: 60,
          ...options
        }
      });

      if (response.data.success) {
        console.log('✅ Screen analysis completed successfully');
        return response.data.data;
      } else {
        console.error('❌ Screen analysis failed:', response.data.error);
        return null;
      }

    } catch (error) {
      console.error('❌ Screen analysis request failed:', error);
      return null;
    }
  }

  public async findElement(imageData: string, description: string): Promise<ScreenElement | null> {
    if (!this.isInitialized) {
      console.warn('⚠️ Screen Analysis Service not initialized');
      return null;
    }

    try {
      console.log(`🔍 Looking for element: ${description}`);

      const response = await axios.post(`${this.screenAnalyzerUrl}/find-element`, {
        image: imageData,
        description: description
      });

      if (response.data.success && response.data.data.found) {
        console.log('✅ Element found successfully');
        return response.data.data.element;
      } else {
        console.log('❌ Element not found');
        return null;
      }

    } catch (error) {
      console.error('❌ Element finding request failed:', error);
      return null;
    }
  }

  public async getClickableElements(imageData: string): Promise<ScreenElement[]> {
    if (!this.isInitialized) {
      console.warn('⚠️ Screen Analysis Service not initialized');
      return [];
    }

    try {
      console.log('🔍 Finding clickable elements...');

      const response = await axios.post(`${this.screenAnalyzerUrl}/clickable-elements`, {
        image: imageData
      });

      if (response.data.success) {
        console.log(`✅ Found ${response.data.data.count} clickable elements`);
        return response.data.data.elements;
      } else {
        console.error('❌ Clickable elements detection failed:', response.data.error);
        return [];
      }

    } catch (error) {
      console.error('❌ Clickable elements request failed:', error);
      return [];
    }
  }

  public async clickElement(imageData: string, elementDescription: string): Promise<boolean> {
    try {
      // Find the element
      const element = await this.findElement(imageData, elementDescription);
      
      if (!element) {
        console.log('❌ Element not found for clicking');
        return false;
      }

      // Calculate center position
      const centerX = element.position.x + (element.position.width / 2);
      const centerY = element.position.y + (element.position.height / 2);

      console.log(`🖱️ Clicking element at (${centerX}, ${centerY})`);

      // This would integrate with the system controller to perform the click
      // For now, we'll return true as a placeholder
      // In a real implementation, this would call the mouse click function
      
      return true;

    } catch (error) {
      console.error('❌ Element clicking failed:', error);
      return false;
    }
  }

  public async getScreenText(imageData: string): Promise<string> {
    try {
      const analysis = await this.analyzeScreen(imageData);
      return analysis?.text || '';
    } catch (error) {
      console.error('❌ Failed to get screen text:', error);
      return '';
    }
  }

  public async getScreenDescription(imageData: string): Promise<string> {
    try {
      const analysis = await this.analyzeScreen(imageData);
      return analysis?.description || '';
    } catch (error) {
      console.error('❌ Failed to get screen description:', error);
      return '';
    }
  }

  public isReady(): boolean {
    return this.isInitialized;
  }

  public getServiceInfo(): any {
    return {
      service: 'Screen Analysis Service',
      initialized: this.isInitialized,
      screenAnalyzerUrl: this.screenAnalyzerUrl,
      capabilities: {
        screenAnalysis: this.isInitialized,
        elementDetection: this.isInitialized,
        textExtraction: this.isInitialized,
        clickableElements: this.isInitialized
      }
    };
  }
}
