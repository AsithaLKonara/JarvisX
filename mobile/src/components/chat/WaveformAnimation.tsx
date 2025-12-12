/**
 * Waveform animation component for voice recording
 */
import React, { useEffect, useRef } from 'react'
import { View, StyleSheet, Animated } from 'react-native'

interface WaveformAnimationProps {
  isActive: boolean
  barCount?: number
  barColor?: string
  barWidth?: number
}

export default function WaveformAnimation({
  isActive,
  barCount = 5,
  barColor = '#ffffff',
  barWidth = 4,
}: WaveformAnimationProps) {
  const animations = useRef(
    Array.from({ length: barCount }, () => new Animated.Value(0.3))
  ).current

  useEffect(() => {
    if (isActive) {
      const anims = animations.map((anim, index) => {
        return Animated.loop(
          Animated.sequence([
            Animated.timing(anim, {
              toValue: 1,
              duration: 300 + index * 100,
              useNativeDriver: true,
            }),
            Animated.timing(anim, {
              toValue: 0.3,
              duration: 300 + index * 100,
              useNativeDriver: true,
            }),
          ])
        )
      })

      Animated.parallel(anims).start()
    } else {
      animations.forEach((anim) => {
        anim.setValue(0.3)
      })
    }
  }, [isActive, animations])

  return (
    <View style={styles.container}>
      {animations.map((anim, index) => (
        <Animated.View
          key={index}
          style={[
            styles.bar,
            {
              width: barWidth,
              height: anim.interpolate({
                inputRange: [0.3, 1],
                outputRange: [8, 32],
              }),
              backgroundColor: barColor,
              marginHorizontal: barWidth / 2,
              opacity: anim,
            },
          ]}
        />
      ))}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 40,
  },
  bar: {
    borderRadius: 2,
  },
})

