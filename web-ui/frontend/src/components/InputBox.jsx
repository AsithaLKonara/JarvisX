import { useState } from 'react'
import { Send, Mic, MicOff } from 'lucide-react'

export default function InputBox({ onSend, ttsEnabled, onTtsToggle, disabled }) {
  const [input, setInput] = useState('')
  
  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !disabled) {
      onSend(input)
      setInput('')
    }
  }
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }
  
  return (
    <form onSubmit={handleSubmit} className="input-box border-t px-6 py-4"
          style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-secondary)' }}>
      <div className="flex items-end gap-3">
        
        {/* TTS Toggle */}
        <button
          type="button"
          onClick={onTtsToggle}
          className="p-3 rounded-lg transition"
          style={{ 
            backgroundColor: ttsEnabled ? 'var(--success)' : 'var(--bg-tertiary)',
            color: ttsEnabled ? '#ffffff' : 'var(--text-secondary)'
          }}
          onMouseEnter={(e) => {
            if (!ttsEnabled) e.currentTarget.style.backgroundColor = 'var(--bg-hover)'
          }}
          onMouseLeave={(e) => {
            if (!ttsEnabled) e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)'
          }}
          title={ttsEnabled ? 'Voice output ON' : 'Voice output OFF'}>
          {ttsEnabled ? <Mic size={20} /> : <MicOff size={20} />}
        </button>
        
        {/* Text Input */}
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? 'Connecting...' : 'Type your message... (Enter to send, Shift+Enter for new line)'}
          disabled={disabled}
          className="flex-1 px-4 py-3 rounded-lg resize-none outline-none transition"
          style={{
            backgroundColor: 'var(--bg-primary)',
            color: 'var(--text-primary)',
            border: '2px solid var(--border)',
            fontFamily: 'var(--font-main)',
            minHeight: '56px',
            maxHeight: '200px'
          }}
          rows={1}
          onInput={(e) => {
            e.target.style.height = 'auto'
            e.target.style.height = e.target.scrollHeight + 'px'
          }}
        />
        
        {/* Send Button */}
        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className="p-3 rounded-lg transition"
          style={{
            backgroundColor: (!input.trim() || disabled) ? 'var(--bg-tertiary)' : 'var(--accent-primary)',
            color: '#ffffff',
            opacity: (!input.trim() || disabled) ? 0.5 : 1,
            cursor: (!input.trim() || disabled) ? 'not-allowed' : 'pointer',
            boxShadow: (!input.trim() || disabled) ? 'none' : '0 4px 12px var(--shadow-md)'
          }}
          onMouseEnter={(e) => {
            if (input.trim() && !disabled) {
              e.currentTarget.style.backgroundColor = 'var(--accent-hover)'
              e.currentTarget.style.transform = 'translateY(-2px)'
            }
          }}
          onMouseLeave={(e) => {
            if (input.trim() && !disabled) {
              e.currentTarget.style.backgroundColor = 'var(--accent-primary)'
              e.currentTarget.style.transform = 'translateY(0)'
            }
          }}>
          <Send size={20} />
        </button>
      </div>
      
      {/* Help text */}
      <div className="mt-2 text-xs opacity-50">
        <span>Press Enter to send, Shift+Enter for new line</span>
      </div>
    </form>
  )
}

