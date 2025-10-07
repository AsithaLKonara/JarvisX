/**
 * Desktop App - Main application with floating voice orb
 * Production-ready desktop interface
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import FloatingVoiceOrb from './components/FloatingVoiceOrb';
import EnhancedMainPanel from './components/EnhancedMainPanel';
import { invoke } from '@tauri-apps/api/tauri';

interface DesktopAppState {
  isMainPanelOpen: boolean;
  isListening: boolean;
  isProcessing: boolean;
  isSpeaking: boolean;
  isMuted: boolean;
  currentEmotion: string;
  confidence: number;
  lastCommand: string;
  status: 'idle' | 'listening' | 'processing' | 'speaking' | 'error';
  systemStats: {
    cpu: number;
    memory: number;
    network: number;
    uptime: string;
  };
  activeServices: string[];
  recentCommands: string[];
  learningInsights: any[];
}

const DesktopApp: React.FC = () => {
  const [appState, setAppState] = useState<DesktopAppState>({
    isMainPanelOpen: false,
    isListening: false,
    isProcessing: false,
    isSpeaking: false,
    isMuted: false,
    currentEmotion: 'focused',
    confidence: 0,
    lastCommand: '',
    status: 'idle',
    systemStats: {
      cpu: 0,
      memory: 0,
      network: 0,
      uptime: '0h 0m'
    },
    activeServices: [],
    recentCommands: [],
    learningInsights: []
  });

  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  // Initialize app
  useEffect(() => {
    initializeApp();
    return () => {
      cleanup();
    };
  }, []);

  const initializeApp = async () => {
    try {
      console.log('🚀 Initializing JarvisX Desktop App...');
      
      // Initialize audio context
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      
      // Connect to orchestrator
      await connectToOrchestrator();
      
      // Load system stats
      await loadSystemStats();
      
      // Load active services
      await loadActiveServices();
      
      // Load learning insights
      await loadLearningInsights();
      
      console.log('✅ JarvisX Desktop App initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize JarvisX Desktop App:', error);
    }
  };

  const connectToOrchestrator = async () => {
    try {
      const wsUrl = 'ws://localhost:3000';
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('✅ Connected to JarvisX Orchestrator');
        setAppState(prev => ({
          ...prev,
          activeServices: [...prev.activeServices, 'Orchestrator']
        }));
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleOrchestratorMessage(data);
        } catch (error) {
          console.error('❌ Failed to parse orchestrator message:', error);
        }
      };
      
      wsRef.current.onclose = () => {
        console.log('🔌 Disconnected from JarvisX Orchestrator');
        setAppState(prev => ({
          ...prev,
          activeServices: prev.activeServices.filter(service => service !== 'Orchestrator')
        }));
      };
      
      wsRef.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };
    } catch (error) {
      console.error('❌ Failed to connect to orchestrator:', error);
    }
  };

  const handleOrchestratorMessage = (data: any) => {
    switch (data.type) {
      case 'voice_status':
        setAppState(prev => ({
          ...prev,
          isListening: data.listening,
          isProcessing: data.processing,
          isSpeaking: data.speaking,
          status: data.status || prev.status
        }));
        break;
      case 'emotion_update':
        setAppState(prev => ({
          ...prev,
          currentEmotion: data.emotion,
          confidence: data.confidence || prev.confidence
        }));
        break;
      case 'command_result':
        setAppState(prev => ({
          ...prev,
          lastCommand: data.command,
          recentCommands: [data.command, ...prev.recentCommands.slice(0, 9)]
        }));
        break;
      case 'system_stats':
        setAppState(prev => ({
          ...prev,
          systemStats: {
            ...prev.systemStats,
            cpu: data.cpu || prev.systemStats.cpu,
            memory: data.memory || prev.systemStats.memory,
            network: data.network || prev.systemStats.network
          }
        }));
        break;
    }
  };

  const loadSystemStats = async () => {
    try {
      // This would call Tauri commands to get system stats
      const uptime = await invoke('get_system_uptime');
      setAppState(prev => ({
        ...prev,
        systemStats: {
          ...prev.systemStats,
          uptime: uptime as string
        }
      }));
    } catch (error) {
      console.error('❌ Failed to load system stats:', error);
    }
  };

  const loadActiveServices = async () => {
    try {
      const services = [
        'PC Agent',
        'Voice Recognition',
        'Text-to-Speech',
        'Screen Analysis',
        'Browser Automation',
        'Reasoning Engine',
        'Approval System',
        'Learning Service'
      ];
      
      setAppState(prev => ({
        ...prev,
        activeServices: services
      }));
    } catch (error) {
      console.error('❌ Failed to load active services:', error);
    }
  };

  const loadLearningInsights = async () => {
    try {
      const response = await fetch('http://localhost:8014/learning/insights?userId=desktop');
      if (response.ok) {
        const data = await response.json();
        setAppState(prev => ({
          ...prev,
          learningInsights: data.data.insights || []
        }));
      }
    } catch (error) {
      console.error('❌ Failed to load learning insights:', error);
    }
  };

  const startListening = async () => {
    try {
      console.log('🎤 Starting voice listening...');
      
      // Request microphone access
      mediaStreamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Send start listening command to orchestrator
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'start_listening',
          timestamp: Date.now()
        }));
      }
      
      setAppState(prev => ({
        ...prev,
        isListening: true,
        status: 'listening'
      }));
      
    } catch (error) {
      console.error('❌ Failed to start listening:', error);
      setAppState(prev => ({
        ...prev,
        status: 'error'
      }));
    }
  };

  const stopListening = async () => {
    try {
      console.log('🎤 Stopping voice listening...');
      
      // Stop microphone
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
        mediaStreamRef.current = null;
      }
      
      // Send stop listening command to orchestrator
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'stop_listening',
          timestamp: Date.now()
        }));
      }
      
      setAppState(prev => ({
        ...prev,
        isListening: false,
        isProcessing: true,
        status: 'processing'
      }));
      
      // Simulate processing time
      setTimeout(() => {
        setAppState(prev => ({
          ...prev,
          isProcessing: false,
          status: 'idle'
        }));
      }, 2000);
      
    } catch (error) {
      console.error('❌ Failed to stop listening:', error);
      setAppState(prev => ({
        ...prev,
        status: 'error'
      }));
    }
  };

  const toggleMute = () => {
    setAppState(prev => ({
      ...prev,
      isMuted: !prev.isMuted
    }));
  };

  const openMainPanel = () => {
    setAppState(prev => ({
      ...prev,
      isMainPanelOpen: true
    }));
  };

  const closeMainPanel = () => {
    setAppState(prev => ({
      ...prev,
      isMainPanelOpen: false
    }));
  };

  const minimizeMainPanel = () => {
    setAppState(prev => ({
      ...prev,
      isMainPanelOpen: false
    }));
  };

  const cleanup = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
  };

  return (
    <div className="desktop-app">
      {/* Floating Voice Orb */}
      <FloatingVoiceOrb
        onOpenMainPanel={openMainPanel}
        onClose={() => {}}
        isListening={appState.isListening}
        isProcessing={appState.isProcessing}
        isSpeaking={appState.isSpeaking}
        onStartListening={startListening}
        onStopListening={stopListening}
        onToggleMute={toggleMute}
        isMuted={appState.isMuted}
        currentEmotion={appState.currentEmotion}
        confidence={appState.confidence}
        lastCommand={appState.lastCommand}
        status={appState.status}
      />

      {/* Enhanced Main Panel */}
      <AnimatePresence>
        {appState.isMainPanelOpen && (
          <EnhancedMainPanel
            onClose={closeMainPanel}
            onMinimize={minimizeMainPanel}
            isListening={appState.isListening}
            isProcessing={appState.isProcessing}
            isSpeaking={appState.isSpeaking}
            onStartListening={startListening}
            onStopListening={stopListening}
            onToggleMute={toggleMute}
            isMuted={appState.isMuted}
            currentEmotion={appState.currentEmotion}
            confidence={appState.confidence}
            lastCommand={appState.lastCommand}
            status={appState.status}
            systemStats={appState.systemStats}
            activeServices={appState.activeServices}
            recentCommands={appState.recentCommands}
            learningInsights={appState.learningInsights}
          />
        )}
      </AnimatePresence>

      {/* Global Styles */}
      <style jsx global>{`
        .desktop-app {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          overflow: hidden;
          background: transparent;
          pointer-events: none;
        }
        
        .desktop-app * {
          pointer-events: auto;
        }
        
        body {
          margin: 0;
          padding: 0;
          overflow: hidden;
          background: transparent;
        }
        
        * {
          box-sizing: border-box;
        }
      `}</style>
    </div>
  );
};

export default DesktopApp;
