/**
 * Lip Sync Processor
 * Server-side audio processing for lip-sync generation
 */

export interface LipSyncFrame {
  timestamp: number;
  viseme: string;
  amplitude: number;
  mouthOpenness: number;
}

export class LipSyncProcessor {
  private fps: number = 30;

  constructor() {}

  /**
   * Process audio data (base64) and generate lip-sync data
   */
  async processAudioData(audioDataBase64: string): Promise<number[]> {
    try {
      // Decode base64 audio
      const audioBuffer = Buffer.from(audioDataBase64, 'base64');
      
      // In production, you would use proper audio analysis here
      // For now, we'll use a simplified amplitude-based approach
      return this.analyzeAudioBuffer(audioBuffer);
    } catch (error) {
      console.error('❌ Failed to process audio data:', error);
      throw error;
    }
  }

  /**
   * Process audio from URL
   */
  async processAudioUrl(audioUrl: string): Promise<number[]> {
    try {
      const fetch = (await import('node-fetch')).default;
      const response = await fetch(audioUrl);
      const arrayBuffer = await response.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);
      
      return this.analyzeAudioBuffer(buffer);
    } catch (error) {
      console.error('❌ Failed to process audio from URL:', error);
      throw error;
    }
  }

  /**
   * Analyze audio buffer and extract amplitude-based mouth movements
   */
  private analyzeAudioBuffer(buffer: Buffer): number[] {
    const lipSyncData: number[] = [];
    const sampleSize = Math.floor(buffer.length / (this.fps * 3)); // Assuming 3-second audio
    
    for (let i = 0; i < buffer.length; i += sampleSize) {
      const chunk = buffer.slice(i, i + sampleSize);
      const amplitude = this.calculateAmplitude(chunk);
      const mouthOpenness = this.amplitudeToMouthOpenness(amplitude);
      lipSyncData.push(mouthOpenness);
    }

    // Smooth the lip-sync data
    return this.smoothLipSyncData(lipSyncData);
  }

  /**
   * Calculate amplitude from audio chunk
   */
  private calculateAmplitude(chunk: Buffer): number {
    let sum = 0;
    for (let i = 0; i < chunk.length; i++) {
      // Convert byte to signed value
      const value = chunk[i] > 127 ? chunk[i] - 256 : chunk[i];
      sum += Math.abs(value);
    }
    return sum / chunk.length / 128; // Normalize to 0-1
  }

  /**
   * Convert amplitude to mouth openness (0-1)
   */
  private amplitudeToMouthOpenness(amplitude: number): number {
    // Apply non-linear mapping for more natural mouth movement
    if (amplitude < 0.05) return 0; // Silence
    if (amplitude < 0.1) return 0.2;
    if (amplitude < 0.2) return 0.4;
    if (amplitude < 0.3) return 0.6;
    if (amplitude < 0.5) return 0.8;
    return 1.0;
  }

  /**
   * Smooth lip-sync data using moving average
   */
  private smoothLipSyncData(data: number[]): number[] {
    const windowSize = 3;
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
   * Estimate lip-sync from text (fallback method)
   */
  estimateFromText(text: string, duration: number): number[] {
    const words = text.split(/\s+/).filter(w => w.length > 0);
    const totalFrames = Math.floor(duration * this.fps);
    const framesPerWord = totalFrames / words.length;
    
    const lipSyncData: number[] = [];
    
    words.forEach((word) => {
      const wordFrames = Math.floor(framesPerWord);
      
      // Estimate phoneme complexity based on word length and vowels
      const vowelCount = (word.match(/[aeiou]/gi) || []).length;
      const baseOpenness = Math.min(0.8, 0.3 + vowelCount * 0.15);
      
      for (let i = 0; i < wordFrames; i++) {
        const progress = i / wordFrames;
        
        // Create natural mouth movement pattern
        let mouthOpenness = 0;
        
        if (progress < 0.2) {
          // Opening
          mouthOpenness = progress * 5 * baseOpenness;
        } else if (progress < 0.7) {
          // Sustained with variation
          mouthOpenness = baseOpenness * (0.7 + Math.sin(progress * Math.PI * 6) * 0.3);
        } else {
          // Closing
          mouthOpenness = (1 - progress) * 3.33 * baseOpenness;
        }
        
        // Add natural variation
        mouthOpenness += (Math.random() - 0.5) * 0.1;
        mouthOpenness = Math.max(0, Math.min(1, mouthOpenness));
        
        lipSyncData.push(mouthOpenness);
      }
      
      // Add brief pause between words
      for (let i = 0; i < 2; i++) {
        lipSyncData.push(0);
      }
    });
    
    // Ensure we have the correct number of frames
    while (lipSyncData.length < totalFrames) {
      lipSyncData.push(0);
    }
    
    return lipSyncData.slice(0, totalFrames);
  }

  /**
   * Convert phoneme to viseme
   * Based on standard viseme mapping
   */
  private phonemeToViseme(phoneme: string): string {
    const phonemeMap: { [key: string]: string } = {
      // Consonants
      'p': 'PP', 'b': 'PP', 'm': 'PP',
      'f': 'FF', 'v': 'FF',
      'th': 'TH', 'dh': 'TH',
      't': 'DD', 'd': 'DD', 'n': 'nn', 'l': 'DD',
      'k': 'kk', 'g': 'kk', 'ng': 'kk',
      's': 'SS', 'z': 'SS',
      'sh': 'CH', 'zh': 'CH', 'ch': 'CH', 'jh': 'CH',
      'r': 'RR',
      // Vowels
      'aa': 'aa', 'ae': 'aa', 'ah': 'aa',
      'eh': 'E', 'ey': 'E',
      'ih': 'I', 'iy': 'I',
      'oh': 'O', 'ow': 'O', 'ao': 'O',
      'uh': 'U', 'uw': 'U',
      // Silence
      'sil': 'sil', 'sp': 'sil'
    };

    return phonemeMap[phoneme.toLowerCase()] || 'sil';
  }

  /**
   * Generate detailed lip-sync frames (for advanced usage)
   */
  generateDetailedFrames(text: string, duration: number): LipSyncFrame[] {
    const lipSyncData = this.estimateFromText(text, duration);
    const frames: LipSyncFrame[] = [];

    lipSyncData.forEach((mouthOpenness, index) => {
      const timestamp = index / this.fps;
      
      frames.push({
        timestamp,
        viseme: this.opennessToViseme(mouthOpenness),
        amplitude: mouthOpenness,
        mouthOpenness
      });
    });

    return frames;
  }

  /**
   * Convert mouth openness to approximate viseme
   */
  private opennessToViseme(openness: number): string {
    if (openness < 0.1) return 'sil';
    if (openness < 0.3) return 'PP';
    if (openness < 0.5) return 'E';
    if (openness < 0.7) return 'O';
    return 'aa';
  }
}

export default LipSyncProcessor;

