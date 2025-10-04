/**
 * JarvisX Mobile Home Screen
 * Main dashboard with quick actions and session controls
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Dimensions,
} from 'react-native';
import { Mic, Monitor, TrendingUp, Settings, Activity, CheckCircle } from 'lucide-react-native';

const { width } = Dimensions.get('window');

interface HomeScreenProps {
  navigation: any;
}

export default function HomeScreen({ navigation }: HomeScreenProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [activeSession, setActiveSession] = useState<string | null>(null);
  const [recentTasks, setRecentTasks] = useState<any[]>([]);

  useEffect(() => {
    // Check connection status
    checkConnectionStatus();
    // Load recent tasks
    loadRecentTasks();
  }, []);

  const checkConnectionStatus = async () => {
    try {
      // Simulate connection check
      setIsConnected(true);
    } catch (error) {
      setIsConnected(false);
    }
  };

  const loadRecentTasks = async () => {
    // Simulate loading recent tasks
    setRecentTasks([
      { id: '1', action: 'Open VS Code', status: 'completed', timestamp: new Date() },
      { id: '2', action: 'Create new project', status: 'running', timestamp: new Date() },
      { id: '3', action: 'Deploy to staging', status: 'pending', timestamp: new Date() },
    ]);
  };

  const handleQuickAction = (action: string) => {
    Alert.alert('Quick Action', `Executing: ${action}`);
  };

  const handleStartSession = () => {
    navigation.navigate('SessionViewer', {
      sessionId: `session_${Date.now()}`,
      signalingUrl: 'ws://localhost:3000'
    });
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <View style={[styles.statusDot, { backgroundColor: isConnected ? '#10B981' : '#EF4444' }]} />
          <Text style={styles.headerTitle}>JarvisX</Text>
        </View>
        <Text style={styles.headerSubtitle}>Mobile Assistant</Text>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionsGrid}>
          <TouchableOpacity 
            style={styles.actionCard}
            onPress={() => handleQuickAction('Open IDE')}
          >
            <Monitor size={24} color="#6366f1" />
            <Text style={styles.actionText}>Open IDE</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.actionCard}
            onPress={() => handleQuickAction('Run Tests')}
          >
            <Activity size={24} color="#10B981" />
            <Text style={styles.actionText}>Run Tests</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.actionCard}
            onPress={() => handleQuickAction('Git Status')}
          >
            <Settings size={24} color="#F59E0B" />
            <Text style={styles.actionText}>Git Status</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.actionCard}
            onPress={() => navigation.navigate('Trading')}
          >
            <TrendingUp size={24} color="#8B5CF6" />
            <Text style={styles.actionText}>Trading</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Session Control */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Session Control</Text>
        <TouchableOpacity 
          style={[styles.sessionButton, activeSession && styles.sessionButtonActive]}
          onPress={handleStartSession}
        >
          <Mic size={20} color="#FFFFFF" />
          <Text style={styles.sessionButtonText}>
            {activeSession ? 'View Live Session' : 'Start Session'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Recent Tasks */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Tasks</Text>
        {recentTasks.map((task) => (
          <View key={task.id} style={styles.taskItem}>
            <View style={styles.taskIcon}>
              {task.status === 'completed' && <CheckCircle size={16} color="#10B981" />}
              {task.status === 'running' && <Activity size={16} color="#3B82F6" />}
              {task.status === 'pending' && <Activity size={16} color="#F59E0B" />}
            </View>
            <View style={styles.taskContent}>
              <Text style={styles.taskAction}>{task.action}</Text>
              <Text style={styles.taskStatus}>{task.status}</Text>
            </View>
          </View>
        ))}
      </View>

      {/* Connection Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Connection Status</Text>
        <View style={styles.statusCard}>
          <Text style={styles.statusText}>
            {isConnected ? 'Connected to JarvisX' : 'Disconnected'}
          </Text>
          <Text style={styles.statusSubtext}>
            {isConnected ? 'All services operational' : 'Check your connection'}
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#111827',
  },
  header: {
    padding: 20,
    paddingTop: 10,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 12,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionCard: {
    width: (width - 60) / 2,
    backgroundColor: '#1F2937',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#374151',
  },
  actionText: {
    color: '#FFFFFF',
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
  },
  sessionButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  sessionButtonActive: {
    backgroundColor: '#10B981',
  },
  sessionButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  taskItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1F2937',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#374151',
  },
  taskIcon: {
    marginRight: 12,
  },
  taskContent: {
    flex: 1,
  },
  taskAction: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '500',
  },
  taskStatus: {
    color: '#9CA3AF',
    fontSize: 12,
    marginTop: 2,
  },
  statusCard: {
    backgroundColor: '#1F2937',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#374151',
  },
  statusText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '500',
  },
  statusSubtext: {
    color: '#9CA3AF',
    fontSize: 14,
    marginTop: 4,
  },
});
