'use client'

import React, { useRef, useEffect, useState } from 'react'
import { useChat } from '@/hooks/useChat'
import { Message, Conversation } from '@/lib/api/chat'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'
import Sidebar from './Sidebar'
import { useAuth } from '@/hooks/useAuth'

export default function ChatContainer() {
  const { 
    messages, 
    conversations, 
    currentConversationId,
    isLoading, 
    error,
    sendMessage,
    loadConversations,
    loadMessages,
    createConversation,
    updateConversation,
    deleteConversation,
    updateMessage,
    deleteMessage,
    setCurrentConversationId,
  } = useChat()
  
  const { user } = useAuth()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load conversations on mount
  useEffect(() => {
    loadConversations().catch(console.error)
  }, [loadConversations])

  // Load messages when conversation is selected
  useEffect(() => {
    if (currentConversationId) {
      loadMessages(currentConversationId).catch(console.error)
    } else {
      // Clear messages when no conversation is selected
      // Note: We might want to keep useChat's setMessages, but for now we'll rely on the hook
    }
  }, [currentConversationId, loadMessages])

  const handleSendMessage = async (content: string) => {
    try {
      await sendMessage(content)
      // Refresh conversations to get updated titles
      if (!currentConversationId) {
        await loadConversations()
      }
    } catch (error) {
      console.error('Error sending message:', error)
    }
  }

  const handleNewChat = async () => {
    try {
      await createConversation()
    } catch (error) {
      console.error('Error creating conversation:', error)
    }
  }

  const handleSelectConversation = async (id: string) => {
    setCurrentConversationId(id)
    // Messages will be loaded via useEffect
  }

  const handleDeleteConversation = async (id: string) => {
    try {
      await deleteConversation(id)
    } catch (error) {
      console.error('Error deleting conversation:', error)
    }
  }

  const handleRenameConversation = async (id: string, newTitle: string) => {
    try {
      await updateConversation(id, { title: newTitle })
    } catch (error) {
      console.error('Error renaming conversation:', error)
    }
  }

  const handleUpdateMessage = async (messageId: string, newContent: string) => {
    try {
      await updateMessage(messageId, newContent)
    } catch (error) {
      console.error('Error updating message:', error)
    }
  }

  const handleDeleteMessage = async (messageId: string) => {
    try {
      await deleteMessage(messageId)
    } catch (error) {
      console.error('Error deleting message:', error)
    }
  }

  const handleVoiceInput = async () => {
    // TODO: Implement voice recording and transcription
    // For now, show a placeholder alert
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      const recognition = new SpeechRecognition()
      recognition.continuous = false
      recognition.interimResults = false
      recognition.lang = 'en-US'

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        handleSendMessage(transcript)
      }

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        alert('Voice input not available. Please type your message.')
      }

      recognition.start()
    } else {
      alert('Voice input is not supported in this browser. Please type your message.')
    }
  }

  // Transform conversations for Sidebar component
  const sidebarConversations = conversations.map((conv) => ({
    id: conv.id,
    title: conv.title || 'New Conversation',
    lastMessage: undefined, // We could add this if the API provides it
    updatedAt: conv.updated_at,
  }))

  // Get current conversation title
  const currentConversation = conversations.find((c) => c.id === currentConversationId)
  const chatTitle = currentConversation?.title || (currentConversationId ? 'Chat' : 'New Chat')

  return (
    <div className="flex h-screen bg-white">
      {/* Sidebar */}
      <Sidebar
        conversations={sidebarConversations}
        currentConversationId={currentConversationId || undefined}
        onNewChat={handleNewChat}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={handleDeleteConversation}
        onRenameConversation={handleRenameConversation}
        userName={user?.name || user?.email?.split('@')[0]}
        userEmail={user?.email}
      />

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col bg-[#343541]">
        {/* Chat Header */}
        {currentConversationId && (
          <div className="border-b border-white/10 px-4 py-3">
            <h2 className="text-sm font-medium text-white/80">{chatTitle}</h2>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 && !isLoading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-2xl px-4">
                <h2 className="text-2xl font-semibold text-white mb-2">How can I help you today?</h2>
                <p className="text-white/70 mb-8">
                  Start a conversation by typing a message or use one of the example prompts:
                </p>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    'Explain quantum computing',
                    'Write a Python function',
                    'Help me debug code',
                    'Create a business plan',
                  ].map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => handleSendMessage(prompt)}
                      className="p-3 text-left rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-white text-sm transition-colors"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {messages.map((message: Message) => (
            <MessageBubble
              key={message.id}
              id={message.id}
              message={message.content}
              role={message.role}
              timestamp={message.created_at}
              onEdit={handleUpdateMessage}
              onDelete={handleDeleteMessage}
            />
          ))}
          
          {isLoading && (
            <div className="flex justify-start px-4 py-2">
              <div className="flex space-x-2 p-2 rounded-md bg-white/5">
                <div className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="px-4 py-2 bg-red-500/10 border-t border-red-500/20">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-white/10 p-4">
          <ChatInput 
            onSend={handleSendMessage} 
            onVoiceInput={handleVoiceInput}
          />
        </div>
      </main>
    </div>
  )
}
