/**
 * API client for mobile app
 */
import axios from 'axios'
import AsyncStorage from '@react-native-async-storage/async-storage'

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000'
const API_PREFIX = '/api/v1'

const apiClient = axios.create({
  baseURL: `${API_URL}${API_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      // Try to refresh token
      const refreshToken = await AsyncStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(
            `${API_URL}${API_PREFIX}/auth/refresh`,
            { refresh_token: refreshToken }
          )
          
          const { access_token, refresh_token } = response.data
          await AsyncStorage.setItem('access_token', access_token)
          await AsyncStorage.setItem('refresh_token', refresh_token)
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } catch (refreshError) {
          // Refresh failed, clear tokens
          await AsyncStorage.removeItem('access_token')
          await AsyncStorage.removeItem('refresh_token')
          return Promise.reject(refreshError)
        }
      }
    }
    
    return Promise.reject(error)
  }
)

export default apiClient

