/**
 * Microphone button component for mobile
 */
import React, { useState } from 'react'
import { TouchableOpacity, StyleSheet, Animated, Text } from 'react-native'
import GlassView from '../ui/GlassView'
import { colors } from '../../utils/liquidGlass'

interface MicrophoneButtonProps {
  onRecordStart?: () => void
  onRecordStop?: () => void
  size?: number
}

export default function MicrophoneButton({
  onRecordStart,
  onRecordStop,
  size = 54,
}: MicrophoneButtonProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [scaleAnim] = useState(new Animated.Value(1))
  const [pulseAnim] = useState(new Animated.Value(1))
  
  const handlePress = () => {
    if (isRecording) {
      setIsRecording(false)
      onRecordStop?.()
      Animated.parallel([
        Animated.spring(scaleAnim, { toValue: 1, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 200, useNativeDriver: true }),
      ]).start()
    } else {
      setIsRecording(true)
      onRecordStart?.()
      Animated.parallel([
        Animated.spring(scaleAnim, { toValue: 0.9, useNativeDriver: true }),
        Animated.loop(
          Animated.sequence([
            Animated.timing(pulseAnim, { toValue: 1.2, duration: 500, useNativeDriver: true }),
            Animated.timing(pulseAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
          ])
        ),
      ]).start()
    }
  }
  
  return (
    <TouchableOpacity onPress={handlePress} activeOpacity={0.8}>
      <Animated.View
        style={[
          styles.container,
          { width: size, height: size, transform: [{ scale: scaleAnim }] },
        ]}
      >
        <Animated.View
          style={[
            styles.pulseRing,
            {
              width: size * 1.5,
              height: size * 1.5,
              borderRadius: size * 0.75,
              opacity: isRecording ? 0.3 : 0,
              transform: [{ scale: pulseAnim }],
            },
          ]}
        />
        <GlassView variant="button" style={styles.button}>
          <Text style={styles.icon}>🎤</Text>
        </GlassView>
      </Animated.View>
    </TouchableOpacity>
  )
}

const styles = StyleSheet.create({
  container: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
  },
  pulseRing: {
    position: 'absolute',
    backgroundColor: colors.primaryAqua,
  },
  button: {
    width: '100%',
    height: '100%',
    borderRadius: 27,
  },
  icon: {
    fontSize: 24,
  },
})
