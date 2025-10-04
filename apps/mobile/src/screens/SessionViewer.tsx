/**
 * JarvisX Mobile Session Viewer
 * Real-time screen streaming and action control interface
 */

import React, { useEffect, useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Dimensions,
  SafeAreaView,
} from 'react-native';
import { RTCView, RTCPeerConnection, mediaDevices } from 'react-native-webrtc';
import { CheckCircle, XCircle, Mic, MicOff, Monitor, Settings } from 'lucide-react-native';

const { width, height } = Dimensions.get('window');

interface ActionEvent {
  sessionId: string;
  stepId: number;
  action: string;
  status: 'started' | 'completed' | 'failed' | 'queued';
  timestamp: string;
}

interface SessionViewerProps {
  signalingUrl: string;
  sessionId?: string;
  onClose?: () => void;
}

export function SessionViewer({ signalingUrl, sessionId, onClose }: SessionViewerProps) {
  const [stream, setStream] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [events, setEvents] = useState<ActionEvent[]>([]);
  const [pendingApprovals, setPendingApprovals] = useState<any[]>([]);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    initializeConnection();
    return () => {
      cleanup();
    };
  }, []);

  const initializeConnection = async () => {
    try {
      // Create WebSocket connection to orchestrator
      const ws = new WebSocket(signalingUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('🔌 Connected to orchestrator');
        setIsConnected(true);
        setStatus('connecting');
        
        // Request to join session
        if (sessionId) {
          ws.send(JSON.stringify({
            type: 'join_session',
            data: { sessionId }
          }));
        }
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('❌ Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        setIsConnected(false);
        setStatus('disconnected');
      };

      // Create WebRTC peer connection
      const peerConnection = new RTCPeerConnection({
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
      });

      peerConnectionRef.current = peerConnection;

      peerConnection.onconnectionstatechange = () => {
        const state = peerConnection.connectionState;
        console.log(`🔗 WebRTC state: ${state}`);
        
        if (state === 'connected') {
          setStatus('connected');
        } else if (state === 'disconnected' || state === 'failed') {
          setStatus('disconnected');
        }
      };

      peerConnection.ontrack = (event) => {
        console.log('📺 Received remote stream');
        setStream(event.streams[0]);
      };

      peerConnection.ondatachannel = (event) => {
        const channel = event.channel;
        console.log(`📡 Data channel received: ${channel.label}`);
        
        channel.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            handleDataChannelMessage(message);
          } catch (error) {
            console.error('❌ Failed to parse data channel message:', error);
          }
        };
      };

    } catch (error) {
      console.error('❌ Failed to initialize connection:', error);
      Alert.alert('Connection Error', 'Failed to connect to JarvisX');
    }
  };

  const handleWebSocketMessage = (message: any) => {
    switch (message.type) {
      case 'session_joined':
        setStatus('connected');
        break;
      
      case 'webrtc_offer':
        handleWebRTCOffer(message.data);
        break;
      
      case 'webrtc_answer':
        handleWebRTCAnswer(message.data);
        break;
      
      case 'ice_candidate':
        handleIceCandidate(message.data);
        break;
      
      case 'approval_request':
        setPendingApprovals(prev => [...prev, message.data]);
        break;
    }
  };

  const handleDataChannelMessage = (message: any) => {
    switch (message.type) {
      case 'action_event':
        setEvents(prev => [...prev, message.event]);
        break;
    }
  };

  const handleWebRTCOffer = async (offer: any) => {
    try {
      if (!peerConnectionRef.current) return;

      await peerConnectionRef.current.setRemoteDescription(offer);
      const answer = await peerConnectionRef.current.createAnswer();
      await peerConnectionRef.current.setLocalDescription(answer);

      // Send answer back via WebSocket
      wsRef.current?.send(JSON.stringify({
        type: 'webrtc_answer',
        data: answer
      }));

    } catch (error) {
      console.error('❌ Failed to handle WebRTC offer:', error);
    }
  };

  const handleWebRTCAnswer = async (answer: any) => {
    try {
      if (!peerConnectionRef.current) return;
      await peerConnectionRef.current.setRemoteDescription(answer);
    } catch (error) {
      console.error('❌ Failed to handle WebRTC answer:', error);
    }
  };

  const handleIceCandidate = async (candidate: any) => {
    try {
      if (!peerConnectionRef.current) return;
      await peerConnectionRef.current.addIceCandidate(candidate);
    } catch (error) {
      console.error('❌ Failed to handle ICE candidate:', error);
    }
  };

  const handleMicToggle = () => {
    setIsMuted(!isMuted);
    wsRef.current?.send(JSON.stringify({
      type: 'voice_control',
      data: { action: isMuted ? 'unmute' : 'mute' }
    }));
  };

  const handleApproval = (approvalId: string, approved: boolean) => {
    wsRef.current?.send(JSON.stringify({
      type: 'approval_response',
      data: { approvalId, approved }
    }));
    
    setPendingApprovals(prev => prev.filter(a => a.id !== approvalId));
  };

  const cleanup = () => {
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
    }
    if (wsRef.current) {
      wsRef.current.close();
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <View style={[styles.statusDot, { backgroundColor: 
            status === 'connected' ? '#10B981' : 
            status === 'connecting' ? '#F59E0B' : '#EF4444'
          }]} />
          <Text style={styles.headerTitle}>JarvisX Session</Text>
        </View>
        
        <View style={styles.headerRight}>
          <TouchableOpacity
            style={[styles.iconButton, isMuted && styles.iconButtonActive]}
            onPress={handleMicToggle}
          >
            {isMuted ? <MicOff size={20} color="#fff" /> : <Mic size={20} color="#fff" />}
          </TouchableOpacity>
          
          {onClose && (
            <TouchableOpacity style={styles.iconButton} onPress={onClose}>
              <XCircle size={20} color="#fff" />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Screen Stream */}
      <View style={styles.screenContainer}>
        {stream ? (
          <RTCView
            style={styles.remoteVideo}
            streamURL={stream.toURL()}
            objectFit="cover"
          />
        ) : (
          <View style={styles.placeholderContainer}>
            <Monitor size={64} color="#6B7280" />
            <Text style={styles.placeholderText}>
              {status === 'connecting' ? 'Connecting...' : 'No screen stream'}
            </Text>
          </View>
        )}
      </View>

      {/* Action Timeline */}
      <View style={styles.timelineContainer}>
        <Text style={styles.timelineTitle}>Live Actions</Text>
        <ScrollView style={styles.timeline} showsVerticalScrollIndicator={false}>
          {events.map((event, index) => (
            <View key={index} style={[
              styles.eventItem,
              event.status === 'completed' && styles.eventCompleted,
              event.status === 'failed' && styles.eventFailed,
              event.status === 'started' && styles.eventStarted
            ]}>
              <View style={styles.eventIcon}>
                {event.status === 'completed' && <CheckCircle size={16} color="#10B981" />}
                {event.status === 'failed' && <XCircle size={16} color="#EF4444" />}
                {event.status === 'started' && <Settings size={16} color="#3B82F6" />}
              </View>
              
              <View style={styles.eventContent}>
                <Text style={styles.eventAction}>{event.action}</Text>
                <Text style={styles.eventTime}>
                  Step {event.stepId} • {new Date(event.timestamp).toLocaleTimeString()}
                </Text>
              </View>
            </View>
          ))}
          
          {events.length === 0 && (
            <View style={styles.emptyTimeline}>
              <Text style={styles.emptyText}>No actions yet</Text>
            </View>
          )}
        </ScrollView>
      </View>

      {/* Pending Approvals */}
      {pendingApprovals.length > 0 && (
        <View style={styles.approvalsContainer}>
          <Text style={styles.approvalsTitle}>Pending Approvals</Text>
          {pendingApprovals.map((approval) => (
            <View key={approval.id} style={styles.approvalItem}>
              <Text style={styles.approvalAction}>{approval.action}</Text>
              <View style={styles.approvalButtons}>
                <TouchableOpacity
                  style={[styles.approvalButton, styles.approveButton]}
                  onPress={() => handleApproval(approval.id, true)}
                >
                  <Text style={styles.approvalButtonText}>✓</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.approvalButton, styles.rejectButton]}
                  onPress={() => handleApproval(approval.id, false)}
                >
                  <Text style={styles.approvalButtonText}>✗</Text>
                </TouchableOpacity>
              </View>
            </View>
          ))}
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1F2937',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#111827',
    borderBottomWidth: 1,
    borderBottomColor: '#374151',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  headerTitle: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
  headerRight: {
    flexDirection: 'row',
    gap: 8,
  },
  iconButton: {
    padding: 8,
    borderRadius: 8,
    backgroundColor: '#374151',
  },
  iconButtonActive: {
    backgroundColor: '#EF4444',
  },
  screenContainer: {
    flex: 1,
    backgroundColor: '#000000',
  },
  remoteVideo: {
    flex: 1,
  },
  placeholderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#111827',
  },
  placeholderText: {
    color: '#9CA3AF',
    fontSize: 16,
    marginTop: 16,
  },
  timelineContainer: {
    height: 200,
    backgroundColor: '#111827',
    borderTopWidth: 1,
    borderTopColor: '#374151',
  },
  timelineTitle: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  timeline: {
    flex: 1,
    paddingHorizontal: 16,
  },
  eventItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#374151',
  },
  eventCompleted: {
    backgroundColor: '#10B98110',
  },
  eventFailed: {
    backgroundColor: '#EF444410',
  },
  eventStarted: {
    backgroundColor: '#3B82F610',
  },
  eventIcon: {
    marginRight: 12,
  },
  eventContent: {
    flex: 1,
  },
  eventAction: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '500',
  },
  eventTime: {
    color: '#9CA3AF',
    fontSize: 12,
    marginTop: 2,
  },
  emptyTimeline: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    color: '#6B7280',
    fontSize: 14,
  },
  approvalsContainer: {
    backgroundColor: '#111827',
    borderTopWidth: 1,
    borderTopColor: '#374151',
    padding: 16,
  },
  approvalsTitle: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  approvalItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#F59E0B20',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  approvalAction: {
    color: '#F59E0B',
    fontSize: 14,
    flex: 1,
  },
  approvalButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  approvalButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  approveButton: {
    backgroundColor: '#10B981',
  },
  rejectButton: {
    backgroundColor: '#EF4444',
  },
  approvalButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default SessionViewer;
