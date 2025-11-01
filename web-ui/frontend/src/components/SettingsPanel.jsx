import { X } from 'lucide-react'

export default function SettingsPanel({ 
  theme, 
  onThemeChange, 
  ttsEnabled, 
  onTtsToggle,
  showAvatar,
  onAvatarToggle,
  onClose 
}) {
  return (
    <div className="settings-overlay fixed inset-0 flex items-center justify-center p-4"
         style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)', zIndex: 100 }}
         onClick={onClose}>
      
      <div className="settings-panel max-w-md w-full p-6 rounded-xl"
           style={{
             backgroundColor: 'var(--bg-primary)',
             border: `2px solid var(--border)`,
             boxShadow: `0 8px 32px var(--shadow-lg)`
           }}
           onClick={(e) => e.stopPropagation()}>
        
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold" style={{ color: 'var(--accent-primary)' }}>
            ⚙️ Settings
          </h2>
          <button 
            onClick={onClose}
            className="p-2 rounded-lg hover:opacity-70 transition"
            style={{ backgroundColor: 'var(--border)' }}>
            <X size={20} />
          </button>
        </div>
        
        {/* Settings Options */}
        <div className="space-y-6">
          
          {/* Theme Selection */}
          <div className="setting-item">
            <label className="block text-sm font-semibold mb-2">
              🎨 Visual Theme
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => onThemeChange('professional')}
                className={`theme-option p-3 rounded-lg text-center transition ${
                  theme === 'professional' ? 'ring-2' : ''
                }`}
                style={{
                  backgroundColor: theme === 'professional' ? 'var(--accent-primary)' : 'var(--bg-secondary)',
                  color: theme === 'professional' ? '#ffffff' : 'var(--text-primary)',
                  ringColor: 'var(--accent-primary)'
                }}>
                <div className="text-2xl mb-1">💼</div>
                <div className="text-xs">Professional</div>
              </button>
              
              <button
                onClick={() => onThemeChange('terminal')}
                className={`theme-option p-3 rounded-lg text-center transition ${
                  theme === 'terminal' ? 'ring-2' : ''
                }`}
                style={{
                  backgroundColor: theme === 'terminal' ? 'var(--accent-primary)' : 'var(--bg-secondary)',
                  color: theme === 'terminal' ? '#ffffff' : 'var(--text-primary)',
                  ringColor: 'var(--accent-primary)'
                }}>
                <div className="text-2xl mb-1">💻</div>
                <div className="text-xs">Terminal</div>
              </button>
              
              <button
                onClick={() => onThemeChange('avatar')}
                className={`theme-option p-3 rounded-lg text-center transition ${
                  theme === 'avatar' ? 'ring-2' : ''
                }`}
                style={{
                  backgroundColor: theme === 'avatar' ? 'var(--accent-primary)' : 'var(--bg-secondary)',
                  color: theme === 'avatar' ? '#ffffff' : 'var(--text-primary)',
                  ringColor: 'var(--accent-primary)'
                }}>
                <div className="text-2xl mb-1">🤖</div>
                <div className="text-xs">Avatar</div>
              </button>
            </div>
          </div>
          
          {/* TTS Toggle */}
          <div className="setting-item">
            <label className="flex items-center justify-between">
              <span className="text-sm font-semibold">🔊 Voice Output (TTS)</span>
              <button
                onClick={onTtsToggle}
                className={`toggle-switch relative w-12 h-6 rounded-full transition ${
                  ttsEnabled ? 'bg-green-500' : ''
                }`}
                style={{ backgroundColor: ttsEnabled ? 'var(--success)' : 'var(--border)' }}>
                <div className={`toggle-thumb absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                  ttsEnabled ? 'translate-x-6' : 'translate-x-0'
                }`} />
              </button>
            </label>
            <p className="text-xs opacity-60 mt-1">
              Enable Jarvis to speak responses
            </p>
          </div>
          
          {/* Avatar Toggle */}
          <div className="setting-item">
            <label className="flex items-center justify-between">
              <span className="text-sm font-semibold">🤖 Show Avatar</span>
              <button
                onClick={onAvatarToggle}
                disabled={theme !== 'avatar'}
                className={`toggle-switch relative w-12 h-6 rounded-full transition ${
                  showAvatar ? 'bg-green-500' : ''
                }`}
                style={{ 
                  backgroundColor: showAvatar ? 'var(--success)' : 'var(--border)',
                  opacity: theme !== 'avatar' ? 0.5 : 1
                }}>
                <div className={`toggle-thumb absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                  showAvatar ? 'translate-x-6' : 'translate-x-0'
                }`} />
              </button>
            </label>
            <p className="text-xs opacity-60 mt-1">
              {theme !== 'avatar' ? 'Only available in Avatar theme' : 'Display visual avatar'}
            </p>
          </div>
          
          {/* Info */}
          <div className="info-box p-3 rounded-lg text-xs"
               style={{ backgroundColor: 'var(--bg-secondary)', border: `1px solid var(--border)` }}>
            <p><strong>Current Theme:</strong> {theme}</p>
            <p className="mt-1 opacity-70">
              Switch themes anytime for different visual experiences. Settings are saved automatically.
            </p>
          </div>
        </div>
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="w-full mt-6 py-3 rounded-lg font-semibold transition hover:opacity-90"
          style={{ backgroundColor: 'var(--accent-primary)', color: '#ffffff' }}>
          Done
        </button>
      </div>
    </div>
  )
}

