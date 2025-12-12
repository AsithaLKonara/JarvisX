'use client'

import React, { useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'
import GlassContainer from '../ui/GlassContainer'
import GradientBlob from '../ui/GradientBlob'
import { useChat } from '@/hooks/useChat'
import { Message } from '@/lib/api/chat'

export default function ChatContainer() {
  const { messages, isLoading, sendMessage } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages])
  
  const handleSendMessage = async (content: string) => {
    try {
      await sendMessage(content)
    } catch (error) {
      console.error('Error sending message:', error)
    }
  }
  
  return (
    <GlassContainer variant="panel" className="flex flex-col h-[585px] w-[267px] md:w-full md:max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <div>
          <h2 className="text-lg font-alata text-white/80">Hi, User</h2>
          <p className="text-xl font-alata text-white">Say something</p>
        </div>
        <button className="glass-button w-8 h-8 flex items-center justify-center">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <line x1="10" y1="4" x2="10" y2="16" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
            <line x1="4" y1="10" x2="16" y2="10" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
      </div>
      
      {/* Gradient Blob Avatar */}
      <div className="flex justify-center py-6">
        <GradientBlob size={175} />
      </div>
      
      {/* Description */}
      <div className="px-4 pb-4">
        <p className="text-sm text-white/80 font-albert-sans leading-relaxed">
          JarvisX V2 is an ultra-optimized, intelligent AI assistant powered by a custom-trained 
          Mistral 7B model with 137,300 domain-specific examples. It features multi-modal operation.
        </p>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-white/50 text-sm py-8">
            Start a conversation with JarvisX
          </div>
        )}
        {messages.map((message: Message) => (
          <MessageBubble
            key={message.id}
            message={message.content}
            role={message.role}
            timestamp={message.created_at}
          />
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="glass-panel p-4 bg-white/5">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      <div className="p-4 border-t border-white/10">
        <ChatInput onSend={handleSendMessage} />
      </div>
    </GlassContainer>
  )
}

