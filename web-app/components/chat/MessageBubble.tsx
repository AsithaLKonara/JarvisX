'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface MessageBubbleProps {
  message: string
  role: 'user' | 'assistant'
  timestamp?: string
}

export default function MessageBubble({ message, role, timestamp }: MessageBubbleProps) {
  const isUser = role === 'user'
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-[80%] glass-panel p-4 ${
          isUser
            ? 'bg-primary-blue/20 border-primary-blue/30'
            : 'bg-white/5 border-white/10'
        }`}
      >
        <p className="text-white/90 text-sm leading-relaxed font-albert-sans">
          {message}
        </p>
        {timestamp && (
          <p className="text-white/50 text-xs mt-2">
            {new Date(timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>
    </motion.div>
  )
}

