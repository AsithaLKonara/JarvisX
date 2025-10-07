/**
 * JarvisX Personality Engine
 * Creates a human-like AI personality with emotional intelligence
 */

import express from 'express';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import dotenv from 'dotenv';

// Import personality modules
import { PersonalityCore } from './core/PersonalityCore';
import { EmotionalEngine } from './engine/EmotionalEngine';
import { MemorySystem } from './memory/MemorySystem';
import { ConversationEngine } from './conversation/ConversationEngine';
import { VoicePersonality } from './voice/VoicePersonality';

dotenv.config();

class JarvisXPersonalityService {
  private app: express.Application;
  private server: any;
  private wss: WebSocketServer;
  private personalityCore: PersonalityCore;
  private emotionalEngine: EmotionalEngine;
  private memorySystem: MemorySystem;
  private conversationEngine: ConversationEngine;
  private voicePersonality: VoicePersonality;

  constructor() {
    this.app = express();
    this.server = createServer(this.app);
    this.wss = new WebSocketServer({ server: this.server });
    
    this.initializePersonality();
    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
  }

  private async initializePersonality(): Promise<void> {
    console.log('🧠 Initializing JarvisX Personality Engine...');

    try {
      // Initialize core personality components
      this.personalityCore = new PersonalityCore();
      this.emotionalEngine = new EmotionalEngine();
      this.memorySystem = new MemorySystem();
      this.conversationEngine = new ConversationEngine();
      this.voicePersonality = new VoicePersonality();

      // Initialize personality traits
      await this.personalityCore.initialize({
        name: 'JarvisX',
        personality: 'intelligent, helpful, witty, professional',
        speakingStyle: 'conversational, confident, occasionally humorous',
        emotionalRange: 'warm, empathetic, enthusiastic when appropriate',
        culturalContext: 'Sri Lankan, understands Sinhala culture and context',
        expertise: 'technology, productivity, automation, trading, development'
      });

      // Connect components
      this.emotionalEngine.setPersonalityCore(this.personalityCore);
      this.conversationEngine.setPersonalityCore(this.personalityCore);
      this.conversationEngine.setEmotionalEngine(this.emotionalEngine);
      this.conversationEngine.setMemorySystem(this.memorySystem);
      this.voicePersonality.setEmotionalEngine(this.emotionalEngine);

      console.log('✅ JarvisX Personality Engine initialized successfully');
      console.log('🤖 JarvisX is now alive and ready to assist!');

    } catch (error) {
      console.error('❌ Failed to initialize Personality Engine:', error);
      process.exit(1);
    }
  }

  private setupMiddleware(): void {
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));

    // CORS middleware
    this.app.use((req, res, next) => {
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
      if (req.method === 'OPTIONS') {
        res.sendStatus(200);
      } else {
        next();
      }
    });
  }

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        service: 'jarvisx-personality',
        timestamp: new Date().toISOString(),
        personality: {
          name: this.personalityCore.getName(),
          mood: this.emotionalEngine.getCurrentMood(),
          memoryItems: this.memorySystem.getMemoryCount(),
          conversationCount: this.conversationEngine.getConversationCount()
        }
      });
    });

    // Personality status
    this.app.get('/personality/status', (req, res) => {
      res.json({
        name: this.personalityCore.getName(),
        traits: this.personalityCore.getTraits(),
        currentMood: this.emotionalEngine.getCurrentMood(),
        emotionalState: this.emotionalEngine.getEmotionalState(),
        recentMemories: this.memorySystem.getRecentMemories(5),
        conversationStyle: this.conversationEngine.getConversationStyle()
      });
    });

    // Generate response
    this.app.post('/personality/respond', async (req, res) => {
      try {
        const { message, context, userEmotion, sessionId } = req.body;

        console.log(`🗣️ User: "${message}"`);

        // Process through conversation engine
        const response = await this.conversationEngine.generateResponse({
          message,
          context,
          userEmotion,
          sessionId
        });

        console.log(`🤖 JarvisX: "${response.text}"`);

        res.json({
          success: true,
          response: response.text,
          emotion: response.emotion,
          personality: response.personality,
          confidence: response.confidence,
          followUpSuggestions: response.followUpSuggestions,
          timestamp: new Date().toISOString()
        });

      } catch (error: any) {
        console.error('❌ Failed to generate response:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Update personality
    this.app.post('/personality/update', async (req, res) => {
      try {
        const { traits, mood, preferences } = req.body;
        
        await this.personalityCore.updateTraits(traits);
        if (mood) {
          this.emotionalEngine.setMood(mood);
        }
        if (preferences) {
          this.memorySystem.updatePreferences(preferences);
        }

        res.json({
          success: true,
          message: 'Personality updated successfully'
        });

      } catch (error: any) {
        console.error('❌ Failed to update personality:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Memory management
    this.app.get('/memory/recent', (req, res) => {
      const limit = parseInt(req.query.limit as string) || 10;
      const memories = this.memorySystem.getRecentMemories(limit);
      res.json({ memories });
    });

    this.app.post('/memory/add', async (req, res) => {
      try {
        const { content, type, importance, tags } = req.body;
        await this.memorySystem.addMemory(content, type, importance, tags);
        res.json({ success: true });
      } catch (error: any) {
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // Voice personality
    this.app.post('/voice/synthesize', async (req, res) => {
      try {
        const { text, emotion, speed, pitch } = req.body;
        
        const audioBuffer = await this.voicePersonality.synthesizeSpeech({
          text,
          emotion: emotion || this.emotionalEngine.getCurrentMood(),
          speed: speed || 1.0,
          pitch: pitch || 1.0
        });

        res.set({
          'Content-Type': 'audio/mpeg',
          'Content-Length': audioBuffer.length.toString()
        });
        res.send(audioBuffer);

      } catch (error: any) {
        console.error('❌ Voice synthesis failed:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Generate avatar animation cues
    this.app.post('/avatar/animation-cues', async (req, res) => {
      try {
        const { text, emotion, duration } = req.body;
        
        const currentMood = emotion || this.emotionalEngine.getCurrentMood();
        const moodIntensity = this.emotionalEngine.getCurrentMoodIntensity();
        
        // Generate animation cues based on text content and emotion
        const animationCues = this.generateAvatarAnimationCues(
          text,
          currentMood,
          moodIntensity,
          duration
        );

        res.json({
          success: true,
          animationCues,
          emotion: currentMood,
          intensity: moodIntensity
        });

      } catch (error: any) {
        console.error('❌ Failed to generate avatar animation cues:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });
  }

  /**
   * Generate avatar animation cues from text and emotion
   */
  private generateAvatarAnimationCues(
    text: string,
    emotion: string,
    intensity: number,
    duration?: number
  ): any {
    const words = text.split(/\s+/);
    const estimatedDuration = duration || (words.length / 150) * 60; // 150 words per minute
    
    // Detect emphasis points (punctuation, capitalization)
    const emphasisPoints: number[] = [];
    let currentPos = 0;
    
    words.forEach((word, index) => {
      if (word.endsWith('!') || word.endsWith('?') || word.toUpperCase() === word) {
        emphasisPoints.push(index / words.length);
      }
    });

    // Generate gesture cues
    const gestures = [];
    
    // Add gestures at emphasis points
    emphasisPoints.forEach(position => {
      const timestamp = position * estimatedDuration;
      gestures.push({
        timestamp,
        type: emotion === 'excited' ? 'wide_gesture' : 'subtle_nod',
        intensity: intensity * 0.8
      });
    });

    // Generate micro-expressions based on emotion
    const microExpressions = this.generateMicroExpressions(emotion, estimatedDuration);

    return {
      emotion,
      intensity,
      duration: estimatedDuration,
      gestures,
      microExpressions,
      emphasisPoints,
      headMovementPattern: this.getHeadMovementPattern(emotion),
      eyeContactPattern: this.getEyeContactPattern(emotion),
      bodyLanguage: this.getBodyLanguage(emotion)
    };
  }

  /**
   * Generate micro-expressions for the duration
   */
  private generateMicroExpressions(emotion: string, duration: number): any[] {
    const expressions = [];
    const expressionInterval = 2.5; // Every 2.5 seconds
    const numExpressions = Math.floor(duration / expressionInterval);

    const emotionExpressions: { [key: string]: string[] } = {
      happy: ['smile', 'bright_eyes', 'raised_cheeks'],
      excited: ['wide_eyes', 'open_mouth', 'animated'],
      concerned: ['furrowed_brow', 'slight_frown', 'focused'],
      confident: ['slight_smirk', 'steady_gaze', 'relaxed'],
      curious: ['raised_eyebrow', 'tilted_head', 'attentive'],
      proud: ['satisfied_smile', 'chin_up', 'chest_out'],
      grateful: ['soft_smile', 'warm_eyes', 'gentle_nod'],
      optimistic: ['hopeful_look', 'forward_lean', 'bright']
    };

    const availableExpressions = emotionExpressions[emotion] || ['neutral', 'attentive'];

    for (let i = 0; i < numExpressions; i++) {
      const timestamp = i * expressionInterval;
      const expression = availableExpressions[Math.floor(Math.random() * availableExpressions.length)];
      
      expressions.push({
        timestamp,
        expression,
        duration: 0.5 + Math.random() * 0.5
      });
    }

    return expressions;
  }

  /**
   * Get head movement pattern for emotion
   */
  private getHeadMovementPattern(emotion: string): string {
    const patterns: { [key: string]: string } = {
      happy: 'slight_bob',
      excited: 'energetic_movement',
      concerned: 'subtle_tilt',
      confident: 'steady',
      curious: 'inquisitive_tilt',
      proud: 'upright',
      grateful: 'gentle_nod',
      optimistic: 'forward_lean'
    };

    return patterns[emotion] || 'neutral';
  }

  /**
   * Get eye contact pattern for emotion
   */
  private getEyeContactPattern(emotion: string): string {
    const patterns: { [key: string]: string } = {
      happy: 'warm_direct',
      excited: 'bright_engaged',
      concerned: 'focused_attentive',
      confident: 'steady_direct',
      curious: 'searching_interested',
      proud: 'assured_direct',
      grateful: 'soft_appreciative',
      optimistic: 'hopeful_forward'
    };

    return patterns[emotion] || 'neutral';
  }

  /**
   * Get body language for emotion
   */
  private getBodyLanguage(emotion: string): string {
    const bodyLanguage: { [key: string]: string } = {
      happy: 'open_relaxed',
      excited: 'energetic_animated',
      concerned: 'attentive_focused',
      confident: 'upright_strong',
      curious: 'leaning_interested',
      proud: 'chest_out_tall',
      grateful: 'warm_open',
      optimistic: 'forward_positive'
    };

    return bodyLanguage[emotion] || 'neutral';
  }

  private setupWebSocket(): void {
    this.wss.on('connection', (ws, req) => {
      console.log('🔌 New WebSocket connection to personality service');

      ws.on('message', async (data) => {
        try {
          const message = JSON.parse(data.toString());
          await this.handleWebSocketMessage(ws, message);
        } catch (error) {
          console.error('❌ Failed to handle WebSocket message:', error);
          ws.send(JSON.stringify({
            type: 'error',
            error: 'Invalid message format'
          }));
        }
      });

      ws.on('close', () => {
        console.log('🔌 WebSocket connection closed');
      });

      ws.on('error', (error) => {
        console.error('❌ WebSocket error:', error);
      });

      // Send welcome message with personality
      ws.send(JSON.stringify({
        type: 'personality_ready',
        data: {
          name: this.personalityCore.getName(),
          greeting: await this.conversationEngine.generateGreeting(),
          currentMood: this.emotionalEngine.getCurrentMood(),
          timestamp: new Date().toISOString()
        }
      }));
    });
  }

  private async handleWebSocketMessage(ws: any, message: any): Promise<void> {
    switch (message.type) {
      case 'chat_message':
        try {
          const { text, context, sessionId } = message.data;
          
          const response = await this.conversationEngine.generateResponse({
            message: text,
            context,
            sessionId
          });

          ws.send(JSON.stringify({
            type: 'chat_response',
            data: {
              response: response.text,
              emotion: response.emotion,
              personality: response.personality,
              confidence: response.confidence,
              timestamp: new Date().toISOString()
            }
          }));

        } catch (error: any) {
          ws.send(JSON.stringify({
            type: 'error',
            error: error.message
          }));
        }
        break;

      case 'mood_update':
        try {
          const { mood, reason } = message.data;
          this.emotionalEngine.setMood(mood, reason);
          
          ws.send(JSON.stringify({
            type: 'mood_updated',
            data: {
              mood: this.emotionalEngine.getCurrentMood(),
              reason,
              timestamp: new Date().toISOString()
            }
          }));

        } catch (error: any) {
          ws.send(JSON.stringify({
            type: 'error',
            error: error.message
          }));
        }
        break;

      case 'memory_query':
        try {
          const { query, limit = 5 } = message.data;
          const memories = this.memorySystem.searchMemories(query, limit);
          
          ws.send(JSON.stringify({
            type: 'memory_results',
            data: { memories }
          }));

        } catch (error: any) {
          ws.send(JSON.stringify({
            type: 'error',
            error: error.message
          }));
        }
        break;

      default:
        console.log('📨 Unknown WebSocket message type:', message.type);
    }
  }

  public async start(): Promise<void> {
    const PORT = process.env.PERSONALITY_SERVICE_PORT || 8007;
    
    try {
      this.server.listen(PORT, '0.0.0.0', () => {
        console.log(`🧠 JarvisX Personality Engine running on port ${PORT}`);
        console.log(`🤖 JarvisX is alive and ready to assist!`);
        console.log(`💭 Current mood: ${this.emotionalEngine.getCurrentMood()}`);
        console.log(`🧠 Memory items: ${this.memorySystem.getMemoryCount()}`);
      });
    } catch (error) {
      console.error('Failed to start Personality Engine:', error);
      process.exit(1);
    }
  }
}

// Start the Personality Engine
const personalityService = new JarvisXPersonalityService();
personalityService.start().catch((error) => {
  console.error('Failed to start Personality Engine:', error);
  process.exit(1);
});

export default personalityService;
