/**
 * Avatar Customization UI
 * Allows users to customize their Joi avatar appearance and personality
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface AvatarCustomizationProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (config: AvatarConfig) => void;
  currentConfig?: AvatarConfig;
}

export interface AvatarConfig {
  appearance: {
    style: 'holographic' | 'realistic' | 'anime' | 'abstract';
    primaryColor: string;
    secondaryColor: string;
    glowIntensity: number;
    particleEffect: 'sparkles' | 'burst' | 'pulse' | 'glow' | 'none';
    opacity: number;
  };
  personality: {
    name: string;
    voice: 'default' | 'warm' | 'professional' | 'playful' | 'confident';
    responsiveness: number; // 0-100
    emotionalRange: number; // 0-100
  };
  behavior: {
    blinkRate: number; // 0-100
    headMovementIntensity: number; // 0-100
    expressiveness: number; // 0-100
    autonomousMovement: boolean;
  };
  lighting: {
    enabled: boolean;
    ambientSync: boolean;
    smartLightsEnabled: boolean;
    intensity: number; // 0-100
  };
}

const DEFAULT_CONFIG: AvatarConfig = {
  appearance: {
    style: 'holographic',
    primaryColor: '#3B82F6',
    secondaryColor: '#8B5CF6',
    glowIntensity: 70,
    particleEffect: 'sparkles',
    opacity: 90,
  },
  personality: {
    name: 'Joi',
    voice: 'default',
    responsiveness: 80,
    emotionalRange: 75,
  },
  behavior: {
    blinkRate: 40,
    headMovementIntensity: 60,
    expressiveness: 80,
    autonomousMovement: true,
  },
  lighting: {
    enabled: true,
    ambientSync: true,
    smartLightsEnabled: false,
    intensity: 70,
  },
};

export function AvatarCustomization({
  isOpen,
  onClose,
  onSave,
  currentConfig = DEFAULT_CONFIG
}: AvatarCustomizationProps) {
  const [config, setConfig] = useState<AvatarConfig>(currentConfig);
  const [activeTab, setActiveTab] = useState<'appearance' | 'personality' | 'behavior' | 'lighting'>('appearance');

  const updateConfig = (section: keyof AvatarConfig, key: string, value: any) => {
    setConfig((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value,
      },
    }));
  };

  const handleSave = () => {
    onSave(config);
    onClose();
  };

  const handleReset = () => {
    setConfig(DEFAULT_CONFIG);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="avatar-customization fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="customization-panel bg-gray-900 rounded-2xl shadow-2xl border border-white/10 w-full max-w-4xl max-h-[90vh] overflow-hidden"
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Avatar Customization</h2>
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-white/10">
            {(['appearance', 'personality', 'behavior', 'lighting'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 px-6 py-4 text-sm font-medium capitalize transition-colors ${
                  activeTab === tab
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
            {/* Appearance Tab */}
            {activeTab === 'appearance' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-white text-sm font-medium mb-3">Avatar Style</label>
                  <div className="grid grid-cols-4 gap-3">
                    {(['holographic', 'realistic', 'anime', 'abstract'] as const).map((style) => (
                      <button
                        key={style}
                        onClick={() => updateConfig('appearance', 'style', style)}
                        className={`p-4 rounded-lg border-2 transition-all capitalize ${
                          config.appearance.style === style
                            ? 'border-blue-500 bg-blue-500/20'
                            : 'border-white/10 hover:border-white/30'
                        }`}
                      >
                        <span className="text-white text-sm">{style}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-white text-sm font-medium mb-3">Primary Color</label>
                  <div className="flex items-center gap-4">
                    <input
                      type="color"
                      value={config.appearance.primaryColor}
                      onChange={(e) => updateConfig('appearance', 'primaryColor', e.target.value)}
                      className="w-16 h-16 rounded-lg border-2 border-white/10 cursor-pointer"
                    />
                    <input
                      type="text"
                      value={config.appearance.primaryColor}
                      onChange={(e) => updateConfig('appearance', 'primaryColor', e.target.value)}
                      className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-white text-sm font-medium mb-3">Secondary Color</label>
                  <div className="flex items-center gap-4">
                    <input
                      type="color"
                      value={config.appearance.secondaryColor}
                      onChange={(e) => updateConfig('appearance', 'secondaryColor', e.target.value)}
                      className="w-16 h-16 rounded-lg border-2 border-white/10 cursor-pointer"
                    />
                    <input
                      type="text"
                      value={config.appearance.secondaryColor}
                      onChange={(e) => updateConfig('appearance', 'secondaryColor', e.target.value)}
                      className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Glow Intensity: {config.appearance.glowIntensity}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={config.appearance.glowIntensity}
                    onChange={(e) => updateConfig('appearance', 'glowIntensity', parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-white text-sm font-medium mb-3">Particle Effect</label>
                  <select
                    value={config.appearance.particleEffect}
                    onChange={(e) => updateConfig('appearance', 'particleEffect', e.target.value)}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  >
                    <option value="sparkles">Sparkles</option>
                    <option value="burst">Burst</option>
                    <option value="pulse">Pulse</option>
                    <option value="glow">Glow</option>
                    <option value="none">None</option>
                  </select>
                </div>

                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Opacity: {config.appearance.opacity}%
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="100"
                    value={config.appearance.opacity}
                    onChange={(e) => updateConfig('appearance', 'opacity', parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            )}

            {/* Personality Tab */}
            {activeTab === 'personality' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-white text-sm font-medium mb-3">Avatar Name</label>
                  <input
                    type="text"
                    value={config.personality.name}
                    onChange={(e) => updateConfig('personality', 'name', e.target.value)}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                    placeholder="Enter avatar name..."
                  />
                </div>

                <div>
                  <label className="block text-white text-sm font-medium mb-3">Voice Style</label>
                  <select
                    value={config.personality.voice}
                    onChange={(e) => updateConfig('personality', 'voice', e.target.value)}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  >
                    <option value="default">Default</option>
                    <option value="warm">Warm & Friendly</option>
                    <option value="professional">Professional</option>
                    <option value="playful">Playful</option>
                    <option value="confident">Confident</option>
                  </select>
                </div>

                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Responsiveness: {config.personality.responsiveness}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={config.personality.responsiveness}
                    onChange={(e) => updateConfig('personality', 'responsiveness', parseInt(e.target.value))}
                    className="w-full"
                  />
                  <p className="text-gray-400 text-xs mt-1">How quickly the avatar responds to interactions</p>
                </div>

                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Emotional Range: {config.personality.emotionalRange}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={config.personality.emotionalRange}
                    onChange={(e) => updateConfig('personality', 'emotionalRange', parseInt(e.target.value))}
                    className="w-full"
                  />
                  <p className="text-gray-400 text-xs mt-1">How expressive the avatar's emotions are</p>
                </div>
              </div>
            )}

            {/* Behavior Tab */}
            {activeTab === 'behavior' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Blink Rate: {config.behavior.blinkRate}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={config.behavior.blinkRate}
                    onChange={(e) => updateConfig('behavior', 'blinkRate', parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Head Movement: {config.behavior.headMovementIntensity}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={config.behavior.headMovementIntensity}
                    onChange={(e) => updateConfig('behavior', 'headMovementIntensity', parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Expressiveness: {config.behavior.expressiveness}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={config.behavior.expressiveness}
                    onChange={(e) => updateConfig('behavior', 'expressiveness', parseInt(e.target.value))}
                    className="w-full"
                  />
                  <p className="text-gray-400 text-xs mt-1">Intensity of facial expressions and gestures</p>
                </div>

                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <div className="text-white text-sm font-medium">Autonomous Movement</div>
                    <div className="text-gray-400 text-xs">Avatar moves naturally when idle</div>
                  </div>
                  <button
                    onClick={() => updateConfig('behavior', 'autonomousMovement', !config.behavior.autonomousMovement)}
                    className={`relative w-14 h-8 rounded-full transition-colors ${
                      config.behavior.autonomousMovement ? 'bg-blue-500' : 'bg-gray-600'
                    }`}
                  >
                    <div className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform ${
                      config.behavior.autonomousMovement ? 'translate-x-6' : 'translate-x-0'
                    }`} />
                  </button>
                </div>
              </div>
            )}

            {/* Lighting Tab */}
            {activeTab === 'lighting' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <div className="text-white text-sm font-medium">Ambient Lighting</div>
                    <div className="text-gray-400 text-xs">Enable emotional ambient effects</div>
                  </div>
                  <button
                    onClick={() => updateConfig('lighting', 'enabled', !config.lighting.enabled)}
                    className={`relative w-14 h-8 rounded-full transition-colors ${
                      config.lighting.enabled ? 'bg-blue-500' : 'bg-gray-600'
                    }`}
                  >
                    <div className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform ${
                      config.lighting.enabled ? 'translate-x-6' : 'translate-x-0'
                    }`} />
                  </button>
                </div>

                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <div className="text-white text-sm font-medium">Ambient Sync</div>
                    <div className="text-gray-400 text-xs">Sync screen glow with avatar emotion</div>
                  </div>
                  <button
                    onClick={() => updateConfig('lighting', 'ambientSync', !config.lighting.ambientSync)}
                    className={`relative w-14 h-8 rounded-full transition-colors ${
                      config.lighting.ambientSync ? 'bg-blue-500' : 'bg-gray-600'
                    }`}
                  >
                    <div className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform ${
                      config.lighting.ambientSync ? 'translate-x-6' : 'translate-x-0'
                    }`} />
                  </button>
                </div>

                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div>
                    <div className="text-white text-sm font-medium">Smart Lights</div>
                    <div className="text-gray-400 text-xs">Connect to Philips Hue, LIFX, etc.</div>
                  </div>
                  <button
                    onClick={() => updateConfig('lighting', 'smartLightsEnabled', !config.lighting.smartLightsEnabled)}
                    className={`relative w-14 h-8 rounded-full transition-colors ${
                      config.lighting.smartLightsEnabled ? 'bg-blue-500' : 'bg-gray-600'
                    }`}
                  >
                    <div className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform ${
                      config.lighting.smartLightsEnabled ? 'translate-x-6' : 'translate-x-0'
                    }`} />
                  </button>
                </div>

                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Lighting Intensity: {config.lighting.intensity}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={config.lighting.intensity}
                    onChange={(e) => updateConfig('lighting', 'intensity', parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-white/10 flex items-center justify-between">
            <button
              onClick={handleReset}
              className="px-6 py-2 text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              Reset to Default
            </button>
            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="px-6 py-2 text-white hover:bg-white/10 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
              >
                Save Changes
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

export default AvatarCustomization;

