/**
 * Remote Control Screen - Mobile remote control for desktop JarvisX
 * Voice commands, system control, and approval management
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  TextInput,
  Dimensions,
  StatusBar,
} from 'react-native';
import { Mic, MicOff, Volume2, VolumeX, Monitor, Settings, Shield, Zap } from 'lucide-react-native';
import PushNotificationService from '../services/PushNotificationService';
import RemoteControlService from '../services/RemoteControlService';

const { width, height } = Dimensions.get('window');

interface RemoteControlScreenProps {
  navigation: any;
}

const RemoteControlScreen: React.FC<RemoteControlScreenProps> = ({ navigation }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState('focused');
  const [confidence, setConfidence] = useState(0);
  const [lastCommand, setLastCommand] = useState('');
  const [voiceCommand, setVoiceCommand] = useState('');
  const [systemStats, setSystemStats] = useState({
    cpu: 0,
    memory: 0,
    network: 0,
    uptime: '0h 0m'
  });
  const [pendingApprovals, setPendingApprovals] = useState<any[]>([]);
  const [commandHistory, setCommandHistory] = useState<any[]>([]);

  const pushNotificationService = PushNotificationService.getInstance();
  const remoteControlService = RemoteControlService.getInstance();

  useEffect(() => {
    initializeServices();
    return () => {
      cleanup();
    };
  }, []);

  const initializeServices = async () => {
    try {
      // Setup remote control event handlers
      remoteControlService.on('connected', () => {
        setIsConnected(true);
        console.log('✅ Connected to desktop JarvisX');
      });

      remoteControlService.on('disconnected', () => {
        setIsConnected(false);
        console.log('🔌 Disconnected from desktop JarvisX');
      });

      remoteControlService.on('status_update', (status) => {
        setSystemStats(status.systemStats);
        setIsListening(status.isListening);
        setIsSpeaking(status.isSpeaking);
        setCurrentEmotion(status.currentEmotion);
        setConfidence(status.confidence);
        setLastCommand(status.lastCommand);
      });

      remoteControlService.on('approval_request', (approval) => {
        setPendingApprovals(prev => [approval, ...prev]);
        
        // Show push notification
        pushNotificationService.showApprovalNotification(
          approval.id,
          approval.action,
          approval.description
        );
      });

      remoteControlService.on('command_result', (command) => {
        setCommandHistory(prev => 
          prev.map(cmd => cmd.id === command.id ? command : cmd)
        );
      });

      // Load initial data
      await loadInitialData();

    } catch (error) {
      console.error('❌ Failed to initialize services:', error);
    }
  };

  const loadInitialData = async () => {
    try {
      const status = await remoteControlService.getDesktopStatus();
      if (status) {
        setSystemStats(status.systemStats);
        setIsListening(status.isListening);
        setIsSpeaking(status.isSpeaking);
        setCurrentEmotion(status.currentEmotion);
        setConfidence(status.confidence);
        setLastCommand(status.lastCommand);
      }

      const approvals = await remoteControlService.getPendingApprovals();
      setPendingApprovals(approvals);

      const history = remoteControlService.getCommandHistory();
      setCommandHistory(history);

    } catch (error) {
      console.error('❌ Failed to load initial data:', error);
    }
  };

  const cleanup = () => {
    remoteControlService.disconnect();
  };

  const handleVoiceCommand = async () => {
    if (!voiceCommand.trim()) return;

    try {
      const commandId = await remoteControlService.sendVoiceCommand(voiceCommand);
      setVoiceCommand('');
      
      // Add to command history
      setCommandHistory(prev => [{
        id: commandId,
        type: 'voice',
        action: 'execute_voice_command',
        parameters: { command: voiceCommand },
        timestamp: Date.now(),
        status: 'pending'
      }, ...prev]);

    } catch (error) {
      Alert.alert('Error', 'Failed to send voice command');
      console.error('❌ Voice command error:', error);
    }
  };

  const handleQuickCommand = async (command: string) => {
    try {
      await remoteControlService.sendVoiceCommand(command);
    } catch (error) {
      Alert.alert('Error', 'Failed to send command');
      console.error('❌ Quick command error:', error);
    }
  };

  const handleApproval = async (requestId: string, approved: boolean) => {
    try {
      const success = await remoteControlService.approveRequest(
        requestId, 
        approved, 
        `Mobile ${approved ? 'approval' : 'rejection'}`
      );
      
      if (success) {
        setPendingApprovals(prev => 
          prev.map(approval => 
            approval.id === requestId 
              ? { ...approval, status: approved ? 'approved' : 'rejected' }
              : approval
          )
        );
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to send approval decision');
      console.error('❌ Approval error:', error);
    }
  };

  const getEmotionColor = (emotion: string) => {
    switch (emotion.toLowerCase()) {
      case 'happy': return '#10B981';
      case 'excited': return '#F59E0B';
      case 'focused': return '#3B82F6';
      case 'thinking': return '#8B5CF6';
      case 'listening': return '#EF4444';
      case 'speaking': return '#06B6D4';
      default: return '#6B7280';
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000000" />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <View 
            style={[styles.statusDot, { backgroundColor: isConnected ? '#10B981' : '#EF4444' }]} 
          />
          <Text style={styles.headerTitle}>JarvisX Remote</Text>
        </View>
        <TouchableOpacity 
          style={styles.settingsButton}
          onPress={() => navigation.navigate('Settings')}
        >
          <Settings size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Desktop Status */}
        <View style={styles.statusCard}>
          <Text style={styles.cardTitle}>Desktop Status</Text>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Status</Text>
            <Text style={[styles.statusValue, { color: getEmotionColor(currentEmotion) }]}>
              {isListening ? 'Listening' : isSpeaking ? 'Speaking' : 'Idle'}
            </Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Emotion</Text>
            <Text style={styles.statusValue}>{currentEmotion}</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Confidence</Text>
            <Text style={styles.statusValue}>{Math.round(confidence)}%</Text>
          </View>
        </View>

        {/* System Stats */}
        <View style={styles.statsCard}>
          <Text style={styles.cardTitle}>System Performance</Text>
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>CPU</Text>
            <View style={styles.progressBar}>
              <View style={[styles.progressFill, { width: `${systemStats.cpu}%`, backgroundColor: '#3B82F6' }]} />
            </View>
            <Text style={styles.statValue}>{systemStats.cpu}%</Text>
          </View>
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Memory</Text>
            <View style={styles.progressBar}>
              <View style={[styles.progressFill, { width: `${systemStats.memory}%`, backgroundColor: '#10B981' }]} />
            </View>
            <Text style={styles.statValue}>{systemStats.memory}%</Text>
          </View>
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Network</Text>
            <View style={styles.progressBar}>
              <View style={[styles.progressFill, { width: `${systemStats.network}%`, backgroundColor: '#8B5CF6' }]} />
            </View>
            <Text style={styles.statValue}>{systemStats.network}%</Text>
          </View>
        </View>

        {/* Voice Command */}
        <View style={styles.commandCard}>
          <Text style={styles.cardTitle}>Voice Command</Text>
          <View style={styles.commandInput}>
            <TextInput
              style={styles.textInput}
              placeholder="Type a command for JarvisX..."
              placeholderTextColor="#6B7280"
              value={voiceCommand}
              onChangeText={setVoiceCommand}
              multiline
            />
            <TouchableOpacity 
              style={styles.sendButton}
              onPress={handleVoiceCommand}
              disabled={!voiceCommand.trim()}
            >
              <Mic size={20} color="#FFFFFF" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Quick Commands */}
        <View style={styles.quickCommandsCard}>
          <Text style={styles.cardTitle}>Quick Commands</Text>
          <View style={styles.quickCommandsGrid}>
            <TouchableOpacity 
              style={styles.quickCommandButton}
              onPress={() => handleQuickCommand('Open Chrome')}
            >
              <Monitor size={20} color="#FFFFFF" />
              <Text style={styles.quickCommandText}>Open Chrome</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.quickCommandButton}
              onPress={() => handleQuickCommand('Check email')}
            >
              <Volume2 size={20} color="#FFFFFF" />
              <Text style={styles.quickCommandText}>Check Email</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.quickCommandButton}
              onPress={() => handleQuickCommand('Show system status')}
            >
              <Settings size={20} color="#FFFFFF" />
              <Text style={styles.quickCommandText}>System Status</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.quickCommandButton}
              onPress={() => handleQuickCommand('Emergency stop')}
            >
              <Shield size={20} color="#FFFFFF" />
              <Text style={styles.quickCommandText}>Emergency Stop</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Pending Approvals */}
        {pendingApprovals.length > 0 && (
          <View style={styles.approvalsCard}>
            <Text style={styles.cardTitle}>Pending Approvals</Text>
            {pendingApprovals.slice(0, 3).map((approval) => (
              <View key={approval.id} style={styles.approvalItem}>
                <View style={styles.approvalContent}>
                  <Text style={styles.approvalAction}>{approval.action}</Text>
                  <Text style={styles.approvalDescription}>{approval.description}</Text>
                  <Text style={styles.approvalRisk}>
                    Risk: {approval.riskCategory} ({approval.riskScore}%)
                  </Text>
                </View>
                <View style={styles.approvalActions}>
                  <TouchableOpacity 
                    style={[styles.approvalButton, styles.approveButton]}
                    onPress={() => handleApproval(approval.id, true)}
                  >
                    <Text style={styles.approvalButtonText}>Approve</Text>
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={[styles.approvalButton, styles.rejectButton]}
                    onPress={() => handleApproval(approval.id, false)}
                  >
                    <Text style={styles.approvalButtonText}>Reject</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Command History */}
        {commandHistory.length > 0 && (
          <View style={styles.historyCard}>
            <Text style={styles.cardTitle}>Recent Commands</Text>
            {commandHistory.slice(0, 5).map((command) => (
              <View key={command.id} style={styles.historyItem}>
                <Text style={styles.historyCommand}>{command.parameters.command || command.action}</Text>
                <Text style={styles.historyStatus}>{command.status}</Text>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.1)',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 12,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  settingsButton: {
    padding: 8,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  statusCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 12,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusLabel: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  statusValue: {
    fontSize: 14,
    color: '#FFFFFF',
    fontWeight: '500',
  },
  statsCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  statRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  statLabel: {
    fontSize: 14,
    color: '#9CA3AF',
    width: 60,
  },
  progressBar: {
    flex: 1,
    height: 8,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 4,
    marginHorizontal: 12,
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  statValue: {
    fontSize: 14,
    color: '#FFFFFF',
    fontWeight: '500',
    width: 40,
    textAlign: 'right',
  },
  commandCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  commandInput: {
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  textInput: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 8,
    padding: 12,
    color: '#FFFFFF',
    fontSize: 16,
    marginRight: 12,
    minHeight: 48,
  },
  sendButton: {
    backgroundColor: '#3B82F6',
    borderRadius: 8,
    padding: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  quickCommandsCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  quickCommandsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickCommandButton: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
    width: (width - 60) / 2,
    marginBottom: 12,
  },
  quickCommandText: {
    color: '#FFFFFF',
    fontSize: 12,
    marginTop: 4,
    textAlign: 'center',
  },
  approvalsCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  approvalItem: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  approvalContent: {
    marginBottom: 12,
  },
  approvalAction: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  approvalDescription: {
    color: '#9CA3AF',
    fontSize: 14,
    marginBottom: 4,
  },
  approvalRisk: {
    color: '#F59E0B',
    fontSize: 12,
  },
  approvalActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  approvalButton: {
    flex: 1,
    padding: 8,
    borderRadius: 6,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  approveButton: {
    backgroundColor: '#10B981',
  },
  rejectButton: {
    backgroundColor: '#EF4444',
  },
  approvalButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
  },
  historyCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  historyItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.1)',
  },
  historyCommand: {
    color: '#FFFFFF',
    fontSize: 14,
    flex: 1,
  },
  historyStatus: {
    color: '#9CA3AF',
    fontSize: 12,
    textTransform: 'capitalize',
  },
});

export default RemoteControlScreen;
