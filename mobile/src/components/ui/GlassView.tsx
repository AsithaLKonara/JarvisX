/**
 * Glass morphism container component for React Native
 */
import React from 'react'
import { View, ViewStyle, StyleSheet } from 'react-native'
import { BlurView } from '@react-native-community/blur'
import { liquidGlassStyles } from '../../utils/liquidGlass'

interface GlassViewProps {
  children: React.ReactNode
  style?: ViewStyle
  variant?: 'panel' | 'button' | 'card'
  intensity?: number
}

export default function GlassView({
  children,
  style,
  variant = 'panel',
  intensity = 20,
}: GlassViewProps) {
  const baseStyle = variant === 'button' 
    ? liquidGlassStyles.glassButton 
    : liquidGlassStyles.glassPanel
  
  return (
    <BlurView
      style={[baseStyle, style]}
      blurType="dark"
      blurAmount={intensity}
      reducedTransparencyFallbackColor="rgba(0, 0, 0, 0.5)"
    >
      {children}
    </BlurView>
  )
}

