import { useState, useEffect } from 'react'
import { Settings } from 'lucide-react'

// Components
import ChatContainer from './components/ChatContainer'
import ModeSelector from './components/ModeSelector'
import SystemStatus from './components/SystemStatus'
import SettingsPanel from './components/SettingsPanel'
import Avatar from './components/Avatar'
import ThemeSwitcher from './components/ThemeSwitcher'

// Themes
import './themes/theme-professional.css'
import './themes/theme-terminal.css'
import './themes/theme-avatar.css'
import './themes/theme-avatar-sidebar.css'

function App() {
  // === STATE ===
  const [theme, setTheme] = useState(() => localStorage.getItem('jarvis-theme') || 'professional')
  const [currentMode, setCurrentMode] = useState('casual')
  const [showSettings, setShowSettings] = useState(false)
  const [ttsEnabled, setTtsEnabled] = useState(false)
  const [showAvatar, setShowAvatar] = useState(true)

  // === EFFECTS ===
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('jarvis-theme', theme)
  }, [theme])

  // === HANDLERS ===
  const toggleTts = () => setTtsEnabled((prev) => !prev)
  const toggleSettings = () => setShowSettings((prev) => !prev)
  const toggleAvatar = () => setShowAvatar((prev) => !prev)

  // === DERIVED ===
  const isAvatarVisible = theme === 'avatar' && showAvatar

  // === COMPONENT ===
  return (
    <div
      className="app-container h-screen flex flex-col"
      style={{
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-primary)',
      }}
    >
      {/* ============================================ */}
      {/* ROW 1: NAVBAR (Full Width) */}
      {/* ============================================ */}
      <header
        className="w-full flex items-center justify-between px-6 py-4 border-b"
        style={{
          borderColor: 'var(--border)',
          backgroundColor: 'var(--bg-secondary)',
          boxShadow: '0 2px 8px var(--shadow-sm)',
          zIndex: 50,
          flexShrink: 0,
        }}
      >
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">
            <span style={{ color: 'var(--accent-primary)' }}>🤖 JARVIS X</span>
            <span style={{ color: 'var(--text-secondary)' }}> V2</span>
          </h1>
          <span
            className="px-3 py-1 rounded-full text-sm font-medium"
            style={{
              backgroundColor: 'var(--bg-tertiary)',
              color: 'var(--accent-primary)',
            }}
          >
            {currentMode === 'engineer' && '🔧 Engineer'}
            {currentMode === 'system' && '📊 System Monitor'}
            {currentMode === 'designer' && '🎨 Designer'}
            {currentMode === 'editor' && '🎬 Editor'}
            {currentMode === 'business' && '💼 Business'}
            {currentMode === 'casual' && '💬 Casual'}
            {currentMode === 'career' && '👔 Career'}
          </span>
        </div>

        <div className="flex items-center gap-4">
          <ThemeSwitcher currentTheme={theme} onThemeChange={setTheme} />
          <button
            onClick={toggleSettings}
            className="p-2.5 rounded-lg transition"
            style={{
              color: 'var(--accent-primary)',
              backgroundColor: 'var(--bg-tertiary)',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-hover)')}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)')}
          >
            <Settings size={20} />
          </button>
        </div>
      </header>

      {/* ============================================ */}
      {/* ROW 2: THREE COLUMNS */}
      {/* ============================================ */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* COLUMN 1: LEFT SIDEBAR */}
        <aside
          className="w-64 border-r flex flex-col"
          style={{
            borderColor: 'var(--border)',
            backgroundColor: 'var(--bg-secondary)',
            zIndex: 10,
            flexShrink: 0,
          }}
        >
          <ModeSelector currentMode={currentMode} onModeChange={setCurrentMode} />
          <div className="mt-auto">
            <SystemStatus />
          </div>
        </aside>

        {/* COLUMN 2: CHAT AREA (CENTER) */}
        <main 
          className="flex-1 flex flex-col overflow-hidden" 
          style={{ 
            zIndex: 5,
            minWidth: 0, // Allows flex item to shrink below content size
          }}
        >
          <ChatContainer currentMode={currentMode} ttsEnabled={ttsEnabled} onTtsToggle={toggleTts} />
        </main>

        {/* COLUMN 3: RIGHT SIDEBAR */}
        {isAvatarVisible && (
          <aside
            className="w-80 border-l flex flex-col items-center p-6 overflow-y-auto"
            style={{
              borderColor: 'var(--border)',
              backgroundColor: 'var(--bg-secondary)',
              zIndex: 10,
              flexShrink: 0,
            }}
          >
            {/* Spacer to push content to bottom */}
            <div className="flex-1"></div>
            
            <div className="avatar-section flex-shrink-0 mb-6">
              <Avatar ttsActive={ttsEnabled} currentEmotion="neutral" />
            </div>

            <div className="avatar-info w-full space-y-4 flex-shrink-0" style={{ maxWidth: '100%' }}>
              {/* Header Info */}
              <div className="text-center">
                <h3 className="text-lg font-semibold mb-1" style={{ color: 'var(--accent-primary)' }}>
                  🤖 JARVIS
                </h3>
                <p className="text-sm opacity-60">{ttsEnabled ? '🎤 Voice Active' : '🔇 Silent Mode'}</p>
              </div>

              {/* Status Cards */}
              <div className="space-y-2">
                <StatusCard label="Status" value="Online & Ready" active />
                <StatusCard label="Current Mode" value={modeLabel(currentMode)} accent />
                <StatusCard
                  label="Voice Output"
                  value={ttsEnabled ? '✓ Enabled' : '✗ Disabled'}
                  active={ttsEnabled}
                />
              </div>

              {/* Quick Actions */}
              <div className="pt-4 border-t space-y-2" style={{ borderColor: 'var(--border)' }}>
                <div
                  className="text-xs font-semibold mb-2"
                  style={{ color: 'var(--text-tertiary)' }}
                >
                  QUICK ACTIONS
                </div>

                <button
                  onClick={toggleTts}
                  className="w-full px-4 py-2.5 rounded-lg text-sm font-medium transition"
                  style={{
                    backgroundColor: ttsEnabled ? 'var(--success)' : 'var(--accent-primary)',
                    color: '#fff',
                    boxShadow: '0 2px 8px var(--shadow-md)',
                  }}
                >
                  {ttsEnabled ? '🔇 Disable Voice' : '🎤 Enable Voice'}
                </button>

                <button
                  onClick={toggleSettings}
                  className="w-full px-4 py-2.5 rounded-lg text-sm font-medium transition border"
                  style={{
                    backgroundColor: 'var(--bg-tertiary)',
                    color: 'var(--text-primary)',
                    borderColor: 'var(--border)',
                  }}
                >
                  ⚙️ Settings
                </button>
              </div>
            </div>
          </aside>
        )}
      </div>

      {/* === SETTINGS PANEL === */}
      {showSettings && (
        <SettingsPanel
          theme={theme}
          onThemeChange={setTheme}
          ttsEnabled={ttsEnabled}
          onTtsToggle={toggleTts}
          showAvatar={showAvatar}
          onAvatarToggle={toggleAvatar}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  )
}

/* === HELPER COMPONENTS === */
function StatusCard({ label, value, active, accent }) {
  return (
    <div
      className="p-3 transition-all rounded-md"
      style={{
        backgroundColor: 'var(--bg-primary)',
        border: '1px solid var(--border)',
        boxShadow: '0 2px 4px var(--shadow-sm)',
      }}
    >
      <div className="text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>
        {label}
      </div>
      <div
        className="text-sm font-semibold flex items-center gap-2"
        style={{
          color: accent
            ? 'var(--accent-primary)'
            : active
            ? 'var(--success)'
            : 'var(--text-secondary)',
        }}
      >
        {active && (
          <span
            className="inline-block w-2 h-2 rounded-full animate-pulse"
            style={{ backgroundColor: 'var(--success)' }}
          ></span>
        )}
        {value}
      </div>
    </div>
  )
}

function modeLabel(mode) {
  const labels = {
    engineer: '🔧 Engineer',
    system: '📊 System Monitor',
    designer: '🎨 Designer',
    editor: '🎬 Editor',
    business: '💼 Business',
    casual: '💬 Casual',
    career: '👔 Career',
  }
  return labels[mode] || '💬 Casual'
}

export default App
