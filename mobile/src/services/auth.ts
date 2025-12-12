/**
 * Authentication service for mobile
 */
import apiClient from './api'
import AsyncStorage from '@react-native-async-storage/async-storage'
import { GoogleSignin } from '@react-native-google-signin/google-signin'
import { appleAuth } from '@invertase/react-native-apple-authentication'
import { LoginManager, AccessToken } from 'react-native-fbsdk-next'

// Configure Google Sign-In
GoogleSignin.configure({
  webClientId: process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID,
})

export const authService = {
  /**
   * Login with email and password
   */
  login: async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/login', {
        email,
        password,
      })
      
      const { access_token, refresh_token } = response.data
      await AsyncStorage.setItem('access_token', access_token)
      await AsyncStorage.setItem('refresh_token', refresh_token)
      
      return { success: true, tokens: { access_token, refresh_token } }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      }
    }
  },
  
  /**
   * Register with email and password
   */
  register: async (email: string, password: string, username?: string) => {
    try {
      const response = await apiClient.post('/auth/register', {
        email,
        password,
        username,
      })
      
      const { access_token, refresh_token } = response.data
      await AsyncStorage.setItem('access_token', access_token)
      await AsyncStorage.setItem('refresh_token', refresh_token)
      
      return { success: true, tokens: { access_token, refresh_token } }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      }
    }
  },
  
  /**
   * Login with Google
   */
  loginWithGoogle: async () => {
    try {
      await GoogleSignin.hasPlayServices()
      const userInfo = await GoogleSignin.signIn()
      const token = await GoogleSignin.getTokens()
      
      // Send token to backend
      const response = await apiClient.post('/auth/oauth', {
        provider: 'google',
        token: token.accessToken,
      })
      
      const { access_token, refresh_token } = response.data
      await AsyncStorage.setItem('access_token', access_token)
      await AsyncStorage.setItem('refresh_token', refresh_token)
      
      return { success: true, tokens: { access_token, refresh_token } }
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Google login failed',
      }
    }
  },
  
  /**
   * Login with Apple
   */
  loginWithApple: async () => {
    try {
      const appleAuthRequestResponse = await appleAuth.performRequest({
        requestedOperation: appleAuth.Operation.LOGIN,
        requestedScopes: [appleAuth.Scope.EMAIL, appleAuth.Scope.FULL_NAME],
      })
      
      if (!appleAuthRequestResponse.identityToken) {
        throw new Error('Apple Sign-In failed - no identity token')
      }
      
      // Send token to backend
      const response = await apiClient.post('/auth/oauth', {
        provider: 'apple',
        token: appleAuthRequestResponse.identityToken,
      })
      
      const { access_token, refresh_token } = response.data
      await AsyncStorage.setItem('access_token', access_token)
      await AsyncStorage.setItem('refresh_token', refresh_token)
      
      return { success: true, tokens: { access_token, refresh_token } }
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Apple login failed',
      }
    }
  },
  
  /**
   * Login with Facebook
   */
  loginWithFacebook: async () => {
    try {
      const result = await LoginManager.logInWithPermissions(['public_profile', 'email'])
      
      if (result.isCancelled) {
        return { success: false, error: 'Facebook login cancelled' }
      }
      
      const data = await AccessToken.getCurrentAccessToken()
      if (!data) {
        return { success: false, error: 'No access token' }
      }
      
      // Send token to backend
      const response = await apiClient.post('/auth/oauth', {
        provider: 'facebook',
        token: data.accessToken,
      })
      
      const { access_token, refresh_token } = response.data
      await AsyncStorage.setItem('access_token', access_token)
      await AsyncStorage.setItem('refresh_token', refresh_token)
      
      return { success: true, tokens: { access_token, refresh_token } }
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Facebook login failed',
      }
    }
  },
  
  /**
   * Logout
   */
  logout: async () => {
    await AsyncStorage.removeItem('access_token')
    await AsyncStorage.removeItem('refresh_token')
    await AsyncStorage.removeItem('user')
    await GoogleSignin.signOut()
    LoginManager.logOut()
  },
  
  /**
   * Check if user is authenticated
   */
  isAuthenticated: async (): Promise<boolean> => {
    const token = await AsyncStorage.getItem('access_token')
    return !!token
  },
}

