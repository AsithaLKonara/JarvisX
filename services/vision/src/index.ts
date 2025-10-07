/**
 * JarvisX Vision Service
 * GPT-4 Vision integration for screen analysis and element detection
 * Port: 8005
 */

import express from 'express';
import cors from 'cors';
import multer from 'multer';
import sharp from 'sharp';
import OpenAI from 'openai';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';

dotenv.config();

interface Element {
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
}

interface ScreenAnalysis {
  description: string;
  elements: Element[];
  actions: string[];
  context: string;
  confidence: number;
}

class JarvisXVisionService {
  private app: express.Application;
  private openai: OpenAI;
  private isInitialized: boolean = false;

  constructor() {
    this.app = express();
    this.initializeOpenAI();
    this.setupMiddleware();
    this.setupRoutes();
  }

  private initializeOpenAI(): void {
    try {
      if (!process.env.OPENAI_API_KEY) {
        throw new Error('OPENAI_API_KEY not found in environment variables');
      }

      this.openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
      });

      this.isInitialized = true;
      console.log('✅ OpenAI client initialized successfully');
      
    } catch (error) {
      console.error('❌ Failed to initialize OpenAI client:', error);
      this.isInitialized = false;
    }
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

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        service: 'jarvisx-vision',
        timestamp: new Date().toISOString(),
        initialized: this.isInitialized,
        capabilities: {
          screenAnalysis: this.isInitialized,
          elementDetection: this.isInitialized,
          actionSuggestion: this.isInitialized,
          gpt4Vision: this.isInitialized
        }
      });
    });

    // Analyze screen content
    this.app.post('/analyze', async (req, res) => {
      try {
        if (!this.isInitialized) {
          return res.status(503).json({
            success: false,
            error: 'Vision service not initialized'
          });
        }

        const { image, prompt, options = {} } = req.body;
        const { 
          includeElements = true,
          includeActions = true,
          includeContext = true,
          language = 'en'
        } = options;

        if (!image) {
          return res.status(400).json({
            success: false,
            error: 'No image provided'
          });
        }

        console.log('🔍 Analyzing screen content...');

        // Process image for GPT-4 Vision
        const processedImage = await this.preprocessImageForVision(image);
        
        // Create analysis prompt
        const analysisPrompt = this.createAnalysisPrompt(prompt, {
          includeElements,
          includeActions,
          includeContext,
          language
        });

        // Call GPT-4 Vision
        const response = await this.openai.chat.completions.create({
          model: "gpt-4-vision-preview",
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: analysisPrompt
                },
                {
                  type: "image_url",
                  image_url: {
                    url: `data:image/png;base64,${processedImage}`,
                    detail: "high"
                  }
                }
              ]
            }
          ],
          max_tokens: 2000,
          temperature: 0.1
        });

        const analysis = this.parseAnalysisResponse(response.choices[0].message.content || '');

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

    // Find specific element on screen
    this.app.post('/find-element', async (req, res) => {
      try {
        const { image, elementDescription, options = {} } = req.body;
        
        if (!image || !elementDescription) {
          return res.status(400).json({
            success: false,
            error: 'Image and element description required'
          });
        }

        console.log(`🔍 Looking for element: ${elementDescription}`);

        const processedImage = await this.preprocessImageForVision(image);
        
        const prompt = `Look at this screen and find the element described as: "${elementDescription}"

        Please identify:
        1. The exact location (x, y coordinates)
        2. The size (width, height)
        3. The element type (button, text, input, etc.)
        4. Any visible text on the element
        5. Your confidence level (0-100)

        Respond in JSON format:
        {
          "found": true/false,
          "element": {
            "type": "button",
            "text": "Click Me",
            "position": {"x": 100, "y": 200, "width": 80, "height": 30},
            "confidence": 95
          }
        }`;

        const response = await this.openai.chat.completions.create({
          model: "gpt-4-vision-preview",
          messages: [
            {
              role: "user",
              content: [
                { type: "text", text: prompt },
                {
                  type: "image_url",
                  image_url: {
                    url: `data:image/png;base64,${processedImage}`,
                    detail: "high"
                  }
                }
              ]
            }
          ],
          max_tokens: 1000,
          temperature: 0.1
        });

        const result = JSON.parse(response.choices[0].message.content || '{}');

        res.json({
          success: true,
          data: result
        });

      } catch (error: any) {
        console.error('❌ Element detection failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get clickable elements
    this.app.post('/clickable-elements', async (req, res) => {
      try {
        const { image, options = {} } = req.body;
        
        if (!image) {
          return res.status(400).json({
            success: false,
            error: 'Image required'
          });
        }

        console.log('🔍 Finding clickable elements...');

        const processedImage = await this.preprocessImageForVision(image);
        
        const prompt = `Analyze this screen and identify all clickable elements (buttons, links, icons, etc.).

        For each element, provide:
        - Type (button, link, icon, etc.)
        - Text content
        - Position (x, y, width, height)
        - Confidence level
        - Any distinguishing features

        Respond in JSON format:
        {
          "elements": [
            {
              "type": "button",
              "text": "Submit",
              "position": {"x": 100, "y": 200, "width": 80, "height": 30},
              "confidence": 95,
              "features": ["blue background", "white text"]
            }
          ]
        }`;

        const response = await this.openai.chat.completions.create({
          model: "gpt-4-vision-preview",
          messages: [
            {
              role: "user",
              content: [
                { type: "text", text: prompt },
                {
                  type: "image_url",
                  image_url: {
                    url: `data:image/png;base64,${processedImage}`,
                    detail: "high"
                  }
                }
              ]
            }
          ],
          max_tokens: 2000,
          temperature: 0.1
        });

        const result = JSON.parse(response.choices[0].message.content || '{"elements": []}');

        res.json({
          success: true,
          data: result
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
          service: 'JarvisX Vision Service',
          version: '1.0.0',
          port: 8005,
          status: this.isInitialized ? 'ready' : 'initializing',
          features: [
            'GPT-4 Vision integration',
            'Screen content analysis',
            'Element detection and localization',
            'Clickable element identification',
            'Action suggestion',
            'Multi-language support'
          ]
        }
      });
    });
  }

  private createAnalysisPrompt(userPrompt: string, options: any): string {
    let prompt = `Analyze this screen image and provide a comprehensive analysis.\n\n`;

    if (userPrompt) {
      prompt += `User Request: ${userPrompt}\n\n`;
    }

    prompt += `Please provide:\n`;

    if (options.includeContext) {
      prompt += `1. A detailed description of what's visible on the screen\n`;
    }

    if (options.includeElements) {
      prompt += `2. A list of all interactive elements (buttons, links, inputs, etc.) with their positions\n`;
    }

    if (options.includeActions) {
      prompt += `3. Suggested actions the user might want to perform\n`;
    }

    prompt += `\nRespond in JSON format with the following structure:
    {
      "description": "Detailed description of the screen content",
      "elements": [
        {
          "type": "button",
          "text": "Click Me",
          "position": {"x": 100, "y": 200, "width": 80, "height": 30},
          "confidence": 95,
          "attributes": {"color": "blue", "enabled": true}
        }
      ],
      "actions": ["Click the blue button", "Fill the form", "Navigate to settings"],
      "context": "This appears to be a login form",
      "confidence": 90
    }`;

    return prompt;
  }

  private parseAnalysisResponse(content: string): ScreenAnalysis {
    try {
      // Try to extract JSON from the response
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      
      // Fallback parsing
      return {
        description: content,
        elements: [],
        actions: [],
        context: '',
        confidence: 50
      };
    } catch (error) {
      console.error('❌ Failed to parse analysis response:', error);
      return {
        description: content,
        elements: [],
        actions: [],
        context: '',
        confidence: 50
      };
    }
  }

  private async preprocessImageForVision(imageData: string): Promise<string> {
    try {
      // Process image for optimal GPT-4 Vision analysis
      const processed = await sharp(Buffer.from(imageData, 'base64'))
        .resize(1920, 1080, { // Standard resolution
          kernel: sharp.kernel.lanczos3,
          withoutEnlargement: true
        })
        .sharpen() // Enhance details
        .png({ quality: 90 })
        .toBuffer();

      return processed.toString('base64');

    } catch (error) {
      console.error('❌ Image preprocessing failed:', error);
      throw error;
    }
  }

  public async start(): Promise<void> {
    const PORT = process.env.VISION_PORT || 8005;
    
    this.app.listen(PORT, '0.0.0.0', () => {
      console.log(`🚀 JarvisX Vision Service running on port ${PORT}`);
      console.log(`👁️  GPT-4 Vision: ${this.isInitialized ? 'Ready' : 'Not initialized'}`);
      console.log(`🎯 Element Detection: Active`);
    });
  }
}

// Start the Vision service
const visionService = new JarvisXVisionService();

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('🛑 Shutting down Vision service...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('🛑 Shutting down Vision service...');
  process.exit(0);
});

visionService.start().catch((error) => {
  console.error('Failed to start Vision service:', error);
  process.exit(1);
});

export default visionService;
