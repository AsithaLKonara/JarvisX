/**
 * Main app navigator
 */
import React, { useEffect, useState } from 'react'
import { NavigationContainer } from '@react-navigation/native'
import { createStackNavigator } from '@react-navigation/stack'
import { authService } from '../services/auth'
import LoginScreen from '../screens/Auth/LoginScreen'
import RegisterScreen from '../screens/Auth/RegisterScreen'
import ChatScreen from '../screens/Chat/ChatScreen'
import ChatWidget from '../components/chat/ChatWidget'

const Stack = createStackNavigator()

export default function AppNavigator() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  
  useEffect(() => {
    checkAuth()
  }, [])
  
  const checkAuth = async () => {
    const authenticated = await authService.isAuthenticated()
    setIsAuthenticated(authenticated)
    setIsLoading(false)
  }
  
  if (isLoading) {
    return null // Show loading screen
  }
  
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
        }}
      >
        {!isAuthenticated ? (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Signup" component={RegisterScreen} />
          </>
        ) : (
          <Stack.Screen name="Chat" component={ChatScreen} />
        )}
      </Stack.Navigator>
      {isAuthenticated && <ChatWidget />}
    </NavigationContainer>
  )
}

