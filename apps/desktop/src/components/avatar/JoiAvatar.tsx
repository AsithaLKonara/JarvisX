/**
 * Joi Avatar - Main integration component
 * Connects the 3D avatar with personality engine, voice services, and lip-sync
 */

import React, { useEffect, useState, useRef, useCallback } from 'react';
import { AvatarRenderer } from './AvatarRenderer';
import LipSyncEngine, { estimateLipSyncFromText } from './LipSyncEngine';
import { motion, AnimatePresence } from 'framer-motion';

interface JoiAvatarProps {
  personalityWsUrl: string;
  avatarWsUrl: string;
  orchestratorWsUrl: string;
  className?: string;
  onAvatarInteraction?: (type: string, data: any) => void;
}

interface EmotionalState {
  mood: string;
  intensity: number;
  color: string;
}

interface VoiceState {
  isListening: boolean;
  isSpeaking: boolean;
  isThinking: boolean;
  currentText?: string;
  audioUrl?: string;
}

export function JoiAvatar({
  personalityWsUrl,
  avatarWsUrl,
  orchestratorWsUrl,
  className = '',
  onAvatarInteraction
}: JoiAvatarProps) {
  // State
  const [emotionalState, setEmotionalState] = useState<EmotionalState>({
    mood: 'optimistic',
    intensity: 70,
    color: '#3B82F6'
  });

  const [voiceState, setVoiceState] = useState<VoiceState>({
    isListening: false,
    isSpeaking: false,
    isThinking: false
  });

  const [lipSyncData, setLipSyncData] = useState<number[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  // Refs
  const personalityWs = useRef<WebSocket | null>(null);
  const avatarWs = useRef<WebSocket | null>(null);
  const orchestratorWs = useRef<WebSocket | null>(null);
  const lipSyncEngine = useRef<LipSyncEngine | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  /**
   * Initialize connections
   */
  useEffect(() => {
    initializeLipSyncEngine();
    connectToPersonality();
    connectToAvatar();
    connectToOrchestrator();

    return () => {
      cleanup();
    };
  }, [personalityWsUrl, avatarWsUrl, orchestratorWsUrl]);

  /**
   * Initialize lip-sync engine
   */
  const initializeLipSyncEngine = async () => {
    try {
      lipSyncEngine.current = new LipSyncEngine({
        smoothing: 0.3,
        sensitivity: 1.5,
        sampleRate: 30
      });
      await lipSyncEngine.current.initialize();
      console.log('✅ Lip sync engine initialized');
    } catch (error) {
      console.error('❌ Failed to initialize lip sync engine:', error);
    }
  };

  /**
   * Connect to personality service
   */
  const connectToPersonality = () => {
    try {
      personalityWs.current = new WebSocket(personalityWsUrl);

      personalityWs.current.onopen = () => {
        console.log('🧠 Connected to Personality Engine');
        setIsConnected(true);
      };

      personalityWs.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handlePersonalityMessage(message);
        } catch (error) {
          console.error('❌ Failed to parse personality message:', error);
        }
      };

      personalityWs.current.onclose = () => {
        console.log('🧠 Disconnected from Personality Engine');
        setIsConnected(false);
        // Attempt reconnection
        setTimeout(connectToPersonality, 3000);
      };

      personalityWs.current.onerror = (error) => {
        console.error('❌ Personality WebSocket error:', error);
      };
    } catch (error) {
      console.error('❌ Failed to connect to personality service:', error);
    }
  };

  /**
   * Connect to avatar service
   */
  const connectToAvatar = () => {
    try {
      avatarWs.current = new WebSocket(avatarWsUrl);

      avatarWs.current.onopen = () => {
        console.log('🎭 Connected to Avatar Service');
      };

      avatarWs.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleAvatarMessage(message);
        } catch (error) {
          console.error('❌ Failed to parse avatar message:', error);
        }
      };

      avatarWs.current.onclose = () => {
        console.log('🎭 Disconnected from Avatar Service');
        setTimeout(connectToAvatar, 3000);
      };
    } catch (error) {
      console.error('❌ Failed to connect to avatar service:', error);
    }
  };

  /**
   * Connect to orchestrator
   */
  const connectToOrchestrator = () => {
    try {
      orchestratorWs.current = new WebSocket(orchestratorWsUrl);

      orchestratorWs.current.onopen = () => {
        console.log('🎯 Connected to Orchestrator');
      };

      orchestratorWs.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleOrchestratorMessage(message);
        } catch (error) {
          console.error('❌ Failed to parse orchestrator message:', error);
        }
      };

      orchestratorWs.current.onclose = () => {
        console.log('🎯 Disconnected from Orchestrator');
        setTimeout(connectToOrchestrator, 3000);
      };
    } catch (error) {
      console.error('❌ Failed to connect to orchestrator:', error);
    }
  };

  /**
   * Handle personality engine messages
   */
  const handlePersonalityMessage = useCallback((message: any) => {
    switch (message.type) {
      case 'emotion_update':
        updateEmotion(message.data);
        break;

      case 'voice_synthesis_start':
        setVoiceState(prev => ({ ...prev, isSpeaking: true, isThinking: false }));
        if (message.data.text) {
          // Generate estimated lip-sync from text
          const duration = estimateSpeechDuration(message.data.text);
          const lipSync = estimateLipSyncFromText(message.data.text, duration);
          setLipSyncData(lipSync);
        }
        break;

      case 'voice_synthesis_complete':
        if (message.data.audioUrl) {
          playAvatarSpeech(message.data.audioUrl, message.data.text);
        }
        break;

      case 'voice_synthesis_end':
        setVoiceState(prev => ({ ...prev, isSpeaking: false }));
        setLipSyncData([]);
        break;

      case 'listening_start':
        setVoiceState(prev => ({ ...prev, isListening: true }));
        break;

      case 'listening_end':
        setVoiceState(prev => ({ ...prev, isListening: false }));
        break;

      case 'thinking_start':
        setVoiceState(prev => ({ ...prev, isThinking: true }));
        break;

      case 'thinking_end':
        setVoiceState(prev => ({ ...prev, isThinking: false }));
        break;

      default:
        console.log('Unknown personality message type:', message.type);
    }
  }, []);

  /**
   * Handle avatar service messages
   */
  const handleAvatarMessage = useCallback((message: any) => {
    switch (message.type) {
      case 'lipsync_data':
        setLipSyncData(message.data);
        break;

      case 'state_update':
        // Sync with avatar service state
        if (message.data.currentEmotion) {
          updateEmotion({
            mood: message.data.currentEmotion,
            intensity: message.data.emotionIntensity * 100
          });
        }
        break;

      default:
        console.log('Unknown avatar message type:', message.type);
    }
  }, []);

  /**
   * Handle orchestrator messages
   */
  const handleOrchestratorMessage = useCallback((message: any) => {
    // Handle task-related events that might affect avatar state
    switch (message.type) {
      case 'task_started':
        setVoiceState(prev => ({ ...prev, isThinking: true }));
        break;

      case 'task_completed':
        setVoiceState(prev => ({ ...prev, isThinking: false }));
        updateEmotion({ mood: 'proud', intensity: 80 });
        break;

      case 'task_failed':
        setVoiceState(prev => ({ ...prev, isThinking: false }));
        updateEmotion({ mood: 'concerned', intensity: 70 });
        break;

      default:
        break;
    }
  }, []);

  /**
   * Update emotional state
   */
  const updateEmotion = (data: any) => {
    const moodColors: { [key: string]: string } = {
      'happy': '#10B981',
      'excited': '#F59E0B',
      'concerned': '#EF4444',
      'confident': '#3B82F6',
      'curious': '#8B5CF6',
      'proud': '#EC4899',
      'grateful': '#06B6D4',
      'optimistic': '#84CC16',
      'neutral': '#6B7280'
    };

    setEmotionalState({
      mood: data.mood || data.emotion,
      intensity: data.intensity || 70,
      color: moodColors[data.mood || data.emotion] || '#3B82F6'
    });

    // Send emotion to avatar service
    if (avatarWs.current?.readyState === WebSocket.OPEN) {
      avatarWs.current.send(JSON.stringify({
        type: 'emotion_update',
        data: {
          emotion: data.mood || data.emotion,
          intensity: (data.intensity || 70) / 100,
          duration: 2.0
        }
      }));
    }
  };

  /**
   * Play avatar speech with lip-sync
   */
  const playAvatarSpeech = async (audioUrl: string, text: string) => {
    try {
      // Generate accurate lip-sync from audio
      if (lipSyncEngine.current && avatarWs.current?.readyState === WebSocket.OPEN) {
        avatarWs.current.send(JSON.stringify({
          type: 'speech_start',
          data: { audioUrl, text }
        }));
      }

      // Play audio
      if (!audioRef.current) {
        audioRef.current = new Audio();
      }
      
      audioRef.current.src = audioUrl;
      audioRef.current.play();

      audioRef.current.onended = () => {
        setVoiceState(prev => ({ ...prev, isSpeaking: false }));
        setLipSyncData([]);
      };
    } catch (error) {
      console.error('❌ Failed to play avatar speech:', error);
    }
  };

  /**
   * Estimate speech duration from text
   */
  const estimateSpeechDuration = (text: string): number => {
    // Average speaking rate: ~150 words per minute
    const wordCount = text.split(/\s+/).length;
    return (wordCount / 150) * 60;
  };

  /**
   * Handle avatar click interaction
   */
  const handleAvatarClick = () => {
    console.log('🎭 Avatar clicked');
    
    if (onAvatarInteraction) {
      onAvatarInteraction('avatar_click', {
        emotion: emotionalState.mood,
        isListening: voiceState.isListening,
        isSpeaking: voiceState.isSpeaking
      });
    }

    // Toggle settings on double-click (implement if needed)
  };

  /**
   * Cleanup connections
   */
  const cleanup = () => {
    if (personalityWs.current) {
      personalityWs.current.close();
    }
    if (avatarWs.current) {
      avatarWs.current.close();
    }
    if (orchestratorWs.current) {
      orchestratorWs.current.close();
    }
    if (lipSyncEngine.current) {
      lipSyncEngine.current.dispose();
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
  };

  return (
    <div className={`joi-avatar-container relative ${className}`}>
      {/* Main 3D Avatar */}
      <div className="avatar-viewport absolute inset-0">
        <AvatarRenderer
          emotionalState={emotionalState}
          isListening={voiceState.isListening}
          isSpeaking={voiceState.isSpeaking}
          lipSyncData={lipSyncData}
          onAvatarClick={handleAvatarClick}
          joiMode={true}
        />
      </div>

      {/* Connection status indicator */}
      <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-2 rounded-full bg-black/20 backdrop-blur-md border border-white/10">
        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
        <span className="text-white text-xs">
          {isConnected ? 'Connected' : 'Reconnecting...'}
        </span>
      </div>

      {/* Avatar info overlay */}
      <AnimatePresence>
        {voiceState.isThinking && (
          <motion.div
            className="absolute bottom-24 left-1/2 transform -translate-x-1/2 px-4 py-2 rounded-full bg-purple-500/20 backdrop-blur-md border border-purple-500/40"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
          >
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-1.5 h-1.5 bg-purple-400 rounded-full"
                    animate={{
                      scale: [1, 1.5, 1],
                      opacity: [0.5, 1, 0.5]
                    }}
                    transition={{
                      duration: 0.8,
                      repeat: Infinity,
                      delay: i * 0.2
                    }}
                  />
                ))}
              </div>
              <span className="text-purple-100 text-sm">Processing...</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Settings button */}
      <button
        onClick={() => setShowSettings(!showSettings)}
        className="absolute top-4 left-4 p-2 rounded-full bg-black/20 backdrop-blur-md border border-white/10 hover:bg-black/30 transition-colors"
      >
        <svg
          className="w-5 h-5 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      </button>

      {/* Settings panel (can be expanded later) */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            className="absolute top-16 left-4 p-4 rounded-lg bg-black/40 backdrop-blur-md border border-white/10 min-w-[200px]"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
          >
            <h3 className="text-white font-medium mb-2">Avatar Settings</h3>
            <div className="space-y-2 text-white/60 text-sm">
              <div>Emotion: {emotionalState.mood}</div>
              <div>Intensity: {emotionalState.intensity}%</div>
              <div>Mode: Joi Holographic</div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default JoiAvatar;

