import { useState, useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import InputBox from './InputBox'
import useWebSocket from '../hooks/useWebSocket'

export default function ChatContainer({ currentMode, ttsEnabled, onTtsToggle }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: `Hello! I'm Jarvis, your AI assistant. I'm currently in ${currentMode} mode. How can I help you today?`,
      timestamp: new Date().toISOString(),
      emotion: 'happy'
    }
  ])
  
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)
  
  // WebSocket connection
  const { sendMessage, lastMessage, connectionStatus } = useWebSocket()
  
  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages])
  
  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      const data = JSON.parse(lastMessage.data)
      
      if (data.type === 'message') {
        // Add AI response
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          role: 'assistant',
          content: data.content,
          timestamp: data.timestamp,
          emotion: data.emotion
        }])
        setIsTyping(false)
      } else if (data.type === 'typing') {
        setIsTyping(data.status)
      }
    }
  }, [lastMessage])
  
  // Send message handler
  const handleSendMessage = (text) => {
    if (!text.trim()) return
    
    // Add user message to UI
    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    }
    
    setMessages(prev => [...prev, userMessage])
    setIsTyping(true)
    
    // Send to backend via WebSocket
    sendMessage({
      type: 'chat',
      message: text,
      mode: currentMode
    })
  }
  
  return (
    <div className="chat-container flex flex-col h-full">
      {/* Connection Status */}
      <div className="px-4 py-2 text-xs opacity-60 border-b" 
           style={{ borderColor: 'var(--border)' }}>
        <span className={connectionStatus === 'connected' ? 'text-green-500' : 'text-red-500'}>
          {connectionStatus === 'connected' ? '🟢' : '🔴'} 
          {connectionStatus === 'connected' ? ' Connected' : ' Disconnected'}
        </span>
        {ttsEnabled && <span className="ml-4">🔊 Voice Output: ON</span>}
      </div>
      
      {/* Messages Area */}
      <div className="messages-area flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {isTyping && (
          <div className="flex items-center gap-2 px-4 py-2 opacity-60">
            <div className="typing-indicator flex gap-1">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
            <span className="text-sm">Jarvis is thinking...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      <InputBox 
        onSend={handleSendMessage}
        ttsEnabled={ttsEnabled}
        onTtsToggle={onTtsToggle}
        disabled={connectionStatus !== 'connected'}
      />
    </div>
  )
}

