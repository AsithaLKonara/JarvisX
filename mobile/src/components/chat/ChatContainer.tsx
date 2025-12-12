/**
 * Chat container component for mobile
 */
import React, { useState, useRef, useEffect } from 'react'
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native'
import GlassView from '../ui/GlassView'
import { colors, liquidGlassStyles } from '../../utils/liquidGlass'
import { chatApi, Message } from '../../services/chat'
import MicrophoneButton from './MicrophoneButton'

export default function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const scrollViewRef = useRef<ScrollView>(null)
  
  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true })
  }, [messages])
  
  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return
    
    const userMessage: Message = {
      id: Date.now().toString(),
      conversation_id: '',
      role: 'user',
      content: inputText,
      created_at: new Date().toISOString(),
    }
    
    setMessages((prev) => [...prev, userMessage])
    setInputText('')
    setIsLoading(true)
    
    try {
      const response = await chatApi.sendMessage(inputText)
      setMessages((prev) => [...prev, response.message])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        conversation_id: '',
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={100}
    >
      <ScrollView
        ref={scrollViewRef}
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}
      >
        {messages.length === 0 && (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>Start a conversation with JarvisX</Text>
          </View>
        )}
        {messages.map((message) => (
          <View
            key={message.id}
            style={[
              styles.messageBubble,
              message.role === 'user' ? styles.userMessage : styles.assistantMessage,
            ]}
          >
            <Text style={styles.messageText}>{message.content}</Text>
          </View>
        ))}
        {isLoading && (
          <View style={[styles.messageBubble, styles.assistantMessage]}>
            <Text style={styles.messageText}>Thinking...</Text>
          </View>
        )}
      </ScrollView>
      
      <View style={styles.inputContainer}>
        <GlassView variant="panel" style={styles.inputWrapper}>
          <TextInput
            style={styles.input}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type your message..."
            placeholderTextColor={colors.white50}
            multiline
            onSubmitEditing={sendMessage}
          />
        </GlassView>
        <MicrophoneButton onRecordStart={() => {}} onRecordStop={() => {}} />
        <TouchableOpacity onPress={sendMessage} style={styles.sendButton}>
          <GlassView variant="button">
            <Text style={styles.sendButtonText}>Send</Text>
          </GlassView>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    color: colors.white50,
    fontSize: 14,
  },
  messageBubble: {
    padding: 12,
    borderRadius: 12,
    marginBottom: 8,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: colors.primaryBlue + '40',
  },
  assistantMessage: {
    alignSelf: 'flex-start',
    backgroundColor: colors.glassLight,
  },
  messageText: {
    color: colors.white,
    fontSize: 14,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    gap: 8,
  },
  inputWrapper: {
    flex: 1,
    padding: 12,
  },
  input: {
    color: colors.white,
    fontSize: 14,
  },
  sendButton: {
    padding: 8,
  },
  sendButtonText: {
    color: colors.white,
    fontSize: 14,
    fontWeight: '600',
  },
})

