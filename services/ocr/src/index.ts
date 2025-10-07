/**
 * JarvisX OCR Service
 * Text extraction from screens with Sinhala + English support
 * Port: 8011
 */

import express from 'express';
import cors from 'cors';
import multer from 'multer';
import sharp from 'sharp';
import { createWorker } from 'tesseract.js';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';

dotenv.config();

class JarvisXOCRService {
  private app: express.Application;
  private worker: any;
  private isInitialized: boolean = false;

  constructor() {
    this.app = express();
    this.setupMiddleware();
    this.setupRoutes();
    this.initializeTesseract();
  }

  private setupMiddleware(): void {
    this.app.use(cors());
    this.app.use(express.json({ limit: '50mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '50mb' }));

    // Configure multer for file uploads
    const storage = multer.memoryStorage();
    const upload = multer({ 
      storage,
      limits: { fileSize: 50 * 1024 * 1024 } // 50MB limit
    });
    this.app.use(upload.single('image'));
  }

  private async initializeTesseract(): Promise<void> {
    try {
      console.log('🔍 Initializing Tesseract OCR...');
      
      this.worker = await createWorker({
        logger: m => console.log(m)
      });

      // Load languages: English + Sinhala
      await this.worker.loadLanguage('eng+sin');
      await this.worker.initialize('eng+sin');
      
      // Configure OCR settings for better accuracy
      await this.worker.setParameters({
        tessedit_char_whitelist: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,!?;:()[]{}\'"-+=/\\|@#$%^&*~`<>',
        tessedit_pageseg_mode: '6', // Uniform block of text
        tessedit_ocr_engine_mode: '3' // Default neural nets LSTM engine
      });

      this.isInitialized = true;
      console.log('✅ Tesseract OCR initialized successfully');
      
    } catch (error) {
      console.error('❌ Failed to initialize Tesseract OCR:', error);
      this.isInitialized = false;
    }
  }

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        service: 'jarvisx-ocr',
        timestamp: new Date().toISOString(),
        initialized: this.isInitialized,
        languages: ['eng', 'sin'],
        capabilities: {
          textExtraction: this.isInitialized,
          multiLanguage: true,
          imagePreprocessing: true,
          batchProcessing: true
        }
      });
    });

    // Extract text from image
    this.app.post('/extract', async (req, res) => {
      try {
        if (!this.isInitialized) {
          return res.status(503).json({
            success: false,
            error: 'OCR service not initialized'
          });
        }

        const { image, options = {} } = req.body;
        const { 
          language = 'eng+sin',
          preprocessing = true,
          confidence_threshold = 60,
          region = null // {x, y, width, height} for specific region
        } = options;

        if (!image) {
          return res.status(400).json({
            success: false,
            error: 'No image provided'
          });
        }

        console.log('🔍 Processing OCR request...');

        // Process image
        let processedImage = image;
        if (preprocessing) {
          processedImage = await this.preprocessImage(image, region);
        }

        // Extract text
        const result = await this.worker.recognize(processedImage);
        
        // Filter results by confidence
        const filteredText = result.data.words
          .filter((word: any) => word.confidence >= confidence_threshold)
          .map((word: any) => ({
            text: word.text,
            confidence: word.confidence,
            bbox: word.bbox
          }));

        const response = {
          success: true,
          data: {
            text: result.data.text,
            confidence: result.data.confidence,
            words: filteredText,
            lines: result.data.lines,
            blocks: result.data.blocks,
            language: language,
            processing_time: result.data.executionTime,
            region: region
          }
        };

        console.log(`✅ OCR completed: ${filteredText.length} words extracted`);
        res.json(response);

      } catch (error: any) {
        console.error('❌ OCR processing failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Extract text from specific screen region
    this.app.post('/extract-region', async (req, res) => {
      try {
        const { image, region, options = {} } = req.body;
        
        if (!image || !region) {
          return res.status(400).json({
            success: false,
            error: 'Image and region required'
          });
        }

        const { x, y, width, height } = region;
        
        // Crop image to region
        const croppedImage = await sharp(Buffer.from(image, 'base64'))
          .extract({ left: x, top: y, width, height })
          .png()
          .toBuffer();

        // Process cropped image
        const result = await this.worker.recognize(croppedImage);

        res.json({
          success: true,
          data: {
            text: result.data.text,
            confidence: result.data.confidence,
            words: result.data.words,
            region: region,
            processing_time: result.data.executionTime
          }
        });

      } catch (error: any) {
        console.error('❌ Region OCR failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Batch process multiple images
    this.app.post('/batch-extract', async (req, res) => {
      try {
        const { images, options = {} } = req.body;
        
        if (!Array.isArray(images) || images.length === 0) {
          return res.status(400).json({
            success: false,
            error: 'Images array required'
          });
        }

        console.log(`🔄 Processing batch: ${images.length} images`);

        const results = await Promise.all(
          images.map(async (imageData: any, index: number) => {
            try {
              const result = await this.worker.recognize(imageData.image);
              return {
                index,
                success: true,
                data: {
                  text: result.data.text,
                  confidence: result.data.confidence,
                  processing_time: result.data.executionTime
                }
              };
            } catch (error: any) {
              return {
                index,
                success: false,
                error: error.message
              };
            }
          })
        );

        res.json({
          success: true,
          data: {
            results,
            total: images.length,
            successful: results.filter(r => r.success).length,
            failed: results.filter(r => !r.success).length
          }
        });

      } catch (error: any) {
        console.error('❌ Batch OCR failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get supported languages
    this.app.get('/languages', (req, res) => {
      res.json({
        success: true,
        data: {
          supported: ['eng', 'sin'],
          default: 'eng+sin',
          descriptions: {
            eng: 'English',
            sin: 'Sinhala (සිංහල)'
          }
        }
      });
    });

    // Service info
    this.app.get('/info', (req, res) => {
      res.json({
        success: true,
        data: {
          service: 'JarvisX OCR Service',
          version: '1.0.0',
          port: 8011,
          status: this.isInitialized ? 'ready' : 'initializing',
          features: [
            'Multi-language OCR (English + Sinhala)',
            'Image preprocessing',
            'Region-based extraction',
            'Batch processing',
            'Confidence filtering',
            'High accuracy text recognition'
          ]
        }
      });
    });
  }

  private async preprocessImage(imageData: string, region?: any): Promise<Buffer> {
    try {
      let image = sharp(Buffer.from(imageData, 'base64'));

      // Crop to region if specified
      if (region) {
        image = image.extract({
          left: region.x,
          top: region.y,
          width: region.width,
          height: region.height
        });
      }

      // Apply preprocessing for better OCR accuracy
      const processed = await image
        .resize(null, 2000, { // Scale up for better recognition
          kernel: sharp.kernel.lanczos3,
          withoutEnlargement: false
        })
        .sharpen() // Enhance text edges
        .normalize() // Normalize contrast
        .threshold(128) // Convert to black and white
        .png()
        .toBuffer();

      return processed;

    } catch (error) {
      console.error('❌ Image preprocessing failed:', error);
      throw error;
    }
  }

  public async start(): Promise<void> {
    const PORT = process.env.OCR_PORT || 8011;
    
    this.app.listen(PORT, '0.0.0.0', () => {
      console.log(`🚀 JarvisX OCR Service running on port ${PORT}`);
      console.log(`🔍 Languages: English + Sinhala`);
      console.log(`📊 Status: ${this.isInitialized ? 'Ready' : 'Initializing...'}`);
    });
  }

  public async stop(): Promise<void> {
    if (this.worker) {
      await this.worker.terminate();
    }
  }
}

// Start the OCR service
const ocrService = new JarvisXOCRService();

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('🛑 Shutting down OCR service...');
  await ocrService.stop();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('🛑 Shutting down OCR service...');
  await ocrService.stop();
  process.exit(0);
});

ocrService.start().catch((error) => {
  console.error('Failed to start OCR service:', error);
  process.exit(1);
});

export default ocrService;
