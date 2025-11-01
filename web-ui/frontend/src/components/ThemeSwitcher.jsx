import { Monitor, Terminal, Sparkles } from 'lucide-react'

export default function ThemeSwitcher({ currentTheme, onThemeChange }) {
  const themes = [
    { id: 'professional', name: 'Pro', icon: Monitor },
    { id: 'terminal', name: 'Terminal', icon: Terminal },
    { id: 'avatar', name: 'Avatar', icon: Sparkles }
  ]
  
  return (
    <div className="theme-switcher flex gap-2 p-1.5 rounded-lg"
         style={{ 
           backgroundColor: 'var(--bg-tertiary)',
           border: '1px solid var(--border-light)'
         }}>
      {themes.map(({ id, name, icon: Icon }) => (
        <button
          key={id}
          onClick={() => onThemeChange(id)}
          className="theme-btn px-3 py-2 transition flex items-center gap-2"
          style={{
            backgroundColor: currentTheme === id ? 'var(--accent-primary)' : 'transparent',
            color: currentTheme === id ? '#ffffff' : 'var(--text-secondary)',
            borderRadius: 'var(--radius-sm)',
            boxShadow: currentTheme === id ? '0 2px 6px var(--shadow-md)' : 'none'
          }}
          onMouseEnter={(e) => {
            if (currentTheme !== id) {
              e.currentTarget.style.backgroundColor = 'var(--bg-hover)'
              e.currentTarget.style.color = 'var(--text-primary)'
            } else {
              e.currentTarget.style.backgroundColor = 'var(--accent-hover)'
            }
          }}
          onMouseLeave={(e) => {
            if (currentTheme !== id) {
              e.currentTarget.style.backgroundColor = 'transparent'
              e.currentTarget.style.color = 'var(--text-secondary)'
            } else {
              e.currentTarget.style.backgroundColor = 'var(--accent-primary)'
            }
          }}
          title={`${name} Theme`}>
          <Icon size={16} />
          <span className="text-sm font-medium">{name}</span>
        </button>
      ))}
    </div>
  )
}

