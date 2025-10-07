/**
 * JarvisX Avatar Service
 * Handles 3D avatar animation generation, lip-sync processing, and emotion mapping
 */

import express from 'express';
import cors from 'cors';
import { WebSocketServer, WebSocket } from 'ws';
import http from 'http';
import { EmotionAnimationMapper } from './engine/EmotionAnimationMapper';
import { LipSyncProcessor } from './processors/LipSyncProcessor';
import { AvatarStateManager } from './state/AvatarStateManager';

const PORT = process.env.AVATAR_PORT || 8008;

class JarvisXAvatarService {
  private app: express.Application;
  private server: http.Server;
  private wss: WebSocketServer;
  private emotionMapper: EmotionAnimationMapper;
  private lipSyncProcessor: LipSyncProcessor;
  private stateManager: AvatarStateManager;
  private clients: Set<WebSocket> = new Set();

  constructor() {
    this.app = express();
    this.server = http.createServer(this.app);
    this.wss = new WebSocketServer({ server: this.server, path: '/avatar-ws' });
    
    this.emotionMapper = new EmotionAnimationMapper();
    this.lipSyncProcessor = new LipSyncProcessor();
    this.stateManager = new AvatarStateManager();

    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
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
        service: 'avatar',
        status: 'healthy',
        timestamp: new Date().toISOString(),
        clients: this.clients.size
      });
    });

    // Generate animation from emotion
    this.app.post('/animation/emotion', async (req, res) => {
      try {
        const { emotion, intensity, duration } = req.body;
        
        const animation = await this.emotionMapper.generateAnimation({
          emotion: emotion || 'neutral',
          intensity: intensity || 0.5,
          duration: duration || 1.0
        });

        res.json({
          success: true,
          animation,
          timestamp: new Date().toISOString()
        });
      } catch (error: any) {
        console.error('❌ Failed to generate emotion animation:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Process audio for lip-sync
    this.app.post('/lipsync/process', async (req, res) => {
      try {
        const { audioData, audioUrl, text, duration } = req.body;
        
        let lipSyncData;
        
        if (audioData) {
          // Process from base64 audio data
          lipSyncData = await this.lipSyncProcessor.processAudioData(audioData);
        } else if (audioUrl) {
          // Process from audio URL
          lipSyncData = await this.lipSyncProcessor.processAudioUrl(audioUrl);
        } else if (text && duration) {
          // Estimate from text (fallback)
          lipSyncData = this.lipSyncProcessor.estimateFromText(text, duration);
        } else {
          throw new Error('Either audioData, audioUrl, or text+duration is required');
        }

        res.json({
          success: true,
          lipSyncData,
          frameCount: lipSyncData.length,
          duration: lipSyncData.length / 30 // Assuming 30 FPS
        });
      } catch (error: any) {
        console.error('❌ Failed to process lip-sync:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Get avatar state
    this.app.get('/state', (req, res) => {
      const state = this.stateManager.getState();
      res.json({
        success: true,
        state
      });
    });

    // Update avatar state
    this.app.post('/state', (req, res) => {
      try {
        const updates = req.body;
        this.stateManager.updateState(updates);
        
        // Broadcast state update to all connected clients
        this.broadcastStateUpdate(this.stateManager.getState());
        
        res.json({
          success: true,
          state: this.stateManager.getState()
        });
      } catch (error: any) {
        console.error('❌ Failed to update avatar state:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Generate full avatar animation sequence
    this.app.post('/animation/sequence', async (req, res) => {
      try {
        const { text, emotion, audioUrl, duration } = req.body;
        
        // Generate lip-sync
        let lipSyncData;
        if (audioUrl) {
          lipSyncData = await this.lipSyncProcessor.processAudioUrl(audioUrl);
        } else {
          lipSyncData = this.lipSyncProcessor.estimateFromText(text, duration || 3);
        }

        // Generate emotion animation
        const emotionAnimation = await this.emotionMapper.generateAnimation({
          emotion: emotion || 'neutral',
          intensity: 0.7,
          duration: duration || 3
        });

        res.json({
          success: true,
          sequence: {
            lipSync: lipSyncData,
            emotionAnimation,
            duration: lipSyncData.length / 30
          }
        });
      } catch (error: any) {
        console.error('❌ Failed to generate animation sequence:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });
  }

  private setupWebSocket(): void {
    this.wss.on('connection', (ws: WebSocket) => {
      console.log('👤 Avatar client connected');
      this.clients.add(ws);

      // Send current state to new client
      ws.send(JSON.stringify({
        type: 'state_update',
        data: this.stateManager.getState()
      }));

      ws.on('message', async (message: string) => {
        try {
          const data = JSON.parse(message.toString());
          await this.handleWebSocketMessage(ws, data);
        } catch (error) {
          console.error('❌ WebSocket message error:', error);
        }
      });

      ws.on('close', () => {
        console.log('👤 Avatar client disconnected');
        this.clients.delete(ws);
      });

      ws.on('error', (error) => {
        console.error('❌ WebSocket error:', error);
        this.clients.delete(ws);
      });
    });
  }

  private async handleWebSocketMessage(ws: WebSocket, message: any): Promise<void> {
    switch (message.type) {
      case 'emotion_update':
        const animation = await this.emotionMapper.generateAnimation(message.data);
        this.stateManager.updateState({
          currentEmotion: message.data.emotion,
          emotionIntensity: message.data.intensity,
          animation
        });
        this.broadcastStateUpdate(this.stateManager.getState());
        break;

      case 'speech_start':
        if (message.data.audioUrl) {
          const lipSyncData = await this.lipSyncProcessor.processAudioUrl(message.data.audioUrl);
          ws.send(JSON.stringify({
            type: 'lipsync_data',
            data: lipSyncData
          }));
        }
        break;

      case 'state_query':
        ws.send(JSON.stringify({
          type: 'state_update',
          data: this.stateManager.getState()
        }));
        break;

      default:
        console.warn('Unknown message type:', message.type);
    }
  }

  private broadcastStateUpdate(state: any): void {
    const message = JSON.stringify({
      type: 'state_update',
      data: state,
      timestamp: new Date().toISOString()
    });

    this.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }

  public start(): void {
    this.server.listen(PORT, () => {
      console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🎭 JarvisX Avatar Service                              ║
║                                                           ║
║   Status: ACTIVE                                         ║
║   Port: ${PORT}                                           ║
║   WebSocket: ws://localhost:${PORT}/avatar-ws            ║
║                                                           ║
║   Capabilities:                                          ║
║   • Real-time emotion-driven animations                  ║
║   • Audio-to-lip-sync processing                         ║
║   • Avatar state management                              ║
║   • WebSocket streaming                                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
      `);
    });
  }
}

// Start the service
const avatarService = new JarvisXAvatarService();
avatarService.start();

export default JarvisXAvatarService;

