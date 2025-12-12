/**
 * Compact message bubble for Siri-style interface
 */
import React from 'react'
import { View, Text, StyleSheet } from 'react-native'

interface CompactMessageBubbleProps {
  message: string
  role: 'user' | 'assistant'
  timestamp?: string
}

export default function CompactMessageBubble({
  message,
  role,
  timestamp,
}: CompactMessageBubbleProps) {
  const isUser = role === 'user'

  return (
    <View
      style={[
        styles.container,
        isUser ? styles.userBubble : styles.assistantBubble,
      ]}
    >
      <Text
        style={[
          styles.text,
          isUser ? styles.userText : styles.assistantText,
        ]}
      >
        {message}
      </Text>
      {timestamp && (
        <Text style={[styles.timestamp, isUser ? styles.userTimestamp : styles.assistantTimestamp]}>
          {timestamp}
        </Text>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    maxWidth: '85%',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 18,
    marginVertical: 4,
    alignSelf: 'flex-start',
  },
  userBubble: {
    backgroundColor: '#007AFF',
    alignSelf: 'flex-end',
  },
  assistantBubble: {
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  text: {
    fontSize: 15,
    lineHeight: 20,
  },
  userText: {
    color: '#ffffff',
  },
  assistantText: {
    color: '#ffffff',
  },
  timestamp: {
    fontSize: 11,
    marginTop: 4,
    opacity: 0.7,
  },
  userTimestamp: {
    color: '#ffffff',
  },
  assistantTimestamp: {
    color: '#ffffff',
  },
})

