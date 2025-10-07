import React, { useState } from 'react';

/**
 * 🎭 AVATAR SELECTOR
 * 
 * Choose from:
 * - Ready Player Me avatars (customizable)
 * - Celebrity-like presets
 * - Custom GLB/GLTF models
 * 
 * How to get celebrity avatars:
 * 1. Ready Player Me with photo: https://readyplayer.me/
 * 2. Buy from marketplaces:
 *    - Sketchfab: https://sketchfab.com/3d-models?features=downloadable&type=models
 *    - TurboSquid: https://www.turbosquid.com/
 *    - CGTrader: https://www.cgtrader.com/
 * 3. Commission custom model from 3D artist
 * 4. Use AI generators:
 *    - MetaHuman (Unreal Engine)
 *    - Character Creator 4
 *    - Meshcapade
 */

export interface AvatarPreset {
  id: string;
  name: string;
  description: string;
  modelUrl: string;
  thumbnail: string;
  category: 'readyplayerme' | 'celebrity' | 'custom' | 'anime';
  tags: string[];
}

// Pre-configured avatars
export const AVATAR_PRESETS: AvatarPreset[] = [
  // Ready Player Me Avatars (Free!)
  {
    id: 'rpm-female-1',
    name: 'Joi (Default)',
    description: 'Modern holographic assistant',
    modelUrl: 'https://models.readyplayer.me/64bfa15f0e72c63d7c3934a6.glb',
    thumbnail: 'https://models.readyplayer.me/64bfa15f0e72c63d7c3934a6.png',
    category: 'readyplayerme',
    tags: ['female', 'professional', 'modern'],
  },
  {
    id: 'rpm-female-2',
    name: 'Emma',
    description: 'Friendly companion',
    modelUrl: 'https://models.readyplayer.me/658f5c5f8b0c4c001a3e7b5d.glb',
    thumbnail: 'https://models.readyplayer.me/658f5c5f8b0c4c001a3e7b5d.png',
    category: 'readyplayerme',
    tags: ['female', 'friendly', 'casual'],
  },
  {
    id: 'rpm-male-1',
    name: 'Alex',
    description: 'Professional assistant',
    modelUrl: 'https://models.readyplayer.me/64bfa15f0e72c63d7c3934a7.glb',
    thumbnail: 'https://models.readyplayer.me/64bfa15f0e72c63d7c3934a7.png',
    category: 'readyplayerme',
    tags: ['male', 'professional', 'formal'],
  },
  
  // Celebrity-Like Models (Examples - replace with actual models)
  {
    id: 'celebrity-megan',
    name: 'Megan (Celebrity Style)',
    description: 'Hollywood glamour - Megan Fox inspired',
    modelUrl: '/models/avatars/celebrity-female-1.glb', // You need to add this
    thumbnail: '/models/avatars/celebrity-female-1.jpg',
    category: 'celebrity',
    tags: ['female', 'glamorous', 'hollywood'],
  },
  {
    id: 'celebrity-scarlett',
    name: 'Scarlett (Celebrity Style)',
    description: 'Elegant and sophisticated',
    modelUrl: '/models/avatars/celebrity-female-2.glb',
    thumbnail: '/models/avatars/celebrity-female-2.jpg',
    category: 'celebrity',
    tags: ['female', 'elegant', 'sophisticated'],
  },
  {
    id: 'celebrity-keanu',
    name: 'Neo (Celebrity Style)',
    description: 'Keanu Reeves inspired',
    modelUrl: '/models/avatars/celebrity-male-1.glb',
    thumbnail: '/models/avatars/celebrity-male-1.jpg',
    category: 'celebrity',
    tags: ['male', 'cool', 'action'],
  },
  
  // Custom slot for user uploads
  {
    id: 'custom-upload',
    name: 'Upload Custom Model',
    description: 'Use your own GLB/GLTF file',
    modelUrl: '',
    thumbnail: '/placeholder-upload.png',
    category: 'custom',
    tags: ['custom'],
  },
];

interface AvatarSelectorProps {
  currentAvatarId?: string;
  onSelect: (preset: AvatarPreset) => void;
  onCustomUpload?: (file: File) => void;
  className?: string;
}

export default function AvatarSelector({
  currentAvatarId,
  onSelect,
  onCustomUpload,
  className = '',
}: AvatarSelectorProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredPresets = AVATAR_PRESETS.filter((preset) => {
    const matchesCategory = selectedCategory === 'all' || preset.category === selectedCategory;
    const matchesSearch = preset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         preset.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         preset.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && onCustomUpload) {
      onCustomUpload(file);
    }
  };

  return (
    <div className={`flex flex-col h-full bg-gray-900 ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-800">
        <h2 className="text-2xl font-bold text-white mb-2">Choose Your Avatar</h2>
        <p className="text-gray-400 text-sm">
          Select from presets or upload your own 3D model
        </p>
      </div>

      {/* Search & Filters */}
      <div className="p-6 space-y-4 border-b border-gray-800">
        {/* Search */}
        <input
          type="text"
          placeholder="Search avatars..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
        />

        {/* Category Filters */}
        <div className="flex gap-2 flex-wrap">
          {['all', 'readyplayerme', 'celebrity', 'custom', 'anime'].map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {category === 'all' ? 'All' : category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Avatar Grid */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredPresets.map((preset) => (
            <div
              key={preset.id}
              onClick={() => {
                if (preset.id === 'custom-upload') {
                  document.getElementById('avatar-file-input')?.click();
                } else {
                  onSelect(preset);
                }
              }}
              className={`group cursor-pointer rounded-xl overflow-hidden bg-gray-800 hover:bg-gray-750 transition-all duration-200 ${
                currentAvatarId === preset.id ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              {/* Thumbnail */}
              <div className="aspect-square bg-gray-700 relative overflow-hidden">
                {preset.id === 'custom-upload' ? (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <svg
                      className="w-16 h-16 text-gray-500 group-hover:text-blue-500 transition-colors"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                      />
                    </svg>
                  </div>
                ) : (
                  <img
                    src={preset.thumbnail}
                    alt={preset.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = '/placeholder-avatar.png';
                    }}
                  />
                )}

                {/* Category Badge */}
                <div className="absolute top-2 right-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    preset.category === 'celebrity' ? 'bg-purple-600 text-white' :
                    preset.category === 'readyplayerme' ? 'bg-blue-600 text-white' :
                    preset.category === 'custom' ? 'bg-green-600 text-white' :
                    'bg-pink-600 text-white'
                  }`}>
                    {preset.category === 'readyplayerme' ? 'RPM' : preset.category}
                  </span>
                </div>

                {/* Selected Indicator */}
                {currentAvatarId === preset.id && (
                  <div className="absolute inset-0 bg-blue-500/20 flex items-center justify-center">
                    <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="p-3">
                <h3 className="font-semibold text-white text-sm mb-1 truncate">
                  {preset.name}
                </h3>
                <p className="text-gray-400 text-xs line-clamp-2 mb-2">
                  {preset.description}
                </p>
                {/* Tags */}
                <div className="flex gap-1 flex-wrap">
                  {preset.tags.slice(0, 3).map((tag) => (
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
          ))}
        </div>

        {/* No results */}
        {filteredPresets.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg mb-2">No avatars found</p>
            <p className="text-gray-500 text-sm">Try a different search or category</p>
          </div>
        )}
      </div>

      {/* Hidden file input */}
      <input
        id="avatar-file-input"
        type="file"
        accept=".glb,.gltf"
        onChange={handleFileUpload}
        className="hidden"
      />

      {/* Footer with instructions */}
      <div className="p-4 border-t border-gray-800 bg-gray-800/50">
        <div className="text-xs text-gray-400 space-y-1">
          <p>💡 <strong>Get celebrity avatars:</strong></p>
          <ul className="list-disc list-inside pl-2 space-y-0.5">
            <li>Create with photo: <a href="https://readyplayer.me/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">ReadyPlayer.me</a></li>
            <li>Buy models: <a href="https://sketchfab.com/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">Sketchfab</a>, <a href="https://www.turbosquid.com/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">TurboSquid</a></li>
            <li>Use MetaHuman Creator (Unreal Engine) for photorealistic faces</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

