import { Monitor, Terminal, Sparkles } from 'lucide-react'

export default function ThemeSwitcher({ currentTheme, onThemeChange }) {
  const themes = [
    { id: 'professional', name: 'Pro', icon: Monitor },
    { id: 'terminal', name: 'Terminal', icon: Terminal },
    { id: 'avatar', name: 'Avatar', icon: Sparkles }
  ]
  
  return (
    <div className="theme-switcher flex gap-2 p-1 rounded-lg"
         style={{ backgroundColor: 'var(--bg-secondary)' }}>
      {themes.map(({ id, name, icon: Icon }) => (
        <button
          key={id}
          onClick={() => onThemeChange(id)}
          className="theme-btn px-3 py-1.5 rounded transition flex items-center gap-2"
          style={{
            backgroundColor: currentTheme === id ? 'var(--accent)' : 'transparent',
            color: currentTheme === id ? '#ffffff' : 'var(--text-secondary)'
          }}
          title={`${name} Theme`}>
          <Icon size={16} />
          <span className="text-sm font-medium">{name}</span>
        </button>
      ))}
    </div>
  )
}

