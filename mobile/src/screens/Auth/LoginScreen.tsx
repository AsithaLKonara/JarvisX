/**
 * Login screen for mobile
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

export default function LoginScreen() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const navigation = useNavigation()
  
  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields')
      return
    }
    
    setIsLoading(true)
    const result = await authService.login(email, password)
    setIsLoading(false)
    
    if (result.success) {
      navigation.navigate('Chat' as never)
    } else {
      Alert.alert('Login Failed', result.error || 'Please try again')
    }
  }
  
  const handleGoogleLogin = async () => {
    setIsLoading(true)
    const result = await authService.loginWithGoogle()
    setIsLoading(false)
    
    if (result.success) {
      navigation.navigate('Chat' as never)
    } else {
      Alert.alert('Login Failed', result.error || 'Please try again')
    }
  }
  
  const handleAppleLogin = async () => {
    setIsLoading(true)
    const result = await authService.loginWithApple()
    setIsLoading(false)
    
    if (result.success) {
      navigation.navigate('Chat' as never)
    } else {
      Alert.alert('Login Failed', result.error || 'Please try again')
    }
  }
  
  const handleFacebookLogin = async () => {
    setIsLoading(true)
    const result = await authService.loginWithFacebook()
    setIsLoading(false)
    
    if (result.success) {
      navigation.navigate('Chat' as never)
    } else {
      Alert.alert('Login Failed', result.error || 'Please try again')
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
            <Text style={styles.title}>JarvisX V2</Text>
            <Text style={styles.subtitle}>Login to continue</Text>
            
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
                placeholder="Password"
                placeholderTextColor={colors.white50}
                value={password}
                onChangeText={setPassword}
                secureTextEntry
              />
              
              <TouchableOpacity
                onPress={handleLogin}
                disabled={isLoading}
                style={[styles.button, isLoading && styles.buttonDisabled]}
              >
                <Text style={styles.buttonText}>
                  {isLoading ? 'Logging in...' : 'Login'}
                </Text>
              </TouchableOpacity>
              
              <View style={styles.divider}>
                <View style={styles.dividerLine} />
                <Text style={styles.dividerText}>Or</Text>
                <View style={styles.dividerLine} />
              </View>
              
              <View style={styles.oauthButtons}>
                <TouchableOpacity
                  onPress={handleGoogleLogin}
                  style={styles.oauthButton}
                >
                  <Text style={styles.oauthButtonText}>Google</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  onPress={handleAppleLogin}
                  style={styles.oauthButton}
                >
                  <Text style={styles.oauthButtonText}>Apple</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  onPress={handleFacebookLogin}
                  style={styles.oauthButton}
                >
                  <Text style={styles.oauthButtonText}>Facebook</Text>
                </TouchableOpacity>
              </View>
              
              <TouchableOpacity
                onPress={() => navigation.navigate('Signup' as never)}
                style={styles.linkButton}
              >
                <Text style={styles.linkText}>
                  Don't have an account? Sign up
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
    fontSize: 48,
    fontWeight: 'bold',
    color: colors.white,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
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
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 24,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: colors.glassMedium,
  },
  dividerText: {
    marginHorizontal: 16,
    color: colors.white50,
  },
  oauthButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  oauthButton: {
    flex: 1,
    backgroundColor: colors.glassLight,
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.glassMedium,
  },
  oauthButtonText: {
    color: colors.white,
    fontSize: 14,
    fontWeight: '500',
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

