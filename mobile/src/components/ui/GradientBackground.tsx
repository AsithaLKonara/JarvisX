/**
 * Gradient background component
 */
import React from 'react'
import { LinearGradient } from 'expo-linear-gradient'
import { colors } from '../../utils/liquidGlass'

interface GradientBackgroundProps {
  children: React.ReactNode
}

export default function GradientBackground({ children }: GradientBackgroundProps) {
  return (
    <LinearGradient
      colors={[colors.primaryBlue, colors.primaryAqua, colors.primaryPurple]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={{ flex: 1 }}
    >
      {children}
    </LinearGradient>
  )
}

