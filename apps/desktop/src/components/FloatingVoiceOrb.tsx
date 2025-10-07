/**
 * Floating Voice Orb - Main interface for JarvisX
 * Always-on-top floating orb with voice interaction
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Settings, X, Minimize2, Maximize2, Volume2, VolumeX } from 'lucide-react';

interface FloatingVoiceOrbProps {
  onOpenMainPanel: () => void;
  onClose: () => void;
  isListening: boolean;
  isProcessing: boolean;
  isSpeaking: boolean;
  onStartListening: () => void;
  onStopListening: () => void;
  onToggleMute: () => void;
  isMuted: boolean;
  currentEmotion: string;
  confidence: number;
  lastCommand: string;
  status: 'idle' | 'listening' | 'processing' | 'speaking' | 'error';
}

const FloatingVoiceOrb: React.FC<FloatingVoiceOrbProps> = ({
  onOpenMainPanel,
  onClose,
  isListening,
  isProcessing,
  isSpeaking,
  onStartListening,
  onStopListening,
  onToggleMute,
  isMuted,
  currentEmotion,
  confidence,
  lastCommand,
  status
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [position, setPosition] = useState({ x: 50, y: 50 });
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const orbRef = useRef<HTMLDivElement>(null);

  // Emotion-based colors
  const getEmotionColor = (emotion: string) => {
    switch (emotion.toLowerCase()) {
      case 'happy': return '#10B981';
      case 'excited': return '#F59E0B';
      case 'focused': return '#3B82F6';
      case 'thinking': return '#8B5CF6';
      case 'listening': return '#EF4444';
      case 'speaking': return '#06B6D4';
      case 'error': return '#DC2626';
      default: return '#6B7280';
    }
  };

  // Status-based animations
  const getStatusAnimation = () => {
    switch (status) {
      case 'listening':
        return {
          scale: [1, 1.1, 1],
          transition: { duration: 0.5, repeat: Infinity }
        };
      case 'processing':
        return {
          rotate: [0, 360],
          transition: { duration: 1, repeat: Infinity, ease: "linear" }
        };
      case 'speaking':
        return {
          scale: [1, 1.05, 1],
          transition: { duration: 0.3, repeat: Infinity }
        };
      default:
        return {};
    }
  };

  // Handle drag functionality
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget || (e.target as HTMLElement).closest('.orb-content')) {
      setIsDragging(true);
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
    }
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging) {
      const newX = e.clientX - dragStart.x;
      const newY = e.clientY - dragStart.y;
      
      // Keep orb within screen bounds
      const maxX = window.innerWidth - 80;
      const maxY = window.innerHeight - 80;
      
      setPosition({
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY))
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, dragStart]);

  // Auto-expand on status change
  useEffect(() => {
    if (status === 'listening' || status === 'processing' || status === 'speaking') {
      setIsExpanded(true);
    }
  }, [status]);

  // Auto-collapse after speaking
  useEffect(() => {
    if (status === 'speaking') {
      const timer = setTimeout(() => {
        setIsExpanded(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [status]);

  return (
    <motion.div
      ref={orbRef}
      className="fixed z-50 cursor-move select-none"
      style={{
        left: position.x,
        top: position.y,
      }}
      onMouseDown={handleMouseDown}
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Main Orb */}
      <motion.div
        className="relative w-16 h-16 rounded-full shadow-2xl overflow-hidden"
        style={{
          background: `linear-gradient(135deg, ${getEmotionColor(currentEmotion)}80, ${getEmotionColor(currentEmotion)}40)`,
          backdropFilter: 'blur(20px)',
          border: `2px solid ${getEmotionColor(currentEmotion)}60`,
        }}
        animate={getStatusAnimation()}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {/* Orb Content */}
        <div className="orb-content absolute inset-0 flex items-center justify-center">
          {status === 'listening' ? (
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.5, repeat: Infinity }}
            >
              <Mic size={24} className="text-white" />
            </motion.div>
          ) : status === 'processing' ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            >
              <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full" />
            </motion.div>
          ) : status === 'speaking' ? (
            <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 0.3, repeat: Infinity }}
            >
              <Volume2 size={24} className="text-white" />
            </motion.div>
          ) : (
            <Mic size={24} className="text-white" />
          )}
        </div>

        {/* Pulse Ring */}
        {status === 'listening' && (
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-white/30"
            animate={{ scale: [1, 1.5, 1], opacity: [0.7, 0, 0.7] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        )}

        {/* Confidence Indicator */}
        {confidence > 0 && (
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full flex items-center justify-center">
            <span className="text-xs text-white font-bold">{Math.round(confidence)}</span>
          </div>
        )}
      </motion.div>

      {/* Expanded Panel */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            className="absolute top-20 left-1/2 transform -translate-x-1/2 w-80 bg-black/90 backdrop-blur-xl rounded-2xl border border-white/20 shadow-2xl overflow-hidden"
            initial={{ opacity: 0, y: -20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.9 }}
            transition={{ duration: 0.2 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/10">
              <div className="flex items-center gap-3">
                <div 
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: getEmotionColor(currentEmotion) }}
                />
                <span className="text-white font-medium">JarvisX</span>
                <span className="text-xs text-gray-400 capitalize">{currentEmotion}</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={onToggleMute}
                  className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                >
                  {isMuted ? <VolumeX size={16} className="text-gray-400" /> : <Volume2 size={16} className="text-white" />}
                </button>
                <button
                  onClick={onOpenMainPanel}
                  className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <Maximize2 size={16} className="text-white" />
                </button>
                <button
                  onClick={onClose}
                  className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <X size={16} className="text-white" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-4">
              {/* Status */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Status</span>
                  <span className="text-sm text-white capitalize">{status}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <motion.div
                    className="h-2 rounded-full"
                    style={{ backgroundColor: getEmotionColor(currentEmotion) }}
                    initial={{ width: 0 }}
                    animate={{ width: `${confidence}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>

              {/* Last Command */}
              {lastCommand && (
                <div className="mb-4">
                  <span className="text-sm text-gray-400">Last Command</span>
                  <div className="mt-1 p-2 bg-white/5 rounded-lg">
                    <span className="text-white text-sm">{lastCommand}</span>
                  </div>
                </div>
              )}

              {/* Controls */}
              <div className="flex items-center justify-center gap-4">
                <button
                  onClick={isListening ? onStopListening : onStartListening}
                  className={`px-6 py-2 rounded-full font-medium transition-all ${
                    isListening
                      ? 'bg-red-500 hover:bg-red-600 text-white'
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                  }`}
                >
                  {isListening ? 'Stop Listening' : 'Start Listening'}
                </button>
              </div>

              {/* Quick Actions */}
              <div className="mt-4 grid grid-cols-2 gap-2">
                <button className="p-2 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                  <Settings size={16} className="text-white mx-auto" />
                  <span className="text-xs text-white mt-1 block">Settings</span>
                </button>
                <button className="p-2 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                  <Minimize2 size={16} className="text-white mx-auto" />
                  <span className="text-xs text-white mt-1 block">Minimize</span>
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Click to expand hint */}
      {!isExpanded && (
        <motion.div
          className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs text-gray-400 whitespace-nowrap"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          Click to expand
        </motion.div>
      )}
    </motion.div>
  );
};

export default FloatingVoiceOrb;
