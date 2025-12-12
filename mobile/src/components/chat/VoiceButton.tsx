/**
 * Large Siri-style voice button component
 */
import React, { useRef, useEffect } from 'react'
import {
  View,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Dimensions,
} from 'react-native'

const { width } = Dimensions.get('window')
const BUTTON_SIZE = width * 0.35 // Large button size similar to Siri

interface VoiceButtonProps {
  onPress?: () => void
  onPressIn?: () => void
  onPressOut?: () => void
  isActive?: boolean
  size?: number
}

export default function VoiceButton({
  onPress,
  onPressIn,
  onPressOut,
  isActive = false,
  size = BUTTON_SIZE,
}: VoiceButtonProps) {
  const pulseAnim = useRef(new Animated.Value(1)).current
  const scaleAnim = useRef(new Animated.Value(1)).current

  useEffect(() => {
    if (isActive) {
      // Pulse animation when active
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.2,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 800,
            useNativeDriver: true,
          }),
        ])
      ).start()

      // Scale animation
      Animated.spring(scaleAnim, {
        toValue: 1.1,
        useNativeDriver: true,
        tension: 50,
        friction: 7,
      }).start()
    } else {
      pulseAnim.setValue(1)
      Animated.spring(scaleAnim, {
        toValue: 1,
        useNativeDriver: true,
        tension: 50,
        friction: 7,
      }).start()
    }
  }, [isActive, pulseAnim, scaleAnim])

  return (
    <View style={styles.container}>
      {/* Outer pulse ring */}
      {isActive && (
        <Animated.View
          style={[
            styles.pulseRing,
            {
              width: size,
              height: size,
              borderRadius: size / 2,
              transform: [{ scale: pulseAnim }],
              opacity: pulseAnim.interpolate({
                inputRange: [1, 1.2],
                outputRange: [0.3, 0],
              }),
            },
          ]}
        />
      )}
      
      {/* Button */}
      <Animated.View
        style={[
          {
            transform: [{ scale: scaleAnim }],
          },
        ]}
      >
        <TouchableOpacity
          style={[
            styles.button,
            {
              width: size,
              height: size,
              borderRadius: size / 2,
              backgroundColor: isActive ? '#ff3b30' : '#ffffff',
            },
          ]}
          onPress={onPress}
          onPressIn={onPressIn}
          onPressOut={onPressOut}
          activeOpacity={0.8}
        >
          <View
            style={[
              styles.innerCircle,
              {
                width: size * 0.7,
                height: size * 0.7,
                borderRadius: (size * 0.7) / 2,
                backgroundColor: isActive ? '#ff3b30' : '#ffffff',
                borderWidth: isActive ? 0 : 2,
                borderColor: '#000000',
              },
            ]}
          >
            {/* Microphone icon */}
            <View style={styles.iconContainer}>
              {isActive ? (
                <View style={styles.stopIcon} />
              ) : (
                <View style={styles.micIcon}>
                  <View style={styles.micBody} />
                  <View style={styles.micStand} />
                </View>
              )}
            </View>
          </View>
        </TouchableOpacity>
      </Animated.View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  pulseRing: {
    position: 'absolute',
    backgroundColor: '#ff3b30',
  },
  button: {
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  innerCircle: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  micIcon: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  micBody: {
    width: 20,
    height: 30,
    borderRadius: 10,
    borderWidth: 3,
    borderColor: '#000000',
    backgroundColor: 'transparent',
  },
  micStand: {
    width: 4,
    height: 8,
    backgroundColor: '#000000',
    marginTop: -2,
    borderRadius: 2,
  },
  stopIcon: {
    width: 24,
    height: 24,
    borderRadius: 4,
    backgroundColor: '#ffffff',
  },
})

