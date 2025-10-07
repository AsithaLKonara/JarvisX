/**
 * Lip Sync Engine - Real-time audio-to-viseme mapping
 * Analyzes audio and generates mouth movements for avatar
 */

import * as Tone from 'tone';

export interface VisemeData {
  viseme: string;
  timestamp: number;
  amplitude: number;
}

export interface LipSyncConfig {
  smoothing: number;
  sensitivity: number;
  sampleRate: number;
}

/**
 * Viseme phonemes mapping (based on standard lip-sync phonemes)
 */
const VISEME_MAP: { [key: string]: number } = {
  'sil': 0,    // Silence
  'PP': 0.2,   // P, B, M
  'FF': 0.3,   // F, V
  'TH': 0.4,   // TH
  'DD': 0.5,   // T, D
  'kk': 0.6,   // K, G
  'CH': 0.7,   // CH, J, SH
  'SS': 0.5,   // S, Z
  'nn': 0.4,   // N, NG
  'RR': 0.6,   // R
  'aa': 0.8,   // AH, AE
  'E': 0.6,    // EH, AY
  'I': 0.4,    // IH, IY
  'O': 0.7,    // OH, AO
  'U': 0.5,    // UH, UW
};

export class LipSyncEngine {
  private analyzer: Tone.Analyser | null = null;
  private waveform: Tone.Waveform | null = null;
  private fft: Tone.FFT | null = null;
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private isActive: boolean = false;
  private lipSyncData: number[] = [];
  private config: LipSyncConfig;
  private smoothingBuffer: number[] = [];

  constructor(config: Partial<LipSyncConfig> = {}) {
    this.config = {
      smoothing: config.smoothing || 0.3,
      sensitivity: config.sensitivity || 1.5,
      sampleRate: config.sampleRate || 30, // 30 FPS
    };
  }

  /**
   * Initialize the lip sync engine
   */
  async initialize(): Promise<void> {
    try {
      await Tone.start();
      
      // Create audio analyzers
      this.analyzer = new Tone.Analyser('waveform', 256);
      this.waveform = new Tone.Waveform(256);
      this.fft = new Tone.FFT(256);

      console.log('✅ Lip Sync Engine initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Lip Sync Engine:', error);
      throw error;
    }
  }

  /**
   * Start analyzing audio from microphone
   */
  async startFromMicrophone(): Promise<void> {
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const source = Tone.context.createMediaStreamSource(this.mediaStream);
      const toneSource = Tone.context.createMediaStreamSource(this.mediaStream) as any;
      
      if (this.analyzer) {
        toneSource.connect(this.analyzer);
      }
      
      this.isActive = true;
      this.startProcessing();
      
      console.log('✅ Lip sync started from microphone');
    } catch (error) {
      console.error('❌ Failed to start microphone:', error);
      throw error;
    }
  }

  /**
   * Analyze audio buffer (for pre-recorded speech)
   */
  analyzeAudioBuffer(audioBuffer: AudioBuffer): number[] {
    const channelData = audioBuffer.getChannelData(0);
    const lipSyncData: number[] = [];
    const samplesPerFrame = Math.floor(audioBuffer.sampleRate / this.config.sampleRate);

    for (let i = 0; i < channelData.length; i += samplesPerFrame) {
      const frame = channelData.slice(i, i + samplesPerFrame);
      const amplitude = this.calculateAmplitude(frame);
      const viseme = this.amplitudeToViseme(amplitude);
      lipSyncData.push(viseme);
    }

    return this.smoothLipSyncData(lipSyncData);
  }

  /**
   * Analyze audio from URL (for TTS output)
   */
  async analyzeAudioFromUrl(audioUrl: string): Promise<number[]> {
    try {
      const response = await fetch(audioUrl);
      const arrayBuffer = await response.arrayBuffer();
      
      if (!this.audioContext) {
        this.audioContext = new AudioContext();
      }
      
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      return this.analyzeAudioBuffer(audioBuffer);
    } catch (error) {
      console.error('❌ Failed to analyze audio from URL:', error);
      return [];
    }
  }

  /**
   * Analyze audio from base64 data
   */
  async analyzeAudioFromBase64(base64Audio: string): Promise<number[]> {
    try {
      // Convert base64 to array buffer
      const binaryString = atob(base64Audio);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      if (!this.audioContext) {
        this.audioContext = new AudioContext();
      }
      
      const audioBuffer = await this.audioContext.decodeAudioData(bytes.buffer);
      return this.analyzeAudioBuffer(audioBuffer);
    } catch (error) {
      console.error('❌ Failed to analyze audio from base64:', error);
      return [];
    }
  }

  /**
   * Start real-time processing
   */
  private startProcessing(): void {
    const process = () => {
      if (!this.isActive || !this.analyzer) return;

      const waveformData = this.analyzer.getValue();
      
      if (Array.isArray(waveformData)) {
        const amplitude = this.calculateAmplitude(waveformData);
        const viseme = this.amplitudeToViseme(amplitude);
        
        // Add to lip sync data buffer
        this.lipSyncData.push(viseme);
        
        // Keep buffer size manageable (last 2 seconds)
        if (this.lipSyncData.length > this.config.sampleRate * 2) {
          this.lipSyncData.shift();
        }
      }

      // Continue processing
      if (this.isActive) {
        setTimeout(process, 1000 / this.config.sampleRate);
      }
    };

    process();
  }

  /**
   * Calculate amplitude from waveform data
   */
  private calculateAmplitude(data: ArrayLike<number>): number {
    let sum = 0;
    for (let i = 0; i < data.length; i++) {
      sum += Math.abs(data[i]);
    }
    return (sum / data.length) * this.config.sensitivity;
  }

  /**
   * Convert amplitude to viseme value (0-1)
   */
  private amplitudeToViseme(amplitude: number): number {
    // Map amplitude to mouth openness
    // This is a simplified version - in production, you'd use phoneme detection
    
    if (amplitude < 0.01) return 0; // Silence
    if (amplitude < 0.05) return 0.2; // Closed sounds (M, P, B)
    if (amplitude < 0.1) return 0.4; // Medium sounds (N, T, D)
    if (amplitude < 0.2) return 0.6; // Open sounds (E, I)
    if (amplitude < 0.4) return 0.8; // Very open sounds (A, O)
    return 1.0; // Maximum opening
  }

  /**
   * Smooth lip sync data using moving average
   */
  private smoothLipSyncData(data: number[]): number[] {
    const windowSize = Math.max(1, Math.floor(this.config.smoothing * 10));
    const smoothed: number[] = [];

    for (let i = 0; i < data.length; i++) {
      const start = Math.max(0, i - windowSize);
      const end = Math.min(data.length, i + windowSize + 1);
      const window = data.slice(start, end);
      const avg = window.reduce((a, b) => a + b, 0) / window.length;
      smoothed.push(avg);
    }

    return smoothed;
  }

  /**
   * Get current lip sync data
   */
  getLipSyncData(): number[] {
    return [...this.lipSyncData];
  }

  /**
   * Get real-time viseme value
   */
  getCurrentViseme(): number {
    return this.lipSyncData[this.lipSyncData.length - 1] || 0;
  }

  /**
   * Stop lip sync processing
   */
  stop(): void {
    this.isActive = false;
    
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
    
    this.lipSyncData = [];
    console.log('🛑 Lip sync stopped');
  }

  /**
   * Clean up resources
   */
  dispose(): void {
    this.stop();
    
    if (this.analyzer) {
      this.analyzer.dispose();
      this.analyzer = null;
    }
    
    if (this.waveform) {
      this.waveform.dispose();
      this.waveform = null;
    }
    
    if (this.fft) {
      this.fft.dispose();
      this.fft = null;
    }
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    console.log('🧹 Lip sync engine disposed');
  }
}

/**
 * Helper function to create lip sync data from text
 * (Simple phoneme estimation - in production, use proper TTS phoneme output)
 */
export function estimateLipSyncFromText(text: string, duration: number): number[] {
  const words = text.split(' ');
  const framesPerSecond = 30;
  const totalFrames = Math.floor(duration * framesPerSecond);
  const framesPerWord = totalFrames / words.length;
  
  const lipSyncData: number[] = [];
  
  words.forEach((word, wordIndex) => {
    const wordFrames = Math.floor(framesPerWord);
    
    for (let i = 0; i < wordFrames; i++) {
      const progress = i / wordFrames;
      
      // Create natural-looking mouth movement pattern
      let viseme = 0;
      
      if (progress < 0.2) {
        // Opening
        viseme = progress * 5 * 0.7;
      } else if (progress < 0.7) {
        // Sustained
        viseme = 0.4 + Math.sin(progress * Math.PI * 4) * 0.3;
      } else {
        // Closing
        viseme = (1 - progress) * 3 * 0.7;
      }
      
      // Add some randomness for natural variation
      viseme += (Math.random() - 0.5) * 0.1;
      viseme = Math.max(0, Math.min(1, viseme));
      
      lipSyncData.push(viseme);
    }
    
    // Add brief pause between words
    for (let i = 0; i < 3; i++) {
      lipSyncData.push(0);
    }
  });
  
  return lipSyncData;
}

export default LipSyncEngine;

