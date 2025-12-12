/**
 * Chat API functions for mobile
 */
import apiClient from './api'

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface Conversation {
  id: string
  user_id: string
  title: string | null
  created_at: string
  updated_at: string
  message_count: number
}

export interface ChatResponse {
  message: Message
  conversation: Conversation
}

export const chatApi = {
  sendMessage: async (content: string, conversationId?: string): Promise<ChatResponse> => {
    const response = await apiClient.post('/chat/messages', {
      content,
      conversation_id: conversationId || null,
    })
    return response.data
  },
  
  getConversations: async (limit = 50, offset = 0): Promise<Conversation[]> => {
    const response = await apiClient.get('/chat/conversations', {
      params: { limit, offset },
    })
    return response.data
  },
  
  getMessages: async (
    conversationId: string,
    limit = 100,
    offset = 0
  ): Promise<Message[]> => {
    const response = await apiClient.get(
      `/chat/conversations/${conversationId}/messages`,
      { params: { limit, offset } }
    )
    return response.data
  },
  
  deleteConversation: async (conversationId: string): Promise<void> => {
    await apiClient.delete(`/chat/conversations/${conversationId}`)
  },
}

