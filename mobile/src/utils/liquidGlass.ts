/**
 * Liquid glass styling utilities for React Native
 */
import { StyleSheet, ViewStyle, TextStyle } from 'react-native'
import { LinearGradient } from 'expo-linear-gradient'

export const liquidGlassStyles = StyleSheet.create({
  glassPanel: {
    backgroundColor: 'rgba(0, 0, 0, 0.001)',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    // Note: backdrop-filter not available in React Native
    // Use BlurView component instead
  },
  glassButton: {
    backgroundColor: 'rgba(0, 0, 0, 0.001)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    padding: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  gradientBackground: {
    flex: 1,
  },
} as const)

export const colors = {
  primaryBlue: '#000000',
  primaryAqua: '#000000',
  primaryPurple: '#A855F7',
  background: '#000000',
  glassLight: 'rgba(255, 255, 255, 0.1)',
  glassMedium: 'rgba(255, 255, 255, 0.15)',
  glassDark: 'rgba(255, 255, 255, 0.05)',
  white: '#FFFFFF',
  white80: 'rgba(255, 255, 255, 0.8)',
  white50: 'rgba(255, 255, 255, 0.5)',
}

export const createGradientBackground = () => {
  return (
    <LinearGradient
      colors={[colors.primaryBlue, colors.primaryAqua, colors.primaryPurple]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={liquidGlassStyles.gradientBackground}
    />
  )
}

