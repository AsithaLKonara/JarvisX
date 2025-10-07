/**
 * JarvisX Camera Service
 * Computer vision and AR capabilities microservice
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import multer from 'multer';
import CameraService from './CameraService';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8021;

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true }));

// Configure multer for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 50 * 1024 * 1024 // 50MB limit
  }
});

// Initialize camera service
const cameraService = CameraService.getInstance();

// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    const stats = await cameraService.getStats();
    
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      camera: {
        isInitialized: cameraService.isInitialized(),
        totalImages: stats.totalImages,
        totalFaces: stats.totalFaces,
        totalObjects: stats.totalObjects,
        totalText: stats.totalText,
        totalARMarkers: stats.totalARMarkers
      }
    });
  } catch (error) {
    res.status(500).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// Analyze image endpoint
app.post('/analyze', upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        error: 'Image file is required'
      });
    }
    
    const options = req.body;
    const analysis = await cameraService.analyzeImage(req.file.buffer, options);
    
    res.json(analysis);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Analyze image from base64 endpoint
app.post('/analyze/base64', async (req, res) => {
  try {
    const { imageData, options } = req.body;
    
    if (!imageData) {
      return res.status(400).json({
        error: 'Image data is required'
      });
    }
    
    const imageBuffer = Buffer.from(imageData, 'base64');
    const analysis = await cameraService.analyzeImage(imageBuffer, options);
    
    res.json(analysis);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Detect faces endpoint
app.post('/faces', upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        error: 'Image file is required'
      });
    }
    
    const analysis = await cameraService.analyzeImage(req.file.buffer, {
      enableFaceDetection: true,
      enableObjectDetection: false,
      enableTextRecognition: false,
      enableAR: false
    });
    
    res.json({
      faces: analysis.faces || [],
      count: analysis.faces?.length || 0
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Detect objects endpoint
app.post('/objects', upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        error: 'Image file is required'
      });
    }
    
    const analysis = await cameraService.analyzeImage(req.file.buffer, {
      enableFaceDetection: false,
      enableObjectDetection: true,
      enableTextRecognition: false,
      enableAR: false
    });
    
    res.json({
      objects: analysis.objects || [],
      count: analysis.objects?.length || 0
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Recognize text endpoint
app.post('/text', upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        error: 'Image file is required'
      });
    }
    
    const analysis = await cameraService.analyzeImage(req.file.buffer, {
      enableFaceDetection: false,
      enableObjectDetection: false,
      enableTextRecognition: true,
      enableAR: false
    });
    
    res.json({
      text: analysis.text || [],
      count: analysis.text?.length || 0
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Detect AR markers endpoint
app.post('/ar-markers', upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        error: 'Image file is required'
      });
    }
    
    const analysis = await cameraService.analyzeImage(req.file.buffer, {
      enableFaceDetection: false,
      enableObjectDetection: false,
      enableTextRecognition: false,
      enableAR: true
    });
    
    res.json({
      markers: analysis.arMarkers || [],
      count: analysis.arMarkers?.length || 0
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Capture screenshot endpoint
app.post('/screenshot', async (req, res) => {
  try {
    const options = req.body;
    const screenshot = await cameraService.captureScreenshot(options);
    
    res.set('Content-Type', 'image/jpeg');
    res.send(screenshot);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Start video stream endpoint
app.post('/stream/start', async (req, res) => {
  try {
    const config = req.body;
    const streamId = await cameraService.processVideoStream(config);
    
    res.json({
      success: true,
      streamId,
      message: 'Video stream started'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Stop video stream endpoint
app.post('/stream/stop/:streamId', async (req, res) => {
  try {
    const { streamId } = req.params;
    const success = await cameraService.stopVideoStream(streamId);
    
    res.json({
      success,
      message: success ? 'Video stream stopped' : 'Failed to stop video stream'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get analysis history endpoint
app.get('/history', async (req, res) => {
  try {
    const { limit = 100 } = req.query;
    const history = cameraService.getAnalysisHistory(Number(limit));
    
    res.json({
      history,
      total: history.length,
      limit: Number(limit)
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Get statistics endpoint
app.get('/stats', async (req, res) => {
  try {
    const stats = cameraService.getStats();
    res.json(stats);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Get configuration endpoint
app.get('/config', async (req, res) => {
  try {
    const config = cameraService.getConfig();
    res.json(config);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Update configuration endpoint
app.put('/config', async (req, res) => {
  try {
    const newConfig = req.body;
    await cameraService.updateConfig(newConfig);
    
    res.json({
      success: true,
      message: 'Configuration updated',
      config: cameraService.getConfig()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Clear history endpoint
app.delete('/history', async (req, res) => {
  try {
    await cameraService.clearHistory();
    
    res.json({
      success: true,
      message: 'Analysis history cleared'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Error handling middleware
app.use((error: any, req: any, res: any, next: any) => {
  console.error('❌ Camera service error:', error);
  res.status(500).json({
    error: 'Internal server error',
    message: error.message,
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    path: req.originalUrl,
    timestamp: new Date().toISOString()
  });
});

// Start server
const startServer = async () => {
  try {
    // Initialize camera service
    await cameraService.initialize();
    
    // Start server
    app.listen(PORT, () => {
      console.log(`🚀 Camera service running on port ${PORT}`);
      console.log(`📊 Health check: http://localhost:${PORT}/health`);
      console.log(`📈 Stats: http://localhost:${PORT}/stats`);
      console.log(`📷 Config: http://localhost:${PORT}/config`);
    });
  } catch (error) {
    console.error('❌ Failed to start camera service:', error);
    process.exit(1);
  }
};

startServer();

export default app;
