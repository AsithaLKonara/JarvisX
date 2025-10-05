/**
 * JarvisX Desktop App - Main Application Component
 * Siri-style AI assistant interface with real-time streaming
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AssistantWindow from './components/AssistantWindow';
import TradingDashboard from './components/TradingDashboard';
import HumanLikeInterface from './components/HumanLikeInterface';
import { Mic, Settings, TrendingUp, X } from 'lucide-react';

// App state interface
interface AppState {
  isAssistantOpen: boolean;
  isTradingOpen: boolean;
  isMinimized: boolean;
  currentView: 'assistant' | 'trading' | 'settings' | null;
}

function App() {
  // State
  const [appState, setAppState] = useState<AppState>({
    isAssistantOpen: false,
    isTradingOpen: false,
    isMinimized: false,
    currentView: null
  });

  const [isConnected, setIsConnected] = useState(false);
  const [orchestratorUrl, setOrchestratorUrl] = useState('ws://localhost:3000');
  const [personalityUrl, setPersonalityUrl] = useState('ws://localhost:8007');

  // Initialize app
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Check orchestrator connection
      const response = await fetch('http://localhost:3000/health');
      if (response.ok) {
        setIsConnected(true);
        console.log('✅ Connected to JarvisX Orchestrator');
      }
    } catch (error) {
      console.warn('⚠️ Could not connect to orchestrator:', error);
      setIsConnected(false);
    }
  };

  // Event handlers
  const handleOpenAssistant = () => {
    setAppState(prev => ({
      ...prev,
      isAssistantOpen: true,
      isMinimized: false,
      currentView: 'assistant'
    }));
  };

  const handleOpenTrading = () => {
    setAppState(prev => ({
      ...prev,
      isTradingOpen: true,
      currentView: 'trading'
    }));
  };

  const handleCloseAssistant = () => {
    setAppState(prev => ({
      ...prev,
      isAssistantOpen: false,
      currentView: null
    }));
  };

  const handleCloseTrading = () => {
    setAppState(prev => ({
      ...prev,
      isTradingOpen: false,
      currentView: null
    }));
  };

  const handleToggleMinimize = () => {
    setAppState(prev => ({
      ...prev,
      isMinimized: !prev.isMinimized
    }));
  };

  // Global hotkey handler (F1 for assistant)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'F1') {
        event.preventDefault();
        if (appState.isAssistantOpen) {
          handleCloseAssistant();
        } else {
          handleOpenAssistant();
        }
      }
      
      if (event.key === 'F2') {
        event.preventDefault();
        if (appState.isTradingOpen) {
          handleCloseTrading();
        } else {
          handleOpenTrading();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [appState.isAssistantOpen, appState.isTradingOpen]);

  return (
    <div className="jarvisx-app min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* Background Pattern */}
      <div className="fixed inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, white 1px, transparent 0)`,
          backgroundSize: '20px 20px'
        }} />
      </div>

      {/* Main Content */}
      <div className="relative z-10">
        {!appState.isAssistantOpen && !appState.isTradingOpen && (
          <div className="flex flex-col items-center justify-center min-h-screen p-8">
            {/* Logo and Title */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center mb-12"
            >
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center">
                <span className="text-white text-3xl font-bold">J</span>
              </div>
              <h1 className="text-4xl font-bold text-white mb-2">JarvisX</h1>
              <p className="text-gray-400 text-lg">Sinhala-enabled AI Assistant</p>
              <div className="flex items-center justify-center gap-2 mt-4">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
                <span className="text-sm text-gray-400">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-md w-full"
            >
              <button
                onClick={handleOpenAssistant}
                className="group relative p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20 hover:bg-white/20 transition-all duration-300"
              >
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <Mic size={24} className="text-white" />
                  </div>
                  <h3 className="text-white font-semibold text-lg mb-2">AI Assistant</h3>
                  <p className="text-gray-400 text-sm text-center">
                    Voice commands, screen sharing, and real-time action streaming
                  </p>
                </div>
                <div className="absolute top-2 right-2 text-xs text-gray-500">F1</div>
              </button>

              <button
                onClick={handleOpenTrading}
                className="group relative p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20 hover:bg-white/20 transition-all duration-300"
              >
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-r from-green-500 to-blue-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <TrendingUp size={24} className="text-white" />
                  </div>
                  <h3 className="text-white font-semibold text-lg mb-2">Trading Dashboard</h3>
                  <p className="text-gray-400 text-sm text-center">
                    AI-powered trading with safety controls and real-time monitoring
                  </p>
                </div>
                <div className="absolute top-2 right-2 text-xs text-gray-500">F2</div>
              </button>
            </motion.div>

            {/* Features List */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="mt-16 max-w-2xl"
            >
              <h2 className="text-white text-xl font-semibold mb-6 text-center">Features</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-indigo-400 text-sm font-medium mb-1">Voice Control</div>
                  <div className="text-gray-400 text-xs">Sinhala & English support</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-green-400 text-sm font-medium mb-1">Real-time Streaming</div>
                  <div className="text-gray-400 text-xs">Live screen & action feed</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-purple-400 text-sm font-medium mb-1">AI Automation</div>
                  <div className="text-gray-400 text-xs">Smart task execution</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-blue-400 text-sm font-medium mb-1">Trading Integration</div>
                  <div className="text-gray-400 text-xs">Safe automated trading</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-yellow-400 text-sm font-medium mb-1">Mobile Control</div>
                  <div className="text-gray-400 text-xs">Remote access & approval</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-red-400 text-sm font-medium mb-1">Security First</div>
                  <div className="text-gray-400 text-xs">Enterprise-grade safety</div>
                </div>
              </div>
            </motion.div>
          </div>
        )}

        {/* Assistant Window */}
        <AnimatePresence>
          {appState.isAssistantOpen && (
            <AssistantWindow
              wsUrl={orchestratorUrl.replace('http', 'ws')}
              onClose={handleCloseAssistant}
              isMinimized={appState.isMinimized}
              onToggleMinimize={handleToggleMinimize}
            />
          )}
        </AnimatePresence>

        {/* Trading Dashboard */}
        <AnimatePresence>
          {appState.isTradingOpen && (
            <TradingDashboard
              orchestratorUrl="http://localhost:3000"
              onClose={handleCloseTrading}
            />
          )}
        </AnimatePresence>

        {/* Human-like Interface Overlay */}
        <HumanLikeInterface 
          wsUrl={personalityUrl}
          onInteraction={(type, data) => {
            console.log('Human interaction:', type, data);
          }}
        />
      </div>

      {/* Global Styles */}
      <style jsx global>{`
        .jarvisx-app {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        body {
          margin: 0;
          padding: 0;
          overflow: hidden;
        }
        
        * {
          box-sizing: border-box;
        }
      `}</style>
    </div>
  );
}

export default App;
