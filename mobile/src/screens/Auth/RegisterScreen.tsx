/**
 * Register screen for mobile
 */
import React, { useState } from 'react'
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native'
import { useNavigation } from '@react-navigation/native'
import GradientBackground from '../../components/ui/GradientBackground'
import GlassView from '../../components/ui/GlassView'
import { authService } from '../../services/auth'
import { colors } from '../../utils/liquidGlass'

export default function RegisterScreen() {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const navigation = useNavigation()
  
  const handleRegister = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all required fields')
      return
    }
    
    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match')
      return
    }
    
    if (password.length < 8) {
      Alert.alert('Error', 'Password must be at least 8 characters')
      return
    }
    
    setIsLoading(true)
    const result = await authService.register(email, password, username || undefined)
    setIsLoading(false)
    
    if (result.success) {
      navigation.navigate('Chat' as never)
    } else {
      Alert.alert('Registration Failed', result.error || 'Please try again')
    }
  }
  
  return (
    <GradientBackground>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.content}>
            <Text style={styles.title}>Create Account</Text>
            <Text style={styles.subtitle}>Sign up for JarvisX V2</Text>
            
            <GlassView variant="card" style={styles.form}>
              <TextInput
                style={styles.input}
                placeholder="Email"
                placeholderTextColor={colors.white50}
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />
              
              <TextInput
                style={styles.input}
                placeholder="Username (optional)"
                placeholderTextColor={colors.white50}
                value={username}
                onChangeText={setUsername}
                autoCapitalize="none"
              />
              
              <TextInput
                style={styles.input}
                placeholder="Password"
                placeholderTextColor={colors.white50}
                value={password}
                onChangeText={setPassword}
                secureTextEntry
              />
              
              <TextInput
                style={styles.input}
                placeholder="Confirm Password"
                placeholderTextColor={colors.white50}
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                secureTextEntry
              />
              
              <TouchableOpacity
                onPress={handleRegister}
                disabled={isLoading}
                style={[styles.button, isLoading && styles.buttonDisabled]}
              >
                <Text style={styles.buttonText}>
                  {isLoading ? 'Creating account...' : 'Sign Up'}
                </Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                onPress={() => navigation.navigate('Login' as never)}
                style={styles.linkButton}
              >
                <Text style={styles.linkText}>
                  Already have an account? Login
                </Text>
              </TouchableOpacity>
            </GlassView>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </GradientBackground>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  content: {
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    color: colors.white,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: colors.white80,
    textAlign: 'center',
    marginBottom: 32,
  },
  form: {
    padding: 24,
  },
  input: {
    backgroundColor: colors.glassLight,
    borderRadius: 12,
    padding: 16,
    color: colors.white,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: colors.glassMedium,
  },
  button: {
    backgroundColor: colors.primaryAqua,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: colors.white,
    fontSize: 16,
    fontWeight: '600',
  },
  linkButton: {
    marginTop: 24,
    alignItems: 'center',
  },
  linkText: {
    color: colors.primaryAqua,
    fontSize: 14,
  },
})

