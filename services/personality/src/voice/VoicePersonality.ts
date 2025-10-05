/**
 * Voice Personality - Makes JarvisX sound truly human with emotional speech
 */

import { EventEmitter } from 'events';
import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';

export interface VoiceConfig {
  language: 'en' | 'si' | 'mixed';
  gender: 'male' | 'female' | 'neutral';
  age: 'young' | 'middle' | 'mature';
  accent: 'american' | 'british' | 'australian' | 'sinhala' | 'neutral';
  speed: number;          // 0.5 - 2.0
  pitch: number;          // 0.5 - 2.0
  volume: number;         // 0.0 - 1.0
  emotion: string;
}

export interface SpeechRequest {
  text: string;
  emotion: string;
  speed?: number;
  pitch?: number;
  language?: string;
  context?: any;
}

export interface SpeechResponse {
  audioBuffer: Buffer;
  duration: number;
  wordCount: number;
  emotion: string;
  language: string;
  quality: number;
}

export class VoicePersonality extends EventEmitter {
  private emotionalEngine: any;
  private voiceConfig: VoiceConfig;
  private voiceProfiles: Map<string, VoiceConfig>;
  private speechCache: Map<string, Buffer>;
  private audioEffects: Map<string, (audio: Buffer) => Buffer>;
  private currentVoice: string;
  private googleTtsApiKey: string;
  private elevenLabsApiKey: string;

  constructor() {
    super();
    this.voiceConfig = this.getDefaultVoiceConfig();
    this.voiceProfiles = new Map();
    this.speechCache = new Map();
    this.audioEffects = new Map();
    this.currentVoice = 'default';
    this.googleTtsApiKey = process.env.GOOGLE_TTS_API_KEY || '';
    this.elevenLabsApiKey = process.env.ELEVENLABS_API_KEY || '';
    
    this.initializeVoiceProfiles();
    this.initializeAudioEffects();
  }

  private getDefaultVoiceConfig(): VoiceConfig {
    return {
      language: 'en',
      gender: 'male',
      age: 'middle',
      accent: 'neutral',
      speed: 1.0,
      pitch: 1.0,
      volume: 0.8,
      emotion: 'neutral'
    };
  }

  private initializeVoiceProfiles(): void {
    // Default professional voice
    this.voiceProfiles.set('default', {
      language: 'en',
      gender: 'male',
      age: 'middle',
      accent: 'neutral',
      speed: 1.0,
      pitch: 1.0,
      volume: 0.8,
      emotion: 'neutral'
    });

    // Enthusiastic voice for exciting moments
    this.voiceProfiles.set('enthusiastic', {
      language: 'en',
      gender: 'male',
      age: 'middle',
      accent: 'neutral',
      speed: 1.2,
      pitch: 1.1,
      volume: 0.9,
      emotion: 'excited'
    });

    // Calm voice for reassurance
    this.voiceProfiles.set('calm', {
      language: 'en',
      gender: 'male',
      age: 'middle',
      accent: 'neutral',
      speed: 0.9,
      pitch: 0.95,
      volume: 0.7,
      emotion: 'calm'
    });

    // Sinhala voice
    this.voiceProfiles.set('sinhala', {
      language: 'si',
      gender: 'male',
      age: 'middle',
      accent: 'sinhala',
      speed: 1.0,
      pitch: 1.0,
      volume: 0.8,
      emotion: 'neutral'
    });

    // Concerned voice for problems
    this.voiceProfiles.set('concerned', {
      language: 'en',
      gender: 'male',
      age: 'middle',
      accent: 'neutral',
      speed: 0.95,
      pitch: 0.9,
      volume: 0.75,
      emotion: 'concerned'
    });

    // Proud voice for achievements
    this.voiceProfiles.set('proud', {
      language: 'en',
      gender: 'male',
      age: 'middle',
      accent: 'neutral',
      speed: 1.1,
      pitch: 1.05,
      volume: 0.85,
      emotion: 'proud'
    });

    // Grateful voice for thanks
    this.voiceProfiles.set('grateful', {
      language: 'en',
      gender: 'male',
      age: 'middle',
      accent: 'neutral',
      speed: 1.0,
      pitch: 1.02,
      volume: 0.8,
      emotion: 'grateful'
    });

    // Curious voice for questions
    this.voiceProfiles.set('curious', {
      language: 'en',
      gender: 'male',
      age: 'middle',
      accent: 'neutral',
      speed: 1.05,
      pitch: 1.08,
      volume: 0.8,
      emotion: 'curious'
    });
  }

  private initializeAudioEffects(): void {
    // Warm effect - adds slight reverb and warmth
    this.audioEffects.set('warm', (audio: Buffer) => {
      // Simulate warm effect (in real implementation, use audio processing)
      return audio;
    });

    // Clear effect - enhances clarity
    this.audioEffects.set('clear', (audio: Buffer) => {
      // Simulate clear effect
      return audio;
    });

    // Emotional effect - adds emotional coloring
    this.audioEffects.set('emotional', (audio: Buffer) => {
      // Simulate emotional effect
      return audio;
    });

    // Professional effect - clean and professional
    this.audioEffects.set('professional', (audio: Buffer) => {
      // Simulate professional effect
      return audio;
    });
  }

  public setEmotionalEngine(emotionalEngine: any): void {
    this.emotionalEngine = emotionalEngine;
  }

  public async synthesizeSpeech(request: SpeechRequest): Promise<SpeechResponse> {
    const { text, emotion, speed, pitch, language, context } = request;
    
    // Determine voice profile based on emotion
    const voiceProfile = this.getVoiceProfileForEmotion(emotion);
    
    // Apply speed and pitch overrides
    const finalConfig = {
      ...voiceProfile,
      speed: speed || voiceProfile.speed,
      pitch: pitch || voiceProfile.pitch,
      language: language || voiceProfile.language
    };

    // Check cache first
    const cacheKey = this.generateCacheKey(text, finalConfig);
    const cachedAudio = this.speechCache.get(cacheKey);
    if (cachedAudio) {
      console.log('🎵 Using cached speech');
      return {
        audioBuffer: cachedAudio,
        duration: this.estimateDuration(text, finalConfig.speed),
        wordCount: text.split(' ').length,
        emotion,
        language: finalConfig.language,
        quality: 0.9
      };
    }

    try {
      // Synthesize speech using available TTS service
      let audioBuffer: Buffer;
      
      if (this.elevenLabsApiKey) {
        audioBuffer = await this.synthesizeWithElevenLabs(text, finalConfig);
      } else if (this.googleTtsApiKey) {
        audioBuffer = await this.synthesizeWithGoogleTTS(text, finalConfig);
      } else {
        // Fallback to simple TTS
        audioBuffer = await this.synthesizeWithFallback(text, finalConfig);
      }

      // Apply audio effects based on emotion
      audioBuffer = this.applyAudioEffects(audioBuffer, emotion);

      // Cache the result
      this.speechCache.set(cacheKey, audioBuffer);

      // Estimate duration
      const duration = this.estimateDuration(text, finalConfig.speed);
      const wordCount = text.split(' ').length;

      const response: SpeechResponse = {
        audioBuffer,
        duration,
        wordCount,
        emotion,
        language: finalConfig.language,
        quality: this.calculateQuality(finalConfig, emotion)
      };

      this.emit('speechSynthesized', response);
      console.log(`🎵 Speech synthesized: "${text.substring(0, 50)}..." (${emotion}, ${finalConfig.language})`);

      return response;

    } catch (error) {
      console.error('❌ Speech synthesis failed:', error);
      throw new Error(`Speech synthesis failed: ${error.message}`);
    }
  }

  private getVoiceProfileForEmotion(emotion: string): VoiceConfig {
    // Map emotions to voice profiles
    const emotionToProfile: { [key: string]: string } = {
      'happy': 'enthusiastic',
      'excited': 'enthusiastic',
      'proud': 'proud',
      'grateful': 'grateful',
      'curious': 'curious',
      'concerned': 'concerned',
      'calm': 'calm',
      'neutral': 'default',
      'professional': 'default'
    };

    const profileName = emotionToProfile[emotion] || 'default';
    return this.voiceProfiles.get(profileName) || this.getDefaultVoiceConfig();
  }

  private async synthesizeWithElevenLabs(text: string, config: VoiceConfig): Promise<Buffer> {
    // ElevenLabs provides high-quality, emotional TTS
    const response = await axios.post('https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB', {
      text,
      model_id: 'eleven_monolingual_v1',
      voice_settings: {
        stability: 0.5,
        similarity_boost: 0.5,
        style: this.mapEmotionToElevenLabsStyle(config.emotion),
        use_speaker_boost: true
      }
    }, {
      headers: {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': this.elevenLabsApiKey
      },
      responseType: 'arraybuffer'
    });

    return Buffer.from(response.data);
  }

  private async synthesizeWithGoogleTTS(text: string, config: VoiceConfig): Promise<Buffer> {
    // Google Cloud TTS
    const response = await axios.post(`https://texttospeech.googleapis.com/v1/text:synthesize?key=${this.googleTtsApiKey}`, {
      input: { text },
      voice: {
        languageCode: config.language === 'si' ? 'si-LK' : 'en-US',
        name: this.getGoogleVoiceName(config),
        ssmlGender: config.gender.toUpperCase()
      },
      audioConfig: {
        audioEncoding: 'MP3',
        speakingRate: config.speed,
        pitch: config.pitch,
        volumeGainDb: this.volumeToDb(config.volume)
      }
    });

    return Buffer.from(response.data.audioContent, 'base64');
  }

  private async synthesizeWithFallback(text: string, config: VoiceConfig): Promise<Buffer> {
    // Simple fallback TTS (could use Festival or espeak)
    console.log('🎵 Using fallback TTS');
    
    // Create a simple audio file with metadata
    const audioData = this.createSimpleAudioFile(text, config);
    return audioData;
  }

  private createSimpleAudioFile(text: string, config: VoiceConfig): Buffer {
    // This is a placeholder - in real implementation, use actual TTS
    const duration = this.estimateDuration(text, config.speed);
    const sampleRate = 22050;
    const samples = Math.floor(duration * sampleRate);
    
    // Create a simple sine wave as placeholder
    const audioBuffer = Buffer.alloc(samples * 2); // 16-bit samples
    
    for (let i = 0; i < samples; i++) {
      const sample = Math.sin(2 * Math.PI * 440 * i / sampleRate) * 0.1; // 440Hz tone
      const intSample = Math.round(sample * 32767);
      audioBuffer.writeInt16LE(intSample, i * 2);
    }
    
    return audioBuffer;
  }

  private applyAudioEffects(audio: Buffer, emotion: string): Buffer {
    const effect = this.getAudioEffectForEmotion(emotion);
    const effectFunction = this.audioEffects.get(effect);
    
    if (effectFunction) {
      return effectFunction(audio);
    }
    
    return audio;
  }

  private getAudioEffectForEmotion(emotion: string): string {
    const emotionEffects: { [key: string]: string } = {
      'happy': 'warm',
      'excited': 'clear',
      'proud': 'professional',
      'grateful': 'warm',
      'curious': 'clear',
      'concerned': 'emotional',
      'calm': 'clear',
      'neutral': 'professional'
    };
    
    return emotionEffects[emotion] || 'professional';
  }

  private mapEmotionToElevenLabsStyle(emotion: string): number {
    // ElevenLabs style parameter (0-1)
    const emotionStyles: { [key: string]: number } = {
      'neutral': 0.0,
      'happy': 0.3,
      'excited': 0.6,
      'concerned': 0.2,
      'proud': 0.4,
      'grateful': 0.3,
      'curious': 0.5,
      'calm': 0.1
    };
    
    return emotionStyles[emotion] || 0.0;
  }

  private getGoogleVoiceName(config: VoiceConfig): string {
    if (config.language === 'si') {
      return 'si-LK-Wavenet-A'; // Sinhala voice
    }
    
    const voiceNames: { [key: string]: string } = {
      'male': 'en-US-Wavenet-D',
      'female': 'en-US-Wavenet-C',
      'neutral': 'en-US-Wavenet-D'
    };
    
    return voiceNames[config.gender] || 'en-US-Wavenet-D';
  }

  private volumeToDb(volume: number): number {
    // Convert volume (0-1) to dB gain (-96 to 16)
    return 20 * Math.log10(volume);
  }

  private estimateDuration(text: string, speed: number): number {
    // Estimate speech duration based on text length and speed
    const wordsPerMinute = 150; // Average speaking rate
    const wordCount = text.split(' ').length;
    const baseDuration = (wordCount / wordsPerMinute) * 60; // seconds
    return baseDuration / speed;
  }

  private calculateQuality(config: VoiceConfig, emotion: string): number {
    let quality = 0.8; // Base quality
    
    // Adjust quality based on emotion matching
    const emotionMatch = this.getEmotionMatchScore(emotion, config.emotion);
    quality += emotionMatch * 0.2;
    
    // Adjust quality based on configuration
    if (config.speed > 0.8 && config.speed < 1.2) quality += 0.1;
    if (config.pitch > 0.9 && config.pitch < 1.1) quality += 0.1;
    
    return Math.min(1.0, quality);
  }

  private getEmotionMatchScore(targetEmotion: string, voiceEmotion: string): number {
    if (targetEmotion === voiceEmotion) return 1.0;
    
    // Similar emotions get partial score
    const emotionSimilarity: { [key: string]: string[] } = {
      'happy': ['excited', 'proud', 'grateful'],
      'excited': ['happy', 'curious'],
      'concerned': ['calm', 'neutral'],
      'proud': ['happy', 'grateful'],
      'grateful': ['happy', 'proud'],
      'curious': ['excited', 'neutral']
    };
    
    const similar = emotionSimilarity[targetEmotion] || [];
    return similar.includes(voiceEmotion) ? 0.7 : 0.3;
  }

  private generateCacheKey(text: string, config: VoiceConfig): string {
    const key = `${text}_${JSON.stringify(config)}`;
    return Buffer.from(key).toString('base64').substring(0, 32);
  }

  public setVoiceProfile(name: string, config: VoiceConfig): void {
    this.voiceProfiles.set(name, config);
    console.log(`🎵 Voice profile '${name}' updated`);
  }

  public getVoiceProfile(name: string): VoiceConfig | undefined {
    return this.voiceProfiles.get(name);
  }

  public getAllVoiceProfiles(): { [key: string]: VoiceConfig } {
    return Object.fromEntries(this.voiceProfiles);
  }

  public setCurrentVoice(name: string): void {
    if (this.voiceProfiles.has(name)) {
      this.currentVoice = name;
      this.voiceConfig = this.voiceProfiles.get(name)!;
      console.log(`🎵 Current voice set to: ${name}`);
    } else {
      console.warn(`🎵 Voice profile '${name}' not found`);
    }
  }

  public getCurrentVoice(): string {
    return this.currentVoice;
  }

  public async generateEmotionalSpeech(text: string, emotion: string): Promise<SpeechResponse> {
    // Get current emotional state if available
    let emotionalContext = { emotion };
    
    if (this.emotionalEngine) {
      const emotionalState = this.emotionalEngine.getEmotionalState();
      emotionalContext = {
        emotion,
        intensity: this.getEmotionIntensity(emotionalState, emotion),
        context: emotionalState
      };
    }
    
    return this.synthesizeSpeech({
      text,
      emotion,
      context: emotionalContext
    });
  }

  private getEmotionIntensity(emotionalState: any, emotion: string): number {
    const emotionKey = emotion as keyof typeof emotionalState;
    return emotionalState[emotionKey] || 50;
  }

  public async generateSinhalaSpeech(text: string, emotion: string = 'neutral'): Promise<SpeechResponse> {
    return this.synthesizeSpeech({
      text,
      emotion,
      language: 'si'
    });
  }

  public async generateMixedLanguageSpeech(text: string, emotion: string = 'neutral'): Promise<SpeechResponse> {
    // Detect language and adjust voice accordingly
    const hasSinhala = /[\u0D80-\u0DFF]/.test(text);
    const hasEnglish = /[a-zA-Z]/.test(text);
    
    let language = 'en';
    if (hasSinhala && hasEnglish) {
      language = 'mixed';
    } else if (hasSinhala) {
      language = 'si';
    }
    
    return this.synthesizeSpeech({
      text,
      emotion,
      language
    });
  }

  public clearCache(): void {
    this.speechCache.clear();
    console.log('🎵 Speech cache cleared');
  }

  public getCacheStats(): any {
    return {
      cacheSize: this.speechCache.size,
      cacheKeys: Array.from(this.speechCache.keys()),
      estimatedSize: this.estimateCacheSize()
    };
  }

  private estimateCacheSize(): number {
    // Rough estimate of cache size in bytes
    let totalSize = 0;
    this.speechCache.forEach(buffer => {
      totalSize += buffer.length;
    });
    return totalSize;
  }

  public async generateVoicePreview(emotion: string): Promise<SpeechResponse> {
    const previewTexts: { [key: string]: string } = {
      'happy': "Hello! I'm feeling great today!",
      'excited': "This is so exciting! Let's do this!",
      'concerned': "I want to make sure we handle this carefully.",
      'proud': "I'm proud of what we've accomplished together.",
      'grateful': "Thank you so much! I really appreciate that.",
      'curious': "That's really interesting! Tell me more.",
      'calm': "Everything is going to be just fine.",
      'neutral': "I'm here and ready to help you."
    };
    
    const text = previewTexts[emotion] || previewTexts['neutral'];
    return this.generateEmotionalSpeech(text, emotion);
  }
}
