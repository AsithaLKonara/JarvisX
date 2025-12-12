'use client'

import React, { useState, KeyboardEvent } from 'react'
import MicrophoneButton from '../ui/MicrophoneButton'

interface ChatInputProps {
  onSend: (message: string) => void
}

export default function ChatInput({ onSend }: ChatInputProps) {
  const [message, setMessage] = useState('')
  
  const handleSend = () => {
    if (message.trim()) {
      onSend(message)
      setMessage('')
    }
  }
  
  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }
  
  return (
    <div className="flex items-center gap-4">
      <button className="glass-button w-9 h-9 flex items-center justify-center">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path
            d="M13 3H7C4.79 3 3 4.79 3 7V13C3 15.21 4.79 17 7 17H13C15.21 17 17 15.21 17 13V7C17 4.79 15.21 3 13 3Z"
            stroke="white"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="10" cy="10" r="2" fill="white" />
        </svg>
      </button>
      
      <div className="flex-1 glass-panel px-4 py-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          className="w-full bg-transparent text-white placeholder-white/50 outline-none font-albert-sans"
        />
      </div>
      
      <MicrophoneButton
        size={54}
        onRecordStart={() => console.log('Recording started')}
        onRecordStop={() => console.log('Recording stopped')}
      />
      
      <button
        onClick={handleSend}
        className="glass-button w-9 h-9 flex items-center justify-center"
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <line x1="10" y1="4" x2="10" y2="16" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="4" y1="10" x2="16" y2="10" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </button>
    </div>
  )
}

