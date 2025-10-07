import React, { useState, useEffect, useRef } from 'react';
import RealisticAvatarRenderer from './RealisticAvatarRenderer';
import AvatarSelector, { AvatarPreset, AVATAR_PRESETS } from './AvatarSelector';

/**
 * 🎭 REALISTIC JOI AVATAR - INTEGRATED SYSTEM
 * 
 * Complete avatar system with:
 * - Realistic 3D rendering
 * - Avatar selection UI
 * - Celebrity-like avatars support
 * - WebSocket integration for real-time updates
 * - Emotion system
 * - Lip-sync
 * - Eye tracking
 */

interface RealisticJoiAvatarProps {
  personalityWsUrl?: string;
  avatarWsUrl?: string;
  orchestratorWsUrl?: string;
  className?: string;
  onAvatarInteraction?: (type: string, data: any) => void;
}

export default function RealisticJoiAvatar({
  personalityWsUrl = 'ws://localhost:8003/ws',
  avatarWsUrl = 'ws://localhost:8008/avatar-ws',
  orchestratorWsUrl,
  className = '',
  onAvatarInteraction,
}: RealisticJoiAvatarProps) {
  // Avatar state
  const [selectedAvatar, setSelectedAvatar] = useState<AvatarPreset>(AVATAR_PRESETS[0]);
  const [showSelector, setShowSelector] = useState(false);
  
  // Animation state
  const [emotion, setEmotion] = useState('neutral');
  const [intensity, setIntensity] = useState(0.7);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [lipSyncData, setLipSyncData] = useState<number[]>([]);
  const [currentPhoneme, setCurrentPhoneme] = useState<string>('');
  const [lookAtPosition, setLookAtPosition] = useState<[number, number, number]>([0, 1.6, 2]);
  
  // WebSocket refs
  const personalityWsRef = useRef<WebSocket | null>(null);
  const avatarWsRef = useRef<WebSocket | null>(null);
  
  // Stats
  const [stats, setStats] = useState({
    connected: false,
    latency: 0,
    fps: 60,
  });

  // Connect to WebSocket servers
  useEffect(() => {
    // Connect to Personality Service
    if (personalityWsUrl) {
      const ws = new WebSocket(personalityWsUrl);
      
      ws.onopen = () => {
        console.log('✅ Connected to Personality Service');
        setStats(prev => ({ ...prev, connected: true }));
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle emotion updates
          if (data.type === 'emotion_update') {
            setEmotion(data.emotion);
            setIntensity(data.intensity || 0.7);
          }
          
          // Handle speaking status
          if (data.type === 'speaking_status') {
            setIsSpeaking(data.isSpeaking);
          }
          
          // Handle lip-sync data
          if (data.type === 'lip_sync_data') {
            setLipSyncData(data.visemes || []);
            setCurrentPhoneme(data.currentPhoneme || '');
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('❌ Personality WebSocket error:', error);
      };
      
      ws.onclose = () => {
        console.log('Disconnected from Personality Service');
        setStats(prev => ({ ...prev, connected: false }));
      };
      
      personalityWsRef.current = ws;
    }

    // Connect to Avatar Service
    if (avatarWsUrl) {
      const ws = new WebSocket(avatarWsUrl);
      
      ws.onopen = () => {
        console.log('✅ Connected to Avatar Service');
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle animation cues
          if (data.type === 'animation_cues') {
            if (data.emotion) setEmotion(data.emotion);
            if (data.intensity !== undefined) setIntensity(data.intensity);
          }
        } catch (error) {
          console.error('Error parsing Avatar WebSocket message:', error);
        }
      };
      
      avatarWsRef.current = ws;
    }

    // Cleanup
    return () => {
      personalityWsRef.current?.close();
      avatarWsRef.current?.close();
    };
  }, [personalityWsUrl, avatarWsUrl]);

  // Mouse tracking for look-at
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth) * 2 - 1;
      const y = -(e.clientY / window.innerHeight) * 2 + 1;
      
      // Convert screen space to 3D position
      setLookAtPosition([
        x * 2,
        y * 2 + 1.6, // Offset to head height
        2,
      ]);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleAvatarSelect = (preset: AvatarPreset) => {
    setSelectedAvatar(preset);
    setShowSelector(false);
    
    if (onAvatarInteraction) {
      onAvatarInteraction('avatar_changed', { avatarId: preset.id, avatarName: preset.name });
    }
  };

  const handleCustomUpload = (file: File) => {
    // Create object URL for the uploaded file
    const modelUrl = URL.createObjectURL(file);
    
    const customPreset: AvatarPreset = {
      id: `custom-${Date.now()}`,
      name: file.name.replace(/\.[^/.]+$/, ''),
      description: 'Custom uploaded model',
      modelUrl,
      thumbnail: '/placeholder-avatar.png',
      category: 'custom',
      tags: ['custom', 'uploaded'],
    };
    
    setSelectedAvatar(customPreset);
    setShowSelector(false);
    
    if (onAvatarInteraction) {
      onAvatarInteraction('custom_upload', { fileName: file.name });
    }
  };

  return (
    <div className={`relative w-full h-full ${className}`}>
      {/* Avatar Renderer */}
      <div className="absolute inset-0">
        <RealisticAvatarRenderer
          modelUrl={selectedAvatar.modelUrl}
          emotion={emotion}
          intensity={intensity}
          isSpeaking={isSpeaking}
          lipSyncData={lipSyncData}
          currentPhoneme={currentPhoneme}
          lookAt={lookAtPosition}
          enablePostProcessing={true}
        />
      </div>

      {/* Avatar Selector Modal */}
      {showSelector && (
        <div className="absolute inset-0 z-50 bg-black/80 backdrop-blur-sm">
          <div className="absolute inset-4 md:inset-8 lg:inset-16 bg-gray-900 rounded-2xl overflow-hidden shadow-2xl">
            <AvatarSelector
              currentAvatarId={selectedAvatar.id}
              onSelect={handleAvatarSelect}
              onCustomUpload={handleCustomUpload}
            />
            
            {/* Close button */}
            <button
              onClick={() => setShowSelector(false)}
              className="absolute top-4 right-4 w-10 h-10 bg-gray-800 hover:bg-gray-700 rounded-full flex items-center justify-center transition-colors z-10"
            >
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Control Panel */}
      <div className="absolute top-4 right-4 space-y-2">
        {/* Change Avatar Button */}
        <button
          onClick={() => setShowSelector(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-lg flex items-center gap-2 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          Change Avatar
        </button>

        {/* Stats Panel */}
        <div className="bg-black/50 backdrop-blur-sm rounded-lg p-3 space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${stats.connected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-white">{stats.connected ? 'Connected' : 'Disconnected'}</span>
          </div>
          <div className="text-gray-400">
            Avatar: {selectedAvatar.name}
          </div>
          <div className="text-gray-400">
            FPS: {stats.fps}
          </div>
        </div>

        {/* Quick Emotion Test Buttons */}
        <div className="bg-black/50 backdrop-blur-sm rounded-lg p-3 space-y-2">
          <div className="text-xs text-gray-400 mb-2">Quick Test:</div>
          <div className="grid grid-cols-2 gap-1">
            {['happy', 'excited', 'concerned', 'curious'].map((emo) => (
              <button
                key={emo}
                onClick={() => setEmotion(emo)}
                className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                  emotion === emo
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {emo}
              </button>
            ))}
          </div>
          
          {/* Speaking toggle */}
          <button
            onClick={() => setIsSpeaking(!isSpeaking)}
            className={`w-full px-2 py-1 rounded text-xs font-medium transition-colors ${
              isSpeaking
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {isSpeaking ? '🎤 Speaking' : '🔇 Silent'}
          </button>
        </div>
      </div>

      {/* Avatar Info Overlay */}
      <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-sm rounded-lg p-4 max-w-sm">
        <div className="flex items-start gap-3">
          <img
            src={selectedAvatar.thumbnail}
            alt={selectedAvatar.name}
            className="w-16 h-16 rounded-lg object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).src = '/placeholder-avatar.png';
            }}
          />
          <div className="flex-1">
            <h3 className="text-white font-semibold mb-1">{selectedAvatar.name}</h3>
            <p className="text-gray-400 text-xs mb-2">{selectedAvatar.description}</p>
            <div className="flex gap-1 flex-wrap">
              {selectedAvatar.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-0.5 bg-gray-700 text-gray-300 rounded text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

