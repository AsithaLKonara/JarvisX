const modes = [
  { id: 'engineer', name: 'Engineer', icon: '🔧', desc: 'Software engineering' },
  { id: 'system', name: 'System', icon: '📊', desc: 'PC monitoring' },
  { id: 'designer', name: 'Designer', icon: '🎨', desc: 'Design workflows' },
  { id: 'editor', name: 'Editor', icon: '🎬', desc: 'Video editing' },
  { id: 'business', name: 'Business', icon: '💼', desc: 'Financial management' },
  { id: 'casual', name: 'Casual', icon: '💬', desc: 'Natural conversations' },
  { id: 'career', name: 'Career', icon: '👔', desc: '169 job roles' }
]

export default function ModeSelector({ currentMode, onModeChange }) {
  return (
    <div className="mode-selector p-4">
      <h3 className="text-sm font-semibold mb-3 opacity-60">OPERATIONAL MODES</h3>
      
      <div className="space-y-1">
        {modes.map((mode) => (
          <button
            key={mode.id}
            onClick={() => onModeChange(mode.id)}
            className={`mode-button w-full text-left px-3 py-2.5 rounded-lg transition flex items-center gap-3
                       ${currentMode === mode.id ? 'active' : ''}`}
            style={{
              backgroundColor: currentMode === mode.id ? 'var(--accent)' : 'transparent',
              color: currentMode === mode.id ? '#ffffff' : 'var(--text-primary)',
              opacity: currentMode === mode.id ? 1 : 0.7
            }}
            onMouseEnter={(e) => {
              if (currentMode !== mode.id) {
                e.target.style.backgroundColor = 'var(--border)'
              }
            }}
            onMouseLeave={(e) => {
              if (currentMode !== mode.id) {
                e.target.style.backgroundColor = 'transparent'
              }
            }}>
            
            <span className="text-xl">{mode.icon}</span>
            <div className="flex-1">
              <div className="font-medium">{mode.name}</div>
              <div className="text-xs opacity-70">{mode.desc}</div>
            </div>
            
            {currentMode === mode.id && (
              <span className="status-dot w-2 h-2 rounded-full bg-white"></span>
            )}
          </button>
        ))}
      </div>
    </div>
  )
}

