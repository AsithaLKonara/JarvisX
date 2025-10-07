/**
 * JarvisX Wake Word Detection Service
 * Always-listening voice activation microservice
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import WakeWordDetector from './WakeWordDetector';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8019;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Initialize wake word detector
const wakeWordDetector = WakeWordDetector.getInstance();

// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    const stats = await wakeWordDetector.getStats();
    
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      wakeWord: {
        isListening: wakeWordDetector.isCurrentlyListening(),
        activeStreams: stats.activeStreams,
        detectionCount: stats.detectionCount,
        lastDetection: stats.lastDetection
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

// Start listening endpoint
app.post('/listen', async (req, res) => {
  try {
    const config = req.body;
    const streamId = await wakeWordDetector.startListening(config);
    
    res.json({
      success: true,
      streamId,
      message: 'Started listening for wake words'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Stop listening endpoint
app.post('/stop/:streamId', async (req, res) => {
  try {
    const { streamId } = req.params;
    const success = await wakeWordDetector.stopListening(streamId);
    
    if (success) {
      res.json({
        success: true,
        message: 'Stopped listening for wake words'
      });
    } else {
      res.status(404).json({
        success: false,
        error: 'Stream not found'
      });
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Stop all listening endpoint
app.post('/stop-all', async (req, res) => {
  try {
    await wakeWordDetector.stopAllListening();
    
    res.json({
      success: true,
      message: 'Stopped all listening'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get active streams endpoint
app.get('/streams', async (req, res) => {
  try {
    const streams = wakeWordDetector.getActiveStreams();
    
    res.json({
      streams: streams.map(stream => ({
        id: stream.id,
        isActive: stream.isActive,
        startTime: stream.startTime,
        lastActivity: stream.lastActivity,
        bufferSize: stream.buffer.length,
        config: stream.config
      }))
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Get stream details endpoint
app.get('/streams/:streamId', async (req, res) => {
  try {
    const { streamId } = req.params;
    const stream = wakeWordDetector.getStream(streamId);
    
    if (!stream) {
      return res.status(404).json({
        error: 'Stream not found'
      });
    }
    
    res.json({
      id: stream.id,
      isActive: stream.isActive,
      startTime: stream.startTime,
      lastActivity: stream.lastActivity,
      bufferSize: stream.buffer.length,
      config: stream.config
    });
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Update stream config endpoint
app.put('/streams/:streamId/config', async (req, res) => {
  try {
    const { streamId } = req.params;
    const config = req.body;
    
    const success = await wakeWordDetector.updateConfig(streamId, config);
    
    if (success) {
      res.json({
        success: true,
        message: 'Config updated successfully'
      });
    } else {
      res.status(404).json({
        success: false,
        error: 'Stream not found'
      });
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Process audio data endpoint
app.post('/streams/:streamId/audio', async (req, res) => {
  try {
    const { streamId } = req.params;
    const { audioData } = req.body;
    
    if (!audioData) {
      return res.status(400).json({
        error: 'Audio data is required'
      });
    }
    
    const buffer = Buffer.from(audioData, 'base64');
    await wakeWordDetector.processAudioData(streamId, buffer);
    
    res.json({
      success: true,
      message: 'Audio data processed'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get statistics endpoint
app.get('/stats', async (req, res) => {
  try {
    const stats = await wakeWordDetector.getStats();
    res.json(stats);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Error handling middleware
app.use((error: any, req: any, res: any, next: any) => {
  console.error('❌ Wake word service error:', error);
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

// Create HTTP server
const server = createServer(app);

// Create WebSocket server
const wss = new WebSocketServer({ server });

// WebSocket connection handling
wss.on('connection', (ws) => {
  console.log('🔌 WebSocket client connected');
  
  // Send initial status
  ws.send(JSON.stringify({
    type: 'status',
    data: {
      isListening: wakeWordDetector.isCurrentlyListening(),
      activeStreams: wakeWordDetector.getActiveStreams().length
    }
  }));
  
  // Handle wake word detection events
  const handleWakeWordDetection = (event: any) => {
    ws.send(JSON.stringify({
      type: 'wake_word_detected',
      data: event
    }));
  };
  
  const handleListeningStarted = (data: any) => {
    ws.send(JSON.stringify({
      type: 'listening_started',
      data
    }));
  };
  
  const handleListeningStopped = (data: any) => {
    ws.send(JSON.stringify({
      type: 'listening_stopped',
      data
    }));
  };
  
  // Register event listeners
  wakeWordDetector.on('wake_word_detected', handleWakeWordDetection);
  wakeWordDetector.on('listening_started', handleListeningStarted);
  wakeWordDetector.on('listening_stopped', handleListeningStopped);
  
  // Handle WebSocket messages
  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message.toString());
      
      switch (data.type) {
        case 'start_listening':
          const streamId = await wakeWordDetector.startListening(data.config);
          ws.send(JSON.stringify({
            type: 'listening_started',
            data: { streamId, config: data.config }
          }));
          break;
          
        case 'stop_listening':
          const success = await wakeWordDetector.stopListening(data.streamId);
          ws.send(JSON.stringify({
            type: 'listening_stopped',
            data: { streamId: data.streamId, success }
          }));
          break;
          
        case 'get_stats':
          const stats = await wakeWordDetector.getStats();
          ws.send(JSON.stringify({
            type: 'stats',
            data: stats
          }));
          break;
      }
    } catch (error) {
      console.error('❌ WebSocket message error:', error);
      ws.send(JSON.stringify({
        type: 'error',
        data: { message: error.message }
      }));
    }
  });
  
  // Handle WebSocket close
  ws.on('close', () => {
    console.log('🔌 WebSocket client disconnected');
    
    // Remove event listeners
    wakeWordDetector.off('wake_word_detected', handleWakeWordDetection);
    wakeWordDetector.off('listening_started', handleListeningStarted);
    wakeWordDetector.off('listening_stopped', handleListeningStopped);
  });
});

// Start server
const startServer = async () => {
  try {
    // Initialize wake word detector
    await wakeWordDetector.initialize();
    
    // Start server
    server.listen(PORT, () => {
      console.log(`🚀 Wake word service running on port ${PORT}`);
      console.log(`📊 Health check: http://localhost:${PORT}/health`);
      console.log(`📈 Stats: http://localhost:${PORT}/stats`);
      console.log(`🔌 WebSocket: ws://localhost:${PORT}`);
    });
  } catch (error) {
    console.error('❌ Failed to start wake word service:', error);
    process.exit(1);
  }
};

startServer();

export default app;
