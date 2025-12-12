/**
 * Siri-style chat screen for mobile
 */
import React, { useState, useRef, useEffect } from 'react'
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Dimensions,
  KeyboardAvoidingView,
  Platform,
  StatusBar,
} from 'react-native'
import VoiceButton from '../../components/chat/VoiceButton'
import WaveformAnimation from '../../components/chat/WaveformAnimation'
import CompactMessageBubble from '../../components/chat/CompactMessageBubble'
import { chatApi, Message } from '../../services/chat'

const { width, height } = Dimensions.get('window')

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const scrollViewRef = useRef<ScrollView>(null)

  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true })
  }, [messages])

  const handleVoicePress = () => {
    if (isRecording) {
      handleStopRecording()
    } else {
      handleStartRecording()
    }
  }

  const handleStartRecording = () => {
    setIsRecording(true)
    // TODO: Start voice recording
  }

  const handleStopRecording = async () => {
    setIsRecording(false)
    setIsProcessing(true)
    
    // TODO: Process voice recording and convert to text
    // For now, simulate with a placeholder
    const transcript = 'Hello, how are you?'
    
    try {
      await sendMessage(transcript)
    } catch (error) {
      console.error('Error processing voice message:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  const sendMessage = async (content: string) => {
    if (!content.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      conversation_id: '',
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])

    try {
      const response = await chatApi.sendMessage(content)
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
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
    >
      <StatusBar barStyle="light-content" />
      <View style={styles.background} />

      {/* Messages Area */}
      <ScrollView
        ref={scrollViewRef}
        style={styles.messagesContainer}
        contentContainerStyle={[
          styles.messagesContent,
          messages.length === 0 && styles.emptyMessagesContent,
        ]}
        showsVerticalScrollIndicator={false}
      >
        {messages.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>Say something</Text>
            <Text style={styles.emptySubtitle}>Tap the microphone to start</Text>
          </View>
        ) : (
          messages.map((message) => (
            <CompactMessageBubble
              key={message.id}
              message={message.content}
              role={message.role}
              timestamp={new Date(message.created_at).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            />
          ))
        )}

        {isProcessing && (
          <View style={styles.processingContainer}>
            <Text style={styles.processingText}>Processing...</Text>
          </View>
        )}
      </ScrollView>

      {/* Voice Button Area */}
      <View style={styles.voiceButtonContainer}>
        {isRecording && (
          <View style={styles.waveformContainer}>
            <WaveformAnimation isActive={isRecording} />
            <Text style={styles.recordingText}>Listening...</Text>
          </View>
        )}
        <VoiceButton
          isActive={isRecording}
          onPress={handleVoicePress}
          onPressIn={handleStartRecording}
          onPressOut={handleStopRecording}
        />
      </View>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  background: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: '#000000',
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    paddingHorizontal: 16,
    paddingTop: 20,
    paddingBottom: 100,
  },
  emptyMessagesContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.6)',
  },
  voiceButtonContainer: {
    position: 'absolute',
    bottom: 40,
    left: 0,
    right: 0,
    alignItems: 'center',
    justifyContent: 'center',
  },
  waveformContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  recordingText: {
    color: '#ffffff',
    fontSize: 14,
    marginTop: 8,
    fontWeight: '500',
  },
  processingContainer: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  processingText: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: 14,
  },
})
