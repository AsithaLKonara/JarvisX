/**
 * Chat hook
 */
import { useState, useCallback } from 'react'
import { chatApi, Message, Conversation } from '@/lib/api/chat'

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await chatApi.sendMessage(content, currentConversationId || undefined)
      
      // Add messages to state
      const userMessage: Message = {
        id: Date.now().toString(),
        conversation_id: response.conversation.id,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      }
      
      setMessages((prev) => [...prev, userMessage, response.message])
      setCurrentConversationId(response.conversation.id)
      
      return response
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to send message'
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [currentConversationId])
  
  const loadConversations = useCallback(async (search?: string) => {
    try {
      const data = await chatApi.getConversations(50, 0, search)
      setConversations(data)
      return data
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load conversations')
      throw err
    }
  }, [])
  
  const loadMessages = useCallback(async (conversationId: string) => {
    try {
      const data = await chatApi.getMessages(conversationId)
      setMessages(data)
      setCurrentConversationId(conversationId)
      return data
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load messages')
      throw err
    }
  }, [])
  
  const deleteConversation = useCallback(async (conversationId: string) => {
    try {
      await chatApi.deleteConversation(conversationId)
      setConversations((prev) => prev.filter((c) => c.id !== conversationId))
      if (currentConversationId === conversationId) {
        setCurrentConversationId(null)
        setMessages([])
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete conversation')
      throw err
    }
  }, [currentConversationId])
  
  return {
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
    setMessages,
    setCurrentConversationId,
  }
}

