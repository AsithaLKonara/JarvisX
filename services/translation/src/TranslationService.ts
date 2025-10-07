/**
 * Translation Service
 * Multi-language translation and localization
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

export interface TranslationRequest {
  id: string;
  text: string;
  sourceLanguage: string;
  targetLanguage: string;
  context?: string;
  domain?: string;
  timestamp: number;
  userId?: string;
}

export interface TranslationResult {
  id: string;
  originalText: string;
  translatedText: string;
  sourceLanguage: string;
  targetLanguage: string;
  confidence: number;
  provider: string;
  timestamp: number;
  duration: number;
  alternatives?: string[];
}

export interface LanguageInfo {
  code: string;
  name: string;
  nativeName: string;
  region: string;
  supported: boolean;
}

export interface TranslationStats {
  totalTranslations: number;
  languagesUsed: string[];
  averageConfidence: number;
  averageDuration: number;
  topLanguages: { language: string; count: number }[];
  recentTranslations: TranslationResult[];
}

export class TranslationService extends EventEmitter {
  private static instance: TranslationService;
  private supportedLanguages: LanguageInfo[] = [];
  private translationHistory: TranslationResult[] = [];
  private stats: TranslationStats;
  private isInitialized: boolean = false;

  private constructor() {
    super();
    this.stats = {
      totalTranslations: 0,
      languagesUsed: [],
      averageConfidence: 0,
      averageDuration: 0,
      topLanguages: [],
      recentTranslations: []
    };
  }

  public static getInstance(): TranslationService {
    if (!TranslationService.instance) {
      TranslationService.instance = new TranslationService();
    }
    return TranslationService.instance;
  }

  public async initialize(): Promise<void> {
    try {
      console.log('🌍 Initializing Translation Service...');
      
      // Load supported languages
      await this.loadSupportedLanguages();
      
      // Initialize translation providers
      await this.initializeTranslationProviders();
      
      this.isInitialized = true;
      console.log('✅ Translation Service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Translation Service:', error);
      throw error;
    }
  }

  private async loadSupportedLanguages(): Promise<void> {
    try {
      // Load supported languages from configuration
      this.supportedLanguages = [
        { code: 'en', name: 'English', nativeName: 'English', region: 'US', supported: true },
        { code: 'es', name: 'Spanish', nativeName: 'Español', region: 'ES', supported: true },
        { code: 'fr', name: 'French', nativeName: 'Français', region: 'FR', supported: true },
        { code: 'de', name: 'German', nativeName: 'Deutsch', region: 'DE', supported: true },
        { code: 'it', name: 'Italian', nativeName: 'Italiano', region: 'IT', supported: true },
        { code: 'pt', name: 'Portuguese', nativeName: 'Português', region: 'PT', supported: true },
        { code: 'ru', name: 'Russian', nativeName: 'Русский', region: 'RU', supported: true },
        { code: 'ja', name: 'Japanese', nativeName: '日本語', region: 'JP', supported: true },
        { code: 'ko', name: 'Korean', nativeName: '한국어', region: 'KR', supported: true },
        { code: 'zh', name: 'Chinese', nativeName: '中文', region: 'CN', supported: true },
        { code: 'ar', name: 'Arabic', nativeName: 'العربية', region: 'SA', supported: true },
        { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', region: 'IN', supported: true },
        { code: 'si', name: 'Sinhala', nativeName: 'සිංහල', region: 'LK', supported: true },
        { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', region: 'LK', supported: true }
      ];
      
      console.log(`✅ Loaded ${this.supportedLanguages.length} supported languages`);
    } catch (error) {
      console.error('❌ Failed to load supported languages:', error);
      throw error;
    }
  }

  private async initializeTranslationProviders(): Promise<void> {
    try {
      // Initialize translation providers
      console.log('🔧 Initializing translation providers...');
      
      // This would typically initialize various translation APIs
      // For now, we'll simulate the initialization
      console.log('✅ Translation providers initialized');
    } catch (error) {
      console.error('❌ Failed to initialize translation providers:', error);
      throw error;
    }
  }

  public async translate(request: TranslationRequest): Promise<TranslationResult> {
    try {
      const startTime = Date.now();
      
      // Validate request
      this.validateTranslationRequest(request);
      
      // Detect source language if not provided
      const sourceLanguage = request.sourceLanguage || await this.detectLanguage(request.text);
      
      // Perform translation
      const translationResult = await this.performTranslation(request.text, sourceLanguage, request.targetLanguage);
      
      const result: TranslationResult = {
        id: request.id,
        originalText: request.text,
        translatedText: translationResult.text,
        sourceLanguage: sourceLanguage,
        targetLanguage: request.targetLanguage,
        confidence: translationResult.confidence,
        provider: translationResult.provider,
        timestamp: Date.now(),
        duration: Date.now() - startTime,
        alternatives: translationResult.alternatives
      };
      
      // Store translation history
      this.translationHistory.unshift(result);
      this.translationHistory = this.translationHistory.slice(0, 1000); // Keep last 1000 translations
      
      // Update statistics
      this.updateStats(result);
      
      console.log(`🌍 Translated: "${request.text}" -> "${result.translatedText}"`);
      this.emit('translation_completed', result);
      
      return result;
    } catch (error) {
      console.error('❌ Translation failed:', error);
      throw error;
    }
  }

  private validateTranslationRequest(request: TranslationRequest): void {
    if (!request.text || request.text.trim().length === 0) {
      throw new Error('Text to translate is required');
    }
    
    if (!request.targetLanguage) {
      throw new Error('Target language is required');
    }
    
    if (request.text.length > 5000) {
      throw new Error('Text too long for translation');
    }
    
    // Check if target language is supported
    const targetLang = this.supportedLanguages.find(lang => lang.code === request.targetLanguage);
    if (!targetLang || !targetLang.supported) {
      throw new Error(`Target language ${request.targetLanguage} is not supported`);
    }
  }

  private async detectLanguage(text: string): Promise<string> {
    try {
      // Simple language detection based on character patterns
      // In a real implementation, this would use a proper language detection service
      
      const patterns = {
        'zh': /[\u4e00-\u9fff]/,
        'ja': /[\u3040-\u309f\u30a0-\u30ff]/,
        'ko': /[\uac00-\ud7af]/,
        'ar': /[\u0600-\u06ff]/,
        'hi': /[\u0900-\u097f]/,
        'si': /[\u0d80-\u0dff]/,
        'ta': /[\u0b80-\u0bff]/,
        'ru': /[\u0400-\u04ff]/,
        'es': /[ñáéíóúü]/i,
        'fr': /[àâäçéèêëïîôùûüÿ]/i,
        'de': /[äöüß]/i
      };
      
      for (const [lang, pattern] of Object.entries(patterns)) {
        if (pattern.test(text)) {
          return lang;
        }
      }
      
      // Default to English if no pattern matches
      return 'en';
    } catch (error) {
      console.error('❌ Language detection failed:', error);
      return 'en';
    }
  }

  private async performTranslation(text: string, sourceLanguage: string, targetLanguage: string): Promise<{
    text: string;
    confidence: number;
    provider: string;
    alternatives?: string[];
  }> {
    try {
      // Simulate translation using different providers
      const providers = ['google', 'microsoft', 'amazon', 'local'];
      const provider = providers[Math.floor(Math.random() * providers.length)];
      
      // Simulate translation result
      const translatedText = this.simulateTranslation(text, sourceLanguage, targetLanguage);
      const confidence = 0.7 + Math.random() * 0.3; // 0.7 to 1.0
      
      const alternatives = Math.random() > 0.5 ? [
        this.simulateTranslation(text, sourceLanguage, targetLanguage),
        this.simulateTranslation(text, sourceLanguage, targetLanguage)
      ] : undefined;
      
      return {
        text: translatedText,
        confidence,
        provider,
        alternatives
      };
    } catch (error) {
      console.error('❌ Translation execution failed:', error);
      throw error;
    }
  }

  private simulateTranslation(text: string, sourceLanguage: string, targetLanguage: string): string {
    // Simple simulation of translation
    // In a real implementation, this would call actual translation APIs
    
    const translations: { [key: string]: string } = {
      'hello': 'hola',
      'goodbye': 'adiós',
      'thank you': 'gracias',
      'yes': 'sí',
      'no': 'no',
      'please': 'por favor',
      'sorry': 'lo siento',
      'excuse me': 'disculpe',
      'how are you': '¿cómo estás?',
      'good morning': 'buenos días',
      'good evening': 'buenas tardes',
      'good night': 'buenas noches'
    };
    
    const lowerText = text.toLowerCase();
    const translation = translations[lowerText];
    
    if (translation) {
      return translation;
    }
    
    // If no direct translation, return a simulated translation
    return `[${targetLanguage.toUpperCase()}] ${text}`;
  }

  private updateStats(result: TranslationResult): void {
    this.stats.totalTranslations++;
    
    // Update languages used
    if (!this.stats.languagesUsed.includes(result.sourceLanguage)) {
      this.stats.languagesUsed.push(result.sourceLanguage);
    }
    if (!this.stats.languagesUsed.includes(result.targetLanguage)) {
      this.stats.languagesUsed.push(result.targetLanguage);
    }
    
    // Update average confidence
    this.stats.averageConfidence = 
      (this.stats.averageConfidence * (this.stats.totalTranslations - 1) + result.confidence) / 
      this.stats.totalTranslations;
    
    // Update average duration
    this.stats.averageDuration = 
      (this.stats.averageDuration * (this.stats.totalTranslations - 1) + result.duration) / 
      this.stats.totalTranslations;
    
    // Update top languages
    this.updateTopLanguages(result.targetLanguage);
    
    // Update recent translations
    this.stats.recentTranslations = this.translationHistory.slice(0, 10);
  }

  private updateTopLanguages(language: string): void {
    const existing = this.stats.topLanguages.find(item => item.language === language);
    if (existing) {
      existing.count++;
    } else {
      this.stats.topLanguages.push({ language, count: 1 });
    }
    
    // Sort by count and keep top 10
    this.stats.topLanguages.sort((a, b) => b.count - a.count);
    this.stats.topLanguages = this.stats.topLanguages.slice(0, 10);
  }

  public async batchTranslate(requests: TranslationRequest[]): Promise<TranslationResult[]> {
    try {
      const results: TranslationResult[] = [];
      
      for (const request of requests) {
        try {
          const result = await this.translate(request);
          results.push(result);
        } catch (error) {
          console.error(`❌ Batch translation failed for request ${request.id}:`, error);
          // Continue with other translations
        }
      }
      
      return results;
    } catch (error) {
      console.error('❌ Batch translation failed:', error);
      throw error;
    }
  }

  public getSupportedLanguages(): LanguageInfo[] {
    return this.supportedLanguages;
  }

  public getLanguageInfo(languageCode: string): LanguageInfo | undefined {
    return this.supportedLanguages.find(lang => lang.code === languageCode);
  }

  public getTranslationHistory(limit: number = 100): TranslationResult[] {
    return this.translationHistory.slice(0, limit);
  }

  public getStats(): TranslationStats {
    return { ...this.stats };
  }

  public async detectLanguage(text: string): Promise<string> {
    return this.detectLanguage(text);
  }

  public isInitialized(): boolean {
    return this.isInitialized;
  }

  public async clearHistory(): Promise<void> {
    this.translationHistory = [];
    this.stats = {
      totalTranslations: 0,
      languagesUsed: [],
      averageConfidence: 0,
      averageDuration: 0,
      topLanguages: [],
      recentTranslations: []
    };
    
    console.log('🗑️ Translation history cleared');
    this.emit('history_cleared');
  }
}

export default TranslationService;
