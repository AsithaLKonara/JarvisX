/**
 * Avatar View Screen - Full-screen avatar companion view
 * Mobile screen for interacting with Joi avatar
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  Text,
  StatusBar,
} from 'react-native';
import ARAvatarCompanion from '../components/ARAvatarCompanion';

interface AvatarViewScreenProps {
  navigation: any;
}

export function AvatarViewScreen({ navigation }: AvatarViewScreenProps) {
  const [emotionColor, setEmotionColor] = useState('#3B82F6');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [lipSyncData, setLipSyncData] = useState<number[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    connectToServices();
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  /**
   * Connect to JarvisX services
   */
  const connectToServices = () => {
    try {
      // Connect to personality service
      const websocket = new WebSocket('ws://localhost:8007');
      
      websocket.onopen = () => {
        console.log('🎭 Connected to JarvisX services');
        setIsConnected(true);
      };

      websocket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleMessage(message);
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      };

      websocket.onclose = () => {
        console.log('🎭 Disconnected from JarvisX');
        setIsConnected(false);
        
        // Attempt reconnection
        setTimeout(connectToServices, 3000);
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      setWs(websocket);
    } catch (error) {
      console.error('Failed to connect to services:', error);
    }
  };

  /**
   * Handle WebSocket messages
   */
  const handleMessage = (message: any) => {
    switch (message.type) {
      case 'emotion_update':
        const moodColors: { [key: string]: string } = {
          'happy': '#10B981',
          'excited': '#F59E0B',
          'concerned': '#EF4444',
          'confident': '#3B82F6',
          'curious': '#8B5CF6',
          'proud': '#EC4899',
          'grateful': '#06B6D4',
          'optimistic': '#84CC16',
        };
        setEmotionColor(moodColors[message.data.mood] || '#3B82F6');
        break;

      case 'listening_start':
        setIsListening(true);
        setIsSpeaking(false);
        break;

      case 'listening_end':
        setIsListening(false);
        break;

      case 'voice_synthesis_start':
        setIsSpeaking(true);
        setIsListening(false);
        break;

      case 'voice_synthesis_end':
        setIsSpeaking(false);
        setLipSyncData([]);
        break;

      case 'lipsync_data':
        setLipSyncData(message.data);
        break;

      default:
        break;
    }
  };

  /**
   * Handle avatar tap
   */
  const handleAvatarTap = () => {
    console.log('Avatar tapped');
    
    // Send interaction event
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'avatar_interaction',
        data: { action: 'tap' }
      }));
    }
  };

  /**
   * Toggle listening mode
   */
  const toggleListening = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: isListening ? 'stop_listening' : 'start_listening'
      }));
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      {/* Avatar View */}
      <View style={styles.avatarContainer}>
        <ARAvatarCompanion
          emotionColor={emotionColor}
          isListening={isListening}
          isSpeaking={isSpeaking}
          lipSyncData={lipSyncData}
          onAvatarTap={handleAvatarTap}
        />
      </View>

      {/* Control Bar */}
      <View style={styles.controlBar}>
        {/* Connection Status */}
        <View style={styles.statusContainer}>
          <View style={[
            styles.statusDot,
            { backgroundColor: isConnected ? '#10B981' : '#EF4444' }
          ]} />
          <Text style={styles.statusText}>
            {isConnected ? 'Connected' : 'Connecting...'}
          </Text>
        </View>

        {/* Listen Button */}
        <TouchableOpacity
          style={[
            styles.listenButton,
            isListening && styles.listenButtonActive
          ]}
          onPress={toggleListening}
        >
          <Text style={styles.listenButtonText}>
            {isListening ? '🎤 Listening' : '🎤 Tap to Speak'}
          </Text>
        </TouchableOpacity>

        {/* Back Button */}
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>← Back</Text>
        </TouchableOpacity>
      </View>

      {/* Ambient Glow */}
      <View 
        style={[
          styles.ambientGlow,
          { backgroundColor: `${emotionColor}20` }
        ]} 
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  avatarContainer: {
    flex: 1,
  },
  controlBar: {
    position: 'absolute',
    bottom: 30,
    left: 20,
    right: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: 12,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '500',
  },
  listenButton: {
    flex: 1,
    backgroundColor: 'rgba(59, 130, 246, 0.3)',
    paddingVertical: 16,
    borderRadius: 25,
    borderWidth: 2,
    borderColor: 'rgba(59, 130, 246, 0.5)',
    alignItems: 'center',
  },
  listenButtonActive: {
    backgroundColor: 'rgba(59, 130, 246, 0.6)',
    borderColor: 'rgba(59, 130, 246, 0.8)',
  },
  listenButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  backButton: {
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  backButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
  },
  ambientGlow: {
    position: 'absolute',
    inset: 0,
    opacity: 0.3,
    pointerEvents: 'none',
  },
});

export default AvatarViewScreen;

