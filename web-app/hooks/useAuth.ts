/**
 * Authentication hook
 */
import { useState, useEffect } from 'react'
import { sessionManager, User } from '@/lib/auth/session'
import { tokenManager } from '@/lib/auth/jwt'
import apiClient from '@/lib/api/client'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  
  useEffect(() => {
    checkAuth()
  }, [])
  
  const checkAuth = async () => {
    setIsLoading(true)
    
    if (!tokenManager.isAuthenticated()) {
      setIsAuthenticated(false)
      setUser(null)
      setIsLoading(false)
      return
    }
    
    try {
      const response = await apiClient.get('/user/me')
      const userData = response.data
      setUser(userData)
      sessionManager.setUser(userData)
      setIsAuthenticated(true)
    } catch (error) {
      // Token invalid, clear session
      sessionManager.clearSession()
      setIsAuthenticated(false)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }
  
  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/login', {
        email,
        password,
      })
      
      const { access_token, refresh_token } = response.data
      tokenManager.setTokens(access_token, refresh_token)
      
      // Get user info
      await checkAuth()
      
      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      }
    }
  }
  
  const register = async (email: string, password: string, username?: string) => {
    try {
      const response = await apiClient.post('/auth/register', {
        email,
        password,
        username,
      })
      
      const { access_token, refresh_token } = response.data
      tokenManager.setTokens(access_token, refresh_token)
      
      // Get user info
      await checkAuth()
      
      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      }
    }
  }
  
  const logout = () => {
    sessionManager.clearSession()
    setUser(null)
    setIsAuthenticated(false)
  }
  
  return {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    oauthLogin,
    forgotPassword,
    resetPassword,
    verifyEmail,
    logout,
    checkAuth,
  }
}

