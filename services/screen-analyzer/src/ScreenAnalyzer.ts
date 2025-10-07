/**
 * JarvisX Screen Analyzer
 * Combines OCR + Vision + Element Detection for complete screen understanding
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

export class ScreenAnalyzer {
  private ocrServiceUrl: string;
  private visionServiceUrl: string;
  private isInitialized: boolean = false;

  constructor() {
    this.ocrServiceUrl = process.env.OCR_SERVICE_URL || 'http://localhost:8011';
    this.visionServiceUrl = process.env.VISION_SERVICE_URL || 'http://localhost:8005';
    this.initialize();
  }

  private async initialize(): Promise<void> {
    try {
      // Check if services are available
      await this.checkServices();
      this.isInitialized = true;
      console.log('✅ Screen Analyzer initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize Screen Analyzer:', error);
      this.isInitialized = false;
    }
  }

  private async checkServices(): Promise<void> {
    try {
      // Check OCR service
      const ocrResponse = await axios.get(`${this.ocrServiceUrl}/health`, { timeout: 5000 });
      if (!ocrResponse.data.initialized) {
        throw new Error('OCR service not initialized');
      }

      // Check Vision service
      const visionResponse = await axios.get(`${this.visionServiceUrl}/health`, { timeout: 5000 });
      if (!visionResponse.data.initialized) {
        throw new Error('Vision service not initialized');
      }

      console.log('✅ All services are available');
    } catch (error) {
      console.error('❌ Service check failed:', error);
      throw error;
    }
  }

  public async analyzeScreen(imageData: string, options: any = {}): Promise<ScreenAnalysis> {
    if (!this.isInitialized) {
      throw new Error('Screen Analyzer not initialized');
    }

    const startTime = Date.now();
    const { 
      includeOCR = true,
      includeVision = true,
      language = 'eng+sin',
      confidenceThreshold = 60
    } = options;

    try {
      console.log('🔍 Starting comprehensive screen analysis...');

      // Run OCR and Vision analysis in parallel
      const [ocrResult, visionResult] = await Promise.allSettled([
        includeOCR ? this.performOCR(imageData, { language, confidenceThreshold }) : null,
        includeVision ? this.performVisionAnalysis(imageData, options) : null
      ]);

      // Process results
      const ocrData = ocrResult.status === 'fulfilled' ? ocrResult.value : null;
      const visionData = visionResult.status === 'fulfilled' ? visionResult.value : null;

      // Combine results
      const analysis = this.combineResults(ocrData, visionData, options);

      const processingTime = Date.now() - startTime;
      analysis.processingTime = processingTime;

      console.log(`✅ Screen analysis completed in ${processingTime}ms`);
      return analysis;

    } catch (error) {
      console.error('❌ Screen analysis failed:', error);
      throw error;
    }
  }

  private async performOCR(imageData: string, options: any): Promise<any> {
    try {
      const response = await axios.post(`${this.ocrServiceUrl}/extract`, {
        image: imageData,
        options: {
          language: options.language,
          confidence_threshold: options.confidenceThreshold,
          preprocessing: true
        }
      });

      return response.data.data;
    } catch (error) {
      console.error('❌ OCR analysis failed:', error);
      return null;
    }
  }

  private async performVisionAnalysis(imageData: string, options: any): Promise<any> {
    try {
      const response = await axios.post(`${this.visionServiceUrl}/analyze`, {
        image: imageData,
        prompt: options.prompt || 'Analyze this screen and identify all interactive elements',
        options: {
          includeElements: true,
          includeActions: true,
          includeContext: true,
          language: options.language || 'en'
        }
      });

      return response.data.data;
    } catch (error) {
      console.error('❌ Vision analysis failed:', error);
      return null;
    }
  }

  private combineResults(ocrData: any, visionData: any, options: any): ScreenAnalysis {
    const elements: ScreenElement[] = [];
    let description = '';
    let context = '';
    let actions: string[] = [];
    let confidence = 0;
    let text = '';

    // Process OCR data
    if (ocrData) {
      text = ocrData.text || '';
      
      // Convert OCR words to elements
      if (ocrData.words) {
        ocrData.words.forEach((word: any) => {
          elements.push({
            type: 'text',
            text: word.text,
            position: {
              x: word.bbox.x0,
              y: word.bbox.y0,
              width: word.bbox.x1 - word.bbox.x0,
              height: word.bbox.y1 - word.bbox.y0
            },
            confidence: word.confidence,
            source: 'ocr'
          });
        });
      }

      confidence += ocrData.confidence || 0;
    }

    // Process Vision data
    if (visionData) {
      description = visionData.description || description;
      context = visionData.context || context;
      actions = visionData.actions || actions;

      // Convert Vision elements
      if (visionData.elements) {
        visionData.elements.forEach((element: any) => {
          elements.push({
            type: element.type || 'unknown',
            text: element.text,
            position: element.position || { x: 0, y: 0, width: 0, height: 0 },
            confidence: element.confidence || 0,
            attributes: element.attributes,
            source: 'vision'
          });
        });
      }

      confidence += visionData.confidence || 0;
    }

    // Remove duplicates and merge similar elements
    const mergedElements = this.mergeElements(elements);

    // Calculate average confidence
    const avgConfidence = confidence / ((ocrData ? 1 : 0) + (visionData ? 1 : 0));

    return {
      description: description || 'Screen content analyzed',
      elements: mergedElements,
      text: text,
      actions: actions,
      context: context || 'General screen content',
      confidence: Math.round(avgConfidence),
      processingTime: 0, // Will be set by caller
      sources: {
        ocr: !!ocrData,
        vision: !!visionData,
        combined: !!(ocrData && visionData)
      }
    };
  }

  private mergeElements(elements: ScreenElement[]): ScreenElement[] {
    const merged: ScreenElement[] = [];
    const processed: Set<string> = new Set();

    elements.forEach(element => {
      const key = `${element.type}-${element.position.x}-${element.position.y}`;
      
      if (processed.has(key)) {
        // Find existing element and merge
        const existing = merged.find(e => 
          e.type === element.type &&
          Math.abs(e.position.x - element.position.x) < 10 &&
          Math.abs(e.position.y - element.position.y) < 10
        );

        if (existing) {
          // Merge attributes and use higher confidence
          existing.confidence = Math.max(existing.confidence, element.confidence);
          existing.attributes = { ...existing.attributes, ...element.attributes };
          existing.source = 'combined';
          
          if (element.text && !existing.text) {
            existing.text = element.text;
          }
        }
      } else {
        merged.push(element);
        processed.add(key);
      }
    });

    return merged;
  }

  public async findElement(imageData: string, description: string): Promise<ScreenElement | null> {
    try {
      const response = await axios.post(`${this.visionServiceUrl}/find-element`, {
        image: imageData,
        elementDescription: description
      });

      if (response.data.success && response.data.data.found) {
        return {
          type: response.data.data.element.type,
          text: response.data.data.element.text,
          position: response.data.data.element.position,
          confidence: response.data.data.element.confidence,
          source: 'vision'
        };
      }

      return null;
    } catch (error) {
      console.error('❌ Element finding failed:', error);
      return null;
    }
  }

  public async getClickableElements(imageData: string): Promise<ScreenElement[]> {
    try {
      const response = await axios.post(`${this.visionServiceUrl}/clickable-elements`, {
        image: imageData
      });

      if (response.data.success) {
        return response.data.data.elements.map((element: any) => ({
          type: element.type,
          text: element.text,
          position: element.position,
          confidence: element.confidence,
          attributes: element.features ? { features: element.features } : {},
          source: 'vision'
        }));
      }

      return [];
    } catch (error) {
      console.error('❌ Clickable elements detection failed:', error);
      return [];
    }
  }

  public isReady(): boolean {
    return this.isInitialized;
  }
}
