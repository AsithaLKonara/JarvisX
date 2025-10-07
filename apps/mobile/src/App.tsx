/**
 * JarvisX Mobile App - Main Entry Point
 * Native iOS & Android companion with AR avatar and remote control
 */

import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'react-native';
import { JarvisXClient } from '@jarvisx/sdk';
import { getDeviceInfo } from '@jarvisx/sdk/dist/utils/deviceInfo';

// Screens
import HomeScreen from './screens/HomeScreen';
import AvatarViewScreen from './screens/AvatarViewScreen';
import TasksScreen from './screens/TasksScreen';
import RemoteControlScreen from './screens/RemoteControlScreen';
import SettingsScreen from './screens/SettingsScreen';

// Create navigator
const Tab = createBottomTabNavigator();

export default function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [client, setClient] = useState<JarvisXClient | null>(null);

  useEffect(() => {
    initializeClient();
  }, []);

  const initializeClient = async () => {
    try {
      const deviceInfo = getDeviceInfo();
      
      const jarvisClient = new JarvisXClient({
        apiUrl: 'http://YOUR_SERVER_IP:3000',  // Change to your server
        wsUrl: 'ws://YOUR_SERVER_IP:3000',
        deviceId: deviceInfo.deviceId,
        deviceType: 'mobile',
        platform: deviceInfo.platform as any,
        enableOfflineMode: false,
        enableLocalWhisper: false,
        enableAvatar: true
      });

      // Setup event listeners
      jarvisClient.on('connected', () => {
        console.log('✅ Connected to JarvisX');
        setIsConnected(true);
      });

      jarvisClient.on('disconnected', () => {
        console.log('🔌 Disconnected from JarvisX');
        setIsConnected(false);
      });

      jarvisClient.on('avatar_update', (state) => {
        console.log('🎭 Avatar updated:', state.currentEmotion);
      });

      jarvisClient.on('task_update', (task) => {
        console.log('📋 Task updated:', task.id, task.status);
      });

      setClient(jarvisClient);

      // Try to connect if already authenticated
      // (In production, check stored credentials)
      
    } catch (error) {
      console.error('Failed to initialize client:', error);
    }
  };

  return (
    <>
      <StatusBar barStyle="light-content" />
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={{
            headerShown: false,
            tabBarStyle: {
              backgroundColor: '#000000',
              borderTopColor: 'rgba(255,255,255,0.1)',
            },
            tabBarActiveTintColor: '#3B82F6',
            tabBarInactiveTintColor: '#6B7280',
          }}
        >
          <Tab.Screen 
            name="Home" 
            component={HomeScreen}
            options={{
              tabBarIcon: ({ color }) => <span style={{ fontSize: 24 }}>🏠</span>,
            }}
          />
          <Tab.Screen 
            name="Avatar" 
            component={AvatarViewScreen}
            options={{
              tabBarIcon: ({ color }) => <span style={{ fontSize: 24 }}>🎭</span>,
            }}
          />
          <Tab.Screen 
            name="Tasks" 
            component={TasksScreen}
            options={{
              tabBarIcon: ({ color }) => <span style={{ fontSize: 24 }}>📋</span>,
            }}
          />
          <Tab.Screen 
            name="Remote" 
            component={RemoteControlScreen}
            options={{
              tabBarIcon: ({ color }) => <span style={{ fontSize: 24 }}>📱</span>,
            }}
          />
          <Tab.Screen 
            name="Settings" 
            component={SettingsScreen}
            options={{
              tabBarIcon: ({ color }) => <span style={{ fontSize: 24 }}>⚙️</span>,
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </>
  );
}
