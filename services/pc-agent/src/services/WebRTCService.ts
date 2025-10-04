/**
 * WebRTC Service for JarvisX PC Agent
 * Handles peer connections, screen streaming, and action event data channels
 */

import { RTCPeerConnection, RTCSessionDescription, RTCIceCandidate } from 'wrtc';
import { EventEmitter } from 'events';

export interface WebRTCSession {
  id: string;
  peerConnection: RTCPeerConnection;
  dataChannel: RTCDataChannel | null;
  status: 'connecting' | 'connected' | 'disconnected' | 'failed';
  startTime: Date;
}

export interface ActionEvent {
  sessionId: string;
  stepId: number;
  action: string;
  selector?: string;
  cursor?: { x: number; y: number };
  status: 'started' | 'completed' | 'failed' | 'queued';
  meta?: {
    screenshot?: string;
    log?: string;
    duration?: number;
  };
  timestamp: string;
}

export class WebRTCService extends EventEmitter {
  private sessions: Map<string, WebRTCSession> = new Map();
  private isInitialized: boolean = false;
  private iceServers: RTCIceServer[] = [];

  constructor() {
    super();
    this.initializeIceServers();
  }

  private initializeIceServers(): void {
    // Use Google's public STUN servers and optionally TURN servers
    this.iceServers = [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' },
      { urls: 'stun:stun2.l.google.com:19302' },
    ];

    // Add TURN servers if configured
    if (process.env.TURN_SERVER_URL) {
      this.iceServers.push({
        urls: process.env.TURN_SERVER_URL,
        username: process.env.TURN_USERNAME || '',
        credential: process.env.TURN_CREDENTIAL || ''
      });
    }
  }

  public async initialize(): Promise<void> {
    try {
      console.log('🌐 Initializing WebRTC Service...');
      this.isInitialized = true;
      console.log('✅ WebRTC Service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize WebRTC Service:', error);
      throw error;
    }
  }

  public isInitialized(): boolean {
    return this.isInitialized;
  }

  public async createPeerConnection(sessionId: string): Promise<RTCPeerConnection> {
    try {
      console.log(`🔗 Creating WebRTC peer connection for session ${sessionId}`);

      const peerConnection = new RTCPeerConnection({
        iceServers: this.iceServers
      });

      // Create data channel for action events
      const dataChannel = peerConnection.createDataChannel('actions', {
        ordered: true,
        maxRetransmits: 3
      });

      // Set up event handlers
      peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          this.emit('iceCandidate', {
            sessionId,
            candidate: event.candidate
          });
        }
      };

      peerConnection.onconnectionstatechange = () => {
        const state = peerConnection.connectionState;
        console.log(`🔗 Peer connection state changed to: ${state}`);
        
        if (state === 'connected') {
          this.updateSessionStatus(sessionId, 'connected');
        } else if (state === 'disconnected' || state === 'failed') {
          this.updateSessionStatus(sessionId, 'disconnected');
        }
      };

      peerConnection.ondatachannel = (event) => {
        const channel = event.channel;
        console.log(`📡 Data channel received: ${channel.label}`);
        
        channel.onopen = () => {
          console.log(`📡 Data channel opened: ${channel.label}`);
        };

        channel.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.emit('dataChannelMessage', { sessionId, message });
          } catch (error) {
            console.error('❌ Failed to parse data channel message:', error);
          }
        };
      };

      // Store session
      const session: WebRTCSession = {
        id: sessionId,
        peerConnection,
        dataChannel,
        status: 'connecting',
        startTime: new Date()
      };

      this.sessions.set(sessionId, session);

      // Set up data channel event handlers
      dataChannel.onopen = () => {
        console.log(`📡 Action data channel opened for session ${sessionId}`);
      };

      dataChannel.onerror = (error) => {
        console.error(`❌ Data channel error for session ${sessionId}:`, error);
      };

      dataChannel.onclose = () => {
        console.log(`📡 Data channel closed for session ${sessionId}`);
      };

      return peerConnection;

    } catch (error) {
      console.error(`❌ Failed to create peer connection for session ${sessionId}:`, error);
      throw error;
    }
  }

  public async handleOffer(sessionId: string, offer: RTCSessionDescription): Promise<RTCSessionDescription> {
    try {
      const session = this.sessions.get(sessionId);
      if (!session) {
        throw new Error(`Session ${sessionId} not found`);
      }

      console.log(`🤝 Handling WebRTC offer for session ${sessionId}`);

      await session.peerConnection.setRemoteDescription(offer);
      const answer = await session.peerConnection.createAnswer();
      await session.peerConnection.setLocalDescription(answer);

      return answer;

    } catch (error) {
      console.error(`❌ Failed to handle offer for session ${sessionId}:`, error);
      throw error;
    }
  }

  public async addIceCandidate(sessionId: string, candidate: RTCIceCandidate): Promise<void> {
    try {
      const session = this.sessions.get(sessionId);
      if (!session) {
        throw new Error(`Session ${sessionId} not found`);
      }

      await session.peerConnection.addIceCandidate(candidate);
      console.log(`🧊 ICE candidate added for session ${sessionId}`);

    } catch (error) {
      console.error(`❌ Failed to add ICE candidate for session ${sessionId}:`, error);
      throw error;
    }
  }

  public async sendActionEvent(sessionId: string, event: ActionEvent): Promise<void> {
    try {
      const session = this.sessions.get(sessionId);
      if (!session || !session.dataChannel || session.dataChannel.readyState !== 'open') {
        console.warn(`⚠️ Cannot send action event - session ${sessionId} not ready`);
        return;
      }

      const message = JSON.stringify({
        type: 'action_event',
        event
      });

      session.dataChannel.send(message);
      console.log(`📡 Action event sent for session ${sessionId}: ${event.action}`);

    } catch (error) {
      console.error(`❌ Failed to send action event for session ${sessionId}:`, error);
    }
  }

  public async closePeerConnection(sessionId: string): Promise<void> {
    try {
      const session = this.sessions.get(sessionId);
      if (!session) {
        console.warn(`⚠️ Session ${sessionId} not found for closure`);
        return;
      }

      console.log(`🔒 Closing WebRTC connection for session ${sessionId}`);

      // Close data channel
      if (session.dataChannel && session.dataChannel.readyState !== 'closed') {
        session.dataChannel.close();
      }

      // Close peer connection
      session.peerConnection.close();
      
      // Remove session
      this.sessions.delete(sessionId);

      console.log(`✅ WebRTC connection closed for session ${sessionId}`);

    } catch (error) {
      console.error(`❌ Failed to close peer connection for session ${sessionId}:`, error);
    }
  }

  public getSession(sessionId: string): WebRTCSession | undefined {
    return this.sessions.get(sessionId);
  }

  public getActiveSessions(): WebRTCSession[] {
    return Array.from(this.sessions.values());
  }

  public getSessionStats(): any {
    const sessions = this.getActiveSessions();
    return {
      total: sessions.length,
      connected: sessions.filter(s => s.status === 'connected').length,
      connecting: sessions.filter(s => s.status === 'connecting').length,
      disconnected: sessions.filter(s => s.status === 'disconnected').length,
      failed: sessions.filter(s => s.status === 'failed').length
    };
  }

  private updateSessionStatus(sessionId: string, status: WebRTCSession['status']): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.status = status;
      this.emit('sessionStatusChanged', { sessionId, status });
    }
  }

  public async createOffer(sessionId: string): Promise<RTCSessionDescription> {
    try {
      const session = this.sessions.get(sessionId);
      if (!session) {
        throw new Error(`Session ${sessionId} not found`);
      }

      const offer = await session.peerConnection.createOffer();
      await session.peerConnection.setLocalDescription(offer);

      return offer;

    } catch (error) {
      console.error(`❌ Failed to create offer for session ${sessionId}:`, error);
      throw error;
    }
  }

  public async setRemoteDescription(sessionId: string, description: RTCSessionDescription): Promise<void> {
    try {
      const session = this.sessions.get(sessionId);
      if (!session) {
        throw new Error(`Session ${sessionId} not found`);
      }

      await session.peerConnection.setRemoteDescription(description);

    } catch (error) {
      console.error(`❌ Failed to set remote description for session ${sessionId}:`, error);
      throw error;
    }
  }
}
