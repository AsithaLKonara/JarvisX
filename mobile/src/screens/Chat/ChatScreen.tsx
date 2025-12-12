/**
 * Chat screen for mobile
 */
import React from 'react'
import { View, StyleSheet } from 'react-native'
import GradientBackground from '../../components/ui/GradientBackground'
import ChatContainer from '../../components/chat/ChatContainer'

export default function ChatScreen() {
  return (
    <GradientBackground>
      <View style={styles.container}>
        <ChatContainer />
      </View>
    </GradientBackground>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
})

