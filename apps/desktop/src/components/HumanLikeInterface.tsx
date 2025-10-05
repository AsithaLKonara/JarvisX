/**
 * Human-like Interface - Makes JarvisX feel truly alive and human
 */

import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface HumanLikeInterfaceProps {
  wsUrl: string;
  onInteraction?: (type: string, data: any) => void;
}

interface EmotionalState {
  mood: string;
  intensity: number;
  color: string;
  animation: string;
}

interface ConversationContext {
  isListening: boolean;
  isThinking: boolean;
  isSpeaking: boolean;
  currentTopic: string;
  userMood: string;
  conversationHistory: any[];
}

export function HumanLikeInterface({ wsUrl, onInteraction }: HumanLikeInterfaceProps) {
  const [emotionalState, setEmotionalState] = useState<EmotionalState>({
    mood: 'optimistic',
    intensity: 70,
    color: '#3B82F6',
    animation: 'pulse'
  });
  
  const [conversationContext, setConversationContext] = useState<ConversationContext>({
    isListening: false,
    isThinking: false,
    isSpeaking: false,
    currentTopic: '',
    userMood: 'neutral',
    conversationHistory: []
  });

  const [personalityTraits, setPersonalityTraits] = useState({
    intelligence: 95,
    humor: 70,
    empathy: 85,
    confidence: 90,
    enthusiasm: 80,
    creativity: 75,
    culturalAwareness: 90
  });

  const [voiceWaveform, setVoiceWaveform] = useState<number[]>([]);
  const [eyeTracking, setEyeTracking] = useState({ x: 0, y: 0, blink: false });
  const [breathingPattern, setBreathingPattern] = useState(0);
  const [microExpressions, setMicroExpressions] = useState<string[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const animationRef = useRef<number>();
  const eyeTrackingRef = useRef<number>();

  useEffect(() => {
    // Connect to personality service
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      console.log('🧠 Connected to Personality Engine');
    };

    wsRef.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handlePersonalityMessage(message);
    };

    // Start human-like animations
    startBreathingAnimation();
    startEyeTracking();
    startMicroExpressions();

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      if (eyeTrackingRef.current) cancelAnimationFrame(eyeTrackingRef.current);
    };
  }, [wsUrl]);

  const handlePersonalityMessage = (message: any) => {
    switch (message.type) {
      case 'emotion_update':
        updateEmotionalState(message.data);
        break;
      case 'conversation_update':
        updateConversationContext(message.data);
        break;
      case 'personality_update':
        setPersonalityTraits(message.data.traits);
        break;
      case 'voice_analysis':
        updateVoiceWaveform(message.data.waveform);
        break;
      case 'micro_expression':
        addMicroExpression(message.data.expression);
        break;
    }
  };

  const updateEmotionalState = (data: any) => {
    const moodColors: { [key: string]: string } = {
      'happy': '#10B981',
      'excited': '#F59E0B',
      'concerned': '#EF4444',
      'confident': '#3B82F6',
      'curious': '#8B5CF6',
      'proud': '#EC4899',
      'grateful': '#06B6D4',
      'optimistic': '#84CC16'
    };

    setEmotionalState({
      mood: data.mood,
      intensity: data.intensity,
      color: moodColors[data.mood] || '#3B82F6',
      animation: data.animation || 'pulse'
    });
  };

  const updateConversationContext = (data: any) => {
    setConversationContext(prev => ({
      ...prev,
      ...data
    }));
  };

  const updateVoiceWaveform = (waveform: number[]) => {
    setVoiceWaveform(waveform);
  };

  const addMicroExpression = (expression: string) => {
    setMicroExpressions(prev => [...prev.slice(-2), expression]);
    setTimeout(() => {
      setMicroExpressions(prev => prev.slice(1));
    }, 1000);
  };

  const startBreathingAnimation = () => {
    const animate = () => {
      setBreathingPattern(prev => (prev + 0.02) % (Math.PI * 2));
      animationRef.current = requestAnimationFrame(animate);
    };
    animate();
  };

  const startEyeTracking = () => {
    const track = () => {
      // Simulate eye movement following cursor or conversation focus
      setEyeTracking(prev => ({
        x: Math.sin(Date.now() * 0.001) * 10,
        y: Math.cos(Date.now() * 0.0008) * 5,
        blink: Math.random() < 0.02 // Random blinks
      }));
      eyeTrackingRef.current = requestAnimationFrame(track);
    };
    track();
  };

  const startMicroExpressions = () => {
    const expressions = ['curious', 'understanding', 'thoughtful', 'amused', 'concerned'];
    
    setInterval(() => {
      if (Math.random() < 0.3) { // 30% chance every interval
        addMicroExpression(expressions[Math.floor(Math.random() * expressions.length)]);
      }
    }, 3000);
  };

  const getEmotionalAnimation = () => {
    switch (emotionalState.animation) {
      case 'pulse':
        return {
          scale: [1, 1.05, 1],
          transition: { duration: 2, repeat: Infinity }
        };
      case 'bounce':
        return {
          y: [0, -10, 0],
          transition: { duration: 0.6, repeat: Infinity }
        };
      case 'glow':
        return {
          boxShadow: [
            `0 0 20px ${emotionalState.color}40`,
            `0 0 40px ${emotionalState.color}60`,
            `0 0 20px ${emotionalState.color}40`
          ],
          transition: { duration: 1.5, repeat: Infinity }
        };
      default:
        return {};
    }
  };

  const getMoodDescription = () => {
    const descriptions: { [key: string]: string } = {
      'happy': 'Feeling cheerful and ready to help!',
      'excited': 'Energized and enthusiastic about our work!',
      'concerned': 'Focused on ensuring everything goes smoothly.',
      'confident': 'Ready to tackle any challenge with confidence.',
      'curious': 'Intrigued and eager to learn more.',
      'proud': 'Pleased with what we\'ve accomplished together.',
      'grateful': 'Thankful for the opportunity to assist.',
      'optimistic': 'Looking forward to what we can achieve.'
    };
    return descriptions[emotionalState.mood] || 'Ready to help you succeed.';
  };

  const getPersonalityInsight = () => {
    const insights = [
      `Intelligence: ${personalityTraits.intelligence}/100 - Highly analytical and knowledgeable`,
      `Empathy: ${personalityTraits.empathy}/100 - Understanding and caring`,
      `Creativity: ${personalityTraits.creativity}/100 - Innovative and imaginative`,
      `Cultural Awareness: ${personalityTraits.culturalAwareness}/100 - Culturally sensitive`
    ];
    return insights[Math.floor(Math.random() * insights.length)];
  };

  return (
    <div className="human-like-interface fixed inset-0 pointer-events-none z-50">
      {/* Main Personality Avatar */}
      <motion.div
        className="fixed top-4 right-4 w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg"
        style={{ backgroundColor: emotionalState.color }}
        animate={getEmotionalAnimation()}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        {/* Animated Eyes */}
        <div className="relative w-8 h-8">
          <motion.div
            className="absolute w-2 h-2 bg-white rounded-full top-2"
            style={{
              left: 6 + eyeTracking.x,
              top: 6 + eyeTracking.y,
              opacity: eyeTracking.blink ? 0 : 1
            }}
          />
          <motion.div
            className="absolute w-2 h-2 bg-white rounded-full top-2"
            style={{
              left: 18 + eyeTracking.x,
              top: 6 + eyeTracking.y,
              opacity: eyeTracking.blink ? 0 : 1
            }}
          />
        </div>

        {/* Breathing Animation */}
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-white/30"
          style={{
            scale: 1 + Math.sin(breathingPattern) * 0.1
          }}
        />
      </motion.div>

      {/* Voice Waveform Visualizer */}
      <AnimatePresence>
        {conversationContext.isListening && (
          <motion.div
            className="fixed bottom-20 left-1/2 transform -translate-x-1/2 flex items-center space-x-1"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
          >
            {voiceWaveform.map((amplitude, index) => (
              <motion.div
                key={index}
                className="w-1 bg-blue-500 rounded-full"
                style={{
                  height: Math.max(4, amplitude * 40),
                  backgroundColor: emotionalState.color
                }}
                animate={{
                  height: [Math.max(4, amplitude * 40), Math.max(8, amplitude * 60), Math.max(4, amplitude * 40)]
                }}
                transition={{
                  duration: 0.6,
                  repeat: Infinity,
                  delay: index * 0.1
                }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Thinking Indicator */}
      <AnimatePresence>
        {conversationContext.isThinking && (
          <motion.div
            className="fixed top-20 right-20 flex items-center space-x-2 bg-black/20 backdrop-blur-sm rounded-lg px-3 py-2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <div className="flex space-x-1">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-2 h-2 bg-blue-400 rounded-full"
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [0.5, 1, 0.5]
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    delay: i * 0.2
                  }}
                />
              ))}
            </div>
            <span className="text-white text-sm">Thinking...</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Micro Expressions */}
      <AnimatePresence>
        {microExpressions.map((expression, index) => (
          <motion.div
            key={`${expression}-${index}`}
            className="fixed top-32 right-20 bg-black/20 backdrop-blur-sm rounded-lg px-2 py-1"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.3 }}
          >
            <span className="text-white text-xs capitalize">{expression}</span>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Personality Status Panel */}
      <motion.div
        className="fixed bottom-4 right-4 bg-black/20 backdrop-blur-sm rounded-lg p-4 max-w-xs"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ scale: 1.02 }}
      >
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: emotionalState.color }}
            />
            <span className="text-white font-medium capitalize">{emotionalState.mood}</span>
          </div>
          
          <p className="text-white/80 text-sm">{getMoodDescription()}</p>
          
          <div className="text-white/60 text-xs">
            {getPersonalityInsight()}
          </div>
          
          <div className="flex items-center justify-between text-white/60 text-xs">
            <span>Intensity: {emotionalState.intensity}%</span>
            <span>Conversations: {conversationContext.conversationHistory.length}</span>
          </div>
        </div>
      </motion.div>

      {/* Cultural Context Indicator */}
      <motion.div
        className="fixed bottom-4 left-4 bg-black/20 backdrop-blur-sm rounded-lg px-3 py-2"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <div className="flex items-center space-x-2">
          <span className="text-white/80 text-sm">🇱🇰</span>
          <span className="text-white text-sm">Sinhala & English</span>
        </div>
      </motion.div>

      {/* Conversation Topic */}
      <AnimatePresence>
        {conversationContext.currentTopic && (
          <motion.div
            className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-black/20 backdrop-blur-sm rounded-lg px-4 py-2"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <span className="text-white text-sm">
              Topic: <span className="font-medium">{conversationContext.currentTopic}</span>
            </span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Emotional State Visualization */}
      <div className="fixed top-20 right-4 space-y-2">
        {Object.entries(personalityTraits).map(([trait, value]) => (
          <div key={trait} className="flex items-center space-x-2">
            <span className="text-white/60 text-xs w-20 capitalize">{trait}:</span>
            <div className="w-16 h-1 bg-white/20 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-blue-400 to-purple-500 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                transition={{ duration: 1, delay: 0.2 }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HumanLikeInterface;
