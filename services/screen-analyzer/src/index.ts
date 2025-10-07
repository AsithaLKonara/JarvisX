/**
 * JarvisX Screen Analyzer Service
 * Main service that combines OCR + Vision + Element Detection
 * Port: 8010
 */

import express from 'express';
import cors from 'cors';
import { ScreenAnalyzer } from './ScreenAnalyzer';
import dotenv from 'dotenv';

dotenv.config();

class JarvisXScreenAnalyzerService {
  private app: express.Application;
  private screenAnalyzer: ScreenAnalyzer;

  constructor() {
    this.app = express();
    this.screenAnalyzer = new ScreenAnalyzer();
    this.setupMiddleware();
    this.setupRoutes();
  }

  private setupMiddleware(): void {
    this.app.use(cors());
    this.app.use(express.json({ limit: '50mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '50mb' }));
  }

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        service: 'jarvisx-screen-analyzer',
        timestamp: new Date().toISOString(),
        initialized: this.screenAnalyzer.isReady(),
        capabilities: {
          screenAnalysis: this.screenAnalyzer.isReady(),
          elementDetection: this.screenAnalyzer.isReady(),
          textExtraction: this.screenAnalyzer.isReady(),
          actionSuggestion: this.screenAnalyzer.isReady()
        }
      });
    });

    // Comprehensive screen analysis
    this.app.post('/analyze', async (req, res) => {
      try {
        const { image, options = {} } = req.body;

        if (!image) {
          return res.status(400).json({
            success: false,
            error: 'No image provided'
          });
        }

        console.log('🔍 Starting comprehensive screen analysis...');

        const analysis = await this.screenAnalyzer.analyzeScreen(image, options);

        res.json({
          success: true,
          data: analysis
        });

      } catch (error: any) {
        console.error('❌ Screen analysis failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Find specific element
    this.app.post('/find-element', async (req, res) => {
      try {
        const { image, description } = req.body;

        if (!image || !description) {
          return res.status(400).json({
            success: false,
            error: 'Image and description required'
          });
        }

        console.log(`🔍 Looking for element: ${description}`);

        const element = await this.screenAnalyzer.findElement(image, description);

        res.json({
          success: true,
          data: {
            found: !!element,
            element: element
          }
        });

      } catch (error: any) {
        console.error('❌ Element finding failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get clickable elements
    this.app.post('/clickable-elements', async (req, res) => {
      try {
        const { image } = req.body;

        if (!image) {
          return res.status(400).json({
            success: false,
            error: 'Image required'
          });
        }

        console.log('🔍 Finding clickable elements...');

        const elements = await this.screenAnalyzer.getClickableElements(image);

        res.json({
          success: true,
          data: {
            elements,
            count: elements.length
          }
        });

      } catch (error: any) {
        console.error('❌ Clickable elements detection failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Service info
    this.app.get('/info', (req, res) => {
      res.json({
        success: true,
        data: {
          service: 'JarvisX Screen Analyzer',
          version: '1.0.0',
          port: 8010,
          status: this.screenAnalyzer.isReady() ? 'ready' : 'initializing',
          features: [
            'Comprehensive screen analysis',
            'OCR + Vision integration',
            'Element detection and localization',
            'Clickable element identification',
            'Multi-language text recognition',
            'Action suggestion',
            'Real-time screen understanding'
          ],
          dependencies: {
            ocr: 'Port 8011',
            vision: 'Port 8005'
          }
        }
      });
    });
  }

  public async start(): Promise<void> {
    const PORT = process.env.SCREEN_ANALYZER_PORT || 8010;
    
    this.app.listen(PORT, '0.0.0.0', () => {
      console.log(`🚀 JarvisX Screen Analyzer running on port ${PORT}`);
      console.log(`🔍 Status: ${this.screenAnalyzer.isReady() ? 'Ready' : 'Initializing...'}`);
      console.log(`📊 Capabilities: OCR + Vision + Element Detection`);
    });
  }
}

// Start the Screen Analyzer service
const screenAnalyzerService = new JarvisXScreenAnalyzerService();

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('🛑 Shutting down Screen Analyzer service...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('🛑 Shutting down Screen Analyzer service...');
  process.exit(0);
});

screenAnalyzerService.start().catch((error) => {
  console.error('Failed to start Screen Analyzer service:', error);
  process.exit(1);
});

export default screenAnalyzerService;
