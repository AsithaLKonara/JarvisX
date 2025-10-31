export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const timestamp = new Date(message.timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
  
  return (
    <div className={`message-bubble flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[70%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div 
          className="message-content px-4 py-3 rounded-lg"
          style={{
            backgroundColor: isUser ? 'var(--accent)' : 'var(--bg-secondary)',
            color: isUser ? '#ffffff' : 'var(--text-primary)',
            borderRadius: 'var(--radius)',
            boxShadow: `0 2px 8px var(--shadow)`
          }}>
          
          {/* Message text */}
          <div className="message-text whitespace-pre-wrap break-words">
            {message.content}
          </div>
          
          {/* Metadata */}
          <div className="message-meta flex items-center gap-2 mt-2 text-xs opacity-60">
            <span>{timestamp}</span>
            {message.emotion && !isUser && (
              <span className="emotion-badge px-2 py-0.5 rounded"
                    style={{ backgroundColor: 'var(--border)' }}>
                {message.emotion === 'happy' && '😊'}
                {message.emotion === 'neutral' && '😐'}
                {message.emotion === 'thinking' && '🤔'}
                {message.emotion === 'excited' && '🎉'}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

