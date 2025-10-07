/**
 * JarvisX Translation Service
 * Multi-language translation and localization microservice
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import TranslationService from './TranslationService';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8020;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Initialize translation service
const translationService = TranslationService.getInstance();

// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    const stats = await translationService.getStats();
    
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      translation: {
        isInitialized: translationService.isInitialized(),
        totalTranslations: stats.totalTranslations,
        supportedLanguages: translationService.getSupportedLanguages().length,
        averageConfidence: stats.averageConfidence
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

// Translate text endpoint
app.post('/translate', async (req, res) => {
  try {
    const { text, sourceLanguage, targetLanguage, context, domain, userId } = req.body;
    
    if (!text || !targetLanguage) {
      return res.status(400).json({
        error: 'Text and target language are required'
      });
    }
    
    const request = {
      id: `trans_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      text,
      sourceLanguage,
      targetLanguage,
      context,
      domain,
      timestamp: Date.now(),
      userId
    };
    
    const result = await translationService.translate(request);
    
    res.json(result);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Batch translate endpoint
app.post('/translate/batch', async (req, res) => {
  try {
    const { requests } = req.body;
    
    if (!Array.isArray(requests) || requests.length === 0) {
      return res.status(400).json({
        error: 'Requests array is required'
      });
    }
    
    if (requests.length > 100) {
      return res.status(400).json({
        error: 'Maximum 100 translations per batch'
      });
    }
    
    const results = await translationService.batchTranslate(requests);
    
    res.json({
      results,
      total: results.length,
      successful: results.length,
      failed: requests.length - results.length
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Detect language endpoint
app.post('/detect', async (req, res) => {
  try {
    const { text } = req.body;
    
    if (!text) {
      return res.status(400).json({
        error: 'Text is required'
      });
    }
    
    const language = await translationService.detectLanguage(text);
    const languageInfo = translationService.getLanguageInfo(language);
    
    res.json({
      language,
      languageInfo,
      confidence: 0.8 // Simulated confidence
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Get supported languages endpoint
app.get('/languages', async (req, res) => {
  try {
    const languages = translationService.getSupportedLanguages();
    
    res.json({
      languages,
      total: languages.length
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Get language info endpoint
app.get('/languages/:code', async (req, res) => {
  try {
    const { code } = req.params;
    const languageInfo = translationService.getLanguageInfo(code);
    
    if (!languageInfo) {
      return res.status(404).json({
        error: 'Language not found'
      });
    }
    
    res.json(languageInfo);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Get translation history endpoint
app.get('/history', async (req, res) => {
  try {
    const { limit = 100 } = req.query;
    const history = translationService.getTranslationHistory(Number(limit));
    
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
    const stats = translationService.getStats();
    res.json(stats);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Clear history endpoint
app.delete('/history', async (req, res) => {
  try {
    await translationService.clearHistory();
    
    res.json({
      success: true,
      message: 'Translation history cleared'
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Error handling middleware
app.use((error: any, req: any, res: any, next: any) => {
  console.error('❌ Translation service error:', error);
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
    // Initialize translation service
    await translationService.initialize();
    
    // Start server
    app.listen(PORT, () => {
      console.log(`🚀 Translation service running on port ${PORT}`);
      console.log(`📊 Health check: http://localhost:${PORT}/health`);
      console.log(`📈 Stats: http://localhost:${PORT}/stats`);
      console.log(`🌍 Languages: http://localhost:${PORT}/languages`);
    });
  } catch (error) {
    console.error('❌ Failed to start translation service:', error);
    process.exit(1);
  }
};

startServer();

export default app;
