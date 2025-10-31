import { useState, useEffect } from 'react'
import ChatContainer from './components/ChatContainer'
import ModeSelector from './components/ModeSelector'
import SystemStatus from './components/SystemStatus'
import SettingsPanel from './components/SettingsPanel'
import Avatar from './components/Avatar'
import ThemeSwitcher from './components/ThemeSwitcher'
import { Settings } from 'lucide-react'
import './themes/theme-professional.css'
import './themes/theme-terminal.css'
import './themes/theme-avatar.css'

function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('jarvis-theme') || 'professional'
  })
  
  const [currentMode, setCurrentMode] = useState('casual')
  const [showSettings, setShowSettings] = useState(false)
  const [ttsEnabled, setTtsEnabled] = useState(false)
  const [showAvatar, setShowAvatar] = useState(true)
  
  // Apply theme to document root
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('jarvis-theme', theme)
  }, [theme])
  
  // Check if avatar should be visible
  const isAvatarVisible = theme === 'avatar' && showAvatar
  
  return (
    <div className="app-container h-screen flex flex-col overflow-hidden" 
         style={{
           backgroundColor: 'var(--bg-primary)',
           color: 'var(--text-primary)'
         }}>
      
      {/* Header */}
      <header className="header flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: 'var(--border)' }}>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">
            <span style={{ color: 'var(--accent)' }}>🤖 JARVIS X</span> V2
          </h1>
          <span className="text-sm opacity-60">
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
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 rounded hover:bg-opacity-10 hover:bg-white transition"
            style={{ color: 'var(--accent)' }}>
            <Settings size={24} />
          </button>
        </div>
      </header>
      
      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Sidebar - Mode Selector & System Status */}
        <aside className="sidebar w-64 border-r flex flex-col"
               style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-secondary)' }}>
          <ModeSelector 
            currentMode={currentMode}
            onModeChange={setCurrentMode}
          />
          <div className="mt-auto">
            <SystemStatus />
          </div>
        </aside>
        
        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col overflow-hidden relative">
          {/* Avatar (only visible in avatar theme) */}
          {isAvatarVisible && (
            <div className="avatar-container absolute top-4 right-4 z-10">
              <Avatar ttsActive={ttsEnabled} currentEmotion="neutral" />
            </div>
          )}
          
          {/* Chat */}
          <ChatContainer 
            currentMode={currentMode}
            ttsEnabled={ttsEnabled}
            onTtsToggle={setTtsEnabled}
          />
        </main>
      </div>
      
      {/* Settings Panel (Modal) */}
      {showSettings && (
        <SettingsPanel 
          theme={theme}
          onThemeChange={setTheme}
          ttsEnabled={ttsEnabled}
          onTtsToggle={setTtsEnabled}
          showAvatar={showAvatar}
          onAvatarToggle={setShowAvatar}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  )
}

export default App

