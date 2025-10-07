/**
 * Enhanced Main Panel - Full-featured JarvisX interface
 * Complete control panel with all features
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, MicOff, Settings, X, Minimize2, Maximize2, 
  Volume2, VolumeX, Brain, Shield, Zap, BarChart3,
  Clock, Activity, Users, Globe, Smartphone, Monitor,
  ChevronDown, ChevronUp, Play, Pause, Square
} from 'lucide-react';

interface EnhancedMainPanelProps {
  onClose: () => void;
  onMinimize: () => void;
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

const EnhancedMainPanel: React.FC<EnhancedMainPanelProps> = ({
  onClose,
  onMinimize,
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
  status,
  systemStats,
  activeServices,
  recentCommands,
  learningInsights
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'control' | 'learning' | 'system' | 'settings'>('overview');
  const [isCollapsed, setIsCollapsed] = useState(false);

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

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'control', label: 'Control', icon: Zap },
    { id: 'learning', label: 'Learning', icon: Brain },
    { id: 'system', label: 'System', icon: Monitor },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  return (
    <motion.div
      className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-6xl h-[80vh] bg-gray-900/95 backdrop-blur-xl rounded-2xl border border-white/20 shadow-2xl overflow-hidden"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        transition={{ duration: 0.2 }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div className="flex items-center gap-4">
            <div 
              className="w-4 h-4 rounded-full"
              style={{ backgroundColor: getEmotionColor(currentEmotion) }}
            />
            <h1 className="text-2xl font-bold text-white">JarvisX Control Panel</h1>
            <span className="text-sm text-gray-400 capitalize">{currentEmotion}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              {isCollapsed ? <ChevronUp size={20} className="text-white" /> : <ChevronDown size={20} className="text-white" />}
            </button>
            <button
              onClick={onMinimize}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              <Minimize2 size={20} className="text-white" />
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              <X size={20} className="text-white" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-white/10">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-6 py-4 transition-colors ${
                  activeTab === tab.id
                    ? 'text-white border-b-2 border-blue-500 bg-white/5'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon size={18} />
                <span className="font-medium">{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="p-6 h-full overflow-y-auto">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Status Card */}
                <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                  <h3 className="text-lg font-semibold text-white mb-4">Current Status</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Status</span>
                      <span className="text-white capitalize">{status}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Confidence</span>
                      <span className="text-white">{Math.round(confidence)}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Emotion</span>
                      <span className="text-white capitalize">{currentEmotion}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Muted</span>
                      <span className="text-white">{isMuted ? 'Yes' : 'No'}</span>
                    </div>
                  </div>
                </div>

                {/* System Stats */}
                <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                  <h3 className="text-lg font-semibold text-white mb-4">System Performance</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-gray-400">CPU</span>
                        <span className="text-white">{systemStats.cpu}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${systemStats.cpu}%` }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-gray-400">Memory</span>
                        <span className="text-white">{systemStats.memory}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: `${systemStats.memory}%` }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-gray-400">Network</span>
                        <span className="text-white">{systemStats.network}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${systemStats.network}%` }} />
                      </div>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Uptime</span>
                      <span className="text-white">{systemStats.uptime}</span>
                    </div>
                  </div>
                </div>

                {/* Active Services */}
                <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                  <h3 className="text-lg font-semibold text-white mb-4">Active Services</h3>
                  <div className="space-y-2">
                    {activeServices.map((service, index) => (
                      <div key={index} className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-green-400 rounded-full" />
                        <span className="text-white">{service}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recent Commands */}
                <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                  <h3 className="text-lg font-semibold text-white mb-4">Recent Commands</h3>
                  <div className="space-y-2">
                    {recentCommands.slice(0, 5).map((command, index) => (
                      <div key={index} className="text-gray-300 text-sm p-2 bg-white/5 rounded">
                        {command}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Control Tab */}
          {activeTab === 'control' && (
            <div className="p-6 h-full overflow-y-auto">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Voice Control */}
                <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                  <h3 className="text-lg font-semibold text-white mb-4">Voice Control</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-center">
                      <button
                        onClick={isListening ? onStopListening : onStartListening}
                        className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${
                          isListening
                            ? 'bg-red-500 hover:bg-red-600'
                            : 'bg-blue-500 hover:bg-blue-600'
                        }`}
                      >
                        {isListening ? <MicOff size={32} className="text-white" /> : <Mic size={32} className="text-white" />}
                      </button>
                    </div>
                    <div className="text-center">
                      <span className="text-white font-medium">
                        {isListening ? 'Listening...' : 'Click to start listening'}
                      </span>
                    </div>
                    <div className="flex items-center justify-center gap-4">
                      <button
                        onClick={onToggleMute}
                        className={`p-2 rounded-lg transition-colors ${
                          isMuted ? 'bg-red-500/20 text-red-400' : 'bg-white/10 text-white'
                        }`}
                      >
                        {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Quick Actions */}
                <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                  <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
                  <div className="grid grid-cols-2 gap-3">
                    <button className="p-3 bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30 transition-colors">
                      <Zap size={20} className="mx-auto mb-2" />
                      <span className="text-sm">Execute Command</span>
                    </button>
                    <button className="p-3 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors">
                      <Shield size={20} className="mx-auto mb-2" />
                      <span className="text-sm">Safety Check</span>
                    </button>
                    <button className="p-3 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors">
                      <Brain size={20} className="mx-auto mb-2" />
                      <span className="text-sm">AI Analysis</span>
                    </button>
                    <button className="p-3 bg-yellow-500/20 text-yellow-400 rounded-lg hover:bg-yellow-500/30 transition-colors">
                      <BarChart3 size={20} className="mx-auto mb-2" />
                      <span className="text-sm">Analytics</span>
                    </button>
                  </div>
                </div>

                {/* Last Command */}
                {lastCommand && (
                  <div className="lg:col-span-2 bg-white/5 rounded-xl p-6 border border-white/10">
                    <h3 className="text-lg font-semibold text-white mb-4">Last Command</h3>
                    <div className="p-4 bg-white/5 rounded-lg">
                      <span className="text-white">{lastCommand}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Learning Tab */}
          {activeTab === 'learning' && (
            <div className="p-6 h-full overflow-y-auto">
              <div className="space-y-6">
                <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                  <h3 className="text-lg font-semibold text-white mb-4">Learning Insights</h3>
                  <div className="space-y-4">
                    {learningInsights.length > 0 ? (
                      learningInsights.map((insight, index) => (
                        <div key={index} className="p-4 bg-white/5 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-white font-medium">{insight.title}</span>
                            <span className="text-sm text-gray-400">{insight.confidence}% confidence</span>
                          </div>
                          <p className="text-gray-300 text-sm">{insight.description}</p>
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-gray-400 py-8">
                        <Brain size={48} className="mx-auto mb-4 opacity-50" />
                        <p>No learning insights yet. Start using JarvisX to generate insights!</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* System Tab */}
          {activeTab === 'system' && (
            <div className="p-6 h-full overflow-y-auto">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                  <h3 className="text-lg font-semibold text-white mb-4">System Health</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Status</span>
                      <span className="text-green-400">Healthy</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Services Running</span>
                      <span className="text-white">{activeServices.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Uptime</span>
                      <span className="text-white">{systemStats.uptime}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                  <h3 className="text-lg font-semibold text-white mb-4">Connected Devices</h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <Monitor size={20} className="text-blue-400" />
                      <span className="text-white">Desktop</span>
                      <span className="text-green-400 text-sm">Connected</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Smartphone size={20} className="text-purple-400" />
                      <span className="text-white">Mobile</span>
                      <span className="text-gray-400 text-sm">Disconnected</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Globe size={20} className="text-green-400" />
                      <span className="text-white">Web</span>
                      <span className="text-gray-400 text-sm">Disconnected</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Settings Tab */}
          {activeTab === 'settings' && (
            <div className="p-6 h-full overflow-y-auto">
              <div className="space-y-6">
                <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                  <h3 className="text-lg font-semibold text-white mb-4">Voice Settings</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Auto-listen</span>
                      <button className="w-12 h-6 bg-blue-500 rounded-full relative">
                        <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5" />
                      </button>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Voice feedback</span>
                      <button className="w-12 h-6 bg-blue-500 rounded-full relative">
                        <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5" />
                      </button>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Sinhala support</span>
                      <button className="w-12 h-6 bg-blue-500 rounded-full relative">
                        <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5" />
                      </button>
                    </div>
                  </div>
                </div>

                <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                  <h3 className="text-lg font-semibold text-white mb-4">Safety Settings</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Require approval</span>
                      <button className="w-12 h-6 bg-blue-500 rounded-full relative">
                        <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5" />
                      </button>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Emergency stop</span>
                      <button className="w-12 h-6 bg-red-500 rounded-full relative">
                        <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default EnhancedMainPanel;
