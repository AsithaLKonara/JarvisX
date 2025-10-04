/**
 * Screen Capture Service for JarvisX PC Agent
 * Handles screen capture for WebRTC streaming
 */

import { EventEmitter } from 'events';

export interface ScreenCaptureOptions {
  width?: number;
  height?: number;
  frameRate?: number;
  quality?: number;
  audio?: boolean;
}

export interface ScreenCaptureSession {
  id: string;
  stream: MediaStream | null;
  options: ScreenCaptureOptions;
  startTime: Date;
  status: 'starting' | 'active' | 'stopped' | 'error';
}

export class ScreenCaptureService extends EventEmitter {
  private sessions: Map<string, ScreenCaptureSession> = new Map();
  private isAvailable: boolean = false;
  private defaultOptions: ScreenCaptureOptions = {
    width: 1920,
    height: 1080,
    frameRate: 30,
    quality: 0.8,
    audio: false
  };

  constructor() {
    super();
    this.checkAvailability();
  }

  private async checkAvailability(): Promise<void> {
    try {
      // Check if getDisplayMedia is available
      if (typeof navigator !== 'undefined' && navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {
        this.isAvailable = true;
        console.log('✅ Screen capture is available via getDisplayMedia');
      } else {
        // Check for alternative screen capture methods
        this.isAvailable = await this.checkAlternativeMethods();
      }
    } catch (error) {
      console.warn('⚠️ Screen capture not available:', error);
      this.isAvailable = false;
    }
  }

  private async checkAlternativeMethods(): Promise<boolean> {
    // For Node.js environment, we might use alternative methods
    // like electron's desktopCapturer or third-party libraries
    try {
      // This would be implemented based on the platform
      // For now, return false as we're primarily targeting web environments
      return false;
    } catch (error) {
      return false;
    }
  }

  public isAvailable(): boolean {
    return this.isAvailable;
  }

  public async startCapture(sessionId: string, options: ScreenCaptureOptions = {}): Promise<MediaStream> {
    try {
      console.log(`📺 Starting screen capture for session ${sessionId}`);

      const captureOptions = { ...this.defaultOptions, ...options };
      
      let stream: MediaStream;

      if (typeof navigator !== 'undefined' && navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {
        // Browser environment
        stream = await this.startBrowserCapture(captureOptions);
      } else {
        // Node.js environment - use alternative methods
        stream = await this.startNodeCapture(sessionId, captureOptions);
      }

      // Create session
      const session: ScreenCaptureSession = {
        id: sessionId,
        stream,
        options: captureOptions,
        startTime: new Date(),
        status: 'active'
      };

      this.sessions.set(sessionId, session);

      // Set up stream event handlers
      stream.getVideoTracks().forEach(track => {
        track.onended = () => {
          console.log(`📺 Video track ended for session ${sessionId}`);
          this.stopCapture(sessionId);
        };
      });

      if (stream.getAudioTracks().length > 0) {
        stream.getAudioTracks().forEach(track => {
          track.onended = () => {
            console.log(`📺 Audio track ended for session ${sessionId}`);
          };
        });
      }

      console.log(`✅ Screen capture started for session ${sessionId}`);
      this.emit('captureStarted', { sessionId, stream });

      return stream;

    } catch (error: any) {
      console.error(`❌ Failed to start screen capture for session ${sessionId}:`, error);
      
      // Update session status to error
      const session = this.sessions.get(sessionId);
      if (session) {
        session.status = 'error';
      }

      throw error;
    }
  }

  private async startBrowserCapture(options: ScreenCaptureOptions): Promise<MediaStream> {
    const constraints: MediaStreamConstraints = {
      video: {
        width: { ideal: options.width },
        height: { ideal: options.height },
        frameRate: { ideal: options.frameRate }
      },
      audio: options.audio || false
    };

    try {
      const stream = await navigator.mediaDevices.getDisplayMedia(constraints);
      return stream;
    } catch (error: any) {
      if (error.name === 'NotAllowedError') {
        throw new Error('Screen capture permission denied');
      } else if (error.name === 'NotFoundError') {
        throw new Error('No screen capture sources available');
      } else {
        throw new Error(`Screen capture failed: ${error.message}`);
      }
    }
  }

  private async startNodeCapture(sessionId: string, options: ScreenCaptureOptions): Promise<MediaStream> {
    // For Node.js environment, we would implement screen capture using:
    // - electron's desktopCapturer
    // - robotjs for screen capture
    // - ffmpeg for screen recording
    // - or other platform-specific libraries
    
    throw new Error('Screen capture not implemented for Node.js environment');
  }

  public async stopCapture(sessionId: string): Promise<void> {
    try {
      console.log(`🛑 Stopping screen capture for session ${sessionId}`);

      const session = this.sessions.get(sessionId);
      if (!session) {
        console.warn(`⚠️ Session ${sessionId} not found for stop capture`);
        return;
      }

      // Stop all tracks
      if (session.stream) {
        session.stream.getTracks().forEach(track => {
          track.stop();
        });
      }

      // Update session status
      session.status = 'stopped';
      session.stream = null;

      // Remove session
      this.sessions.delete(sessionId);

      console.log(`✅ Screen capture stopped for session ${sessionId}`);
      this.emit('captureStopped', { sessionId });

    } catch (error) {
      console.error(`❌ Failed to stop screen capture for session ${sessionId}:`, error);
      throw error;
    }
  }

  public getSession(sessionId: string): ScreenCaptureSession | undefined {
    return this.sessions.get(sessionId);
  }

  public getActiveSessions(): ScreenCaptureSession[] {
    return Array.from(this.sessions.values()).filter(session => session.status === 'active');
  }

  public getSessionStats(): any {
    const sessions = this.getActiveSessions();
    return {
      total: sessions.length,
      active: sessions.filter(s => s.status === 'active').length,
      stopped: sessions.filter(s => s.status === 'stopped').length,
      error: sessions.filter(s => s.status === 'error').length
    };
  }

  public async getScreenInfo(): Promise<any> {
    try {
      if (typeof navigator !== 'undefined' && navigator.mediaDevices) {
        // Get available video input devices (screens)
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoInputs = devices.filter(device => device.kind === 'videoinput');
        
        return {
          available: true,
          devices: videoInputs,
          method: 'getDisplayMedia'
        };
      } else {
        return {
          available: false,
          method: 'node'
        };
      }
    } catch (error) {
      console.error('❌ Failed to get screen info:', error);
      return {
        available: false,
        error: error.message
      };
    }
  }

  public async captureScreenshot(sessionId: string): Promise<string> {
    try {
      const session = this.sessions.get(sessionId);
      if (!session || !session.stream) {
        throw new Error(`No active capture session ${sessionId}`);
      }

      // Create canvas and draw video frame
      const video = document.createElement('video');
      video.srcObject = session.stream;
      video.play();

      return new Promise((resolve, reject) => {
        video.onloadedmetadata = () => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          
          if (!ctx) {
            reject(new Error('Failed to get canvas context'));
            return;
          }

          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          
          ctx.drawImage(video, 0, 0);
          
          const dataUrl = canvas.toDataURL('image/png');
          resolve(dataUrl);
        };

        video.onerror = (error) => {
          reject(error);
        };
      });

    } catch (error) {
      console.error(`❌ Failed to capture screenshot for session ${sessionId}:`, error);
      throw error;
    }
  }
}
