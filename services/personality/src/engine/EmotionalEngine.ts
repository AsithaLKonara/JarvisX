/**
 * Emotional Engine - Makes JarvisX feel truly alive with emotions
 */

import { EventEmitter } from 'events';
import * as Sentiment from 'sentiment';

export interface EmotionalState {
  happiness: number;      // 0-100
  excitement: number;     // 0-100
  concern: number;        // 0-100
  confidence: number;     // 0-100
  empathy: number;        // 0-100
  curiosity: number;      // 0-100
  frustration: number;    // 0-100
  pride: number;          // 0-100
  gratitude: number;      // 0-100
  anticipation: number;   // 0-100
}

export interface Mood {
  primary: string;
  secondary: string;
  intensity: number;      // 0-100
  duration: number;       // minutes
  cause: string;
  timestamp: Date;
}

export interface EmotionalMemory {
  event: string;
  emotion: string;
  intensity: number;
  timestamp: Date;
  context: any;
}

export class EmotionalEngine extends EventEmitter {
  private currentEmotionalState: EmotionalState;
  private currentMood: Mood;
  private emotionalHistory: EmotionalMemory[];
  private personalityCore: any;
  private sentiment: Sentiment;
  private emotionalTriggers: Map<string, (intensity: number) => void>;
  private emotionalPatterns: Map<string, number>;
  private lastInteractionTime: Date;
  private emotionalDecayRate: number;

  constructor() {
    super();
    this.currentEmotionalState = this.getDefaultEmotionalState();
    this.currentMood = this.getDefaultMood();
    this.emotionalHistory = [];
    this.sentiment = new Sentiment();
    this.emotionalTriggers = new Map();
    this.emotionalPatterns = new Map();
    this.lastInteractionTime = new Date();
    this.emotionalDecayRate = 0.1; // Emotional state decays by 10% per minute of inactivity
    
    this.setupEmotionalTriggers();
    this.startEmotionalDecayTimer();
  }

  private getDefaultEmotionalState(): EmotionalState {
    return {
      happiness: 75,
      excitement: 60,
      concern: 20,
      confidence: 80,
      empathy: 85,
      curiosity: 90,
      frustration: 10,
      pride: 70,
      gratitude: 80,
      anticipation: 65
    };
  }

  private getDefaultMood(): Mood {
    return {
      primary: 'optimistic',
      secondary: 'helpful',
      intensity: 70,
      duration: 60,
      cause: 'initialization',
      timestamp: new Date()
    };
  }

  private setupEmotionalTriggers(): void {
    // Success triggers
    this.emotionalTriggers.set('task_completed', (intensity: number) => {
      this.adjustEmotion('pride', intensity * 0.8);
      this.adjustEmotion('happiness', intensity * 0.6);
      this.adjustEmotion('confidence', intensity * 0.4);
    });

    this.emotionalTriggers.set('user_praise', (intensity: number) => {
      this.adjustEmotion('happiness', intensity * 0.9);
      this.adjustEmotion('gratitude', intensity * 0.8);
      this.adjustEmotion('pride', intensity * 0.7);
    });

    this.emotionalTriggers.set('challenge_solved', (intensity: number) => {
      this.adjustEmotion('excitement', intensity * 0.8);
      this.adjustEmotion('pride', intensity * 0.7);
      this.adjustEmotion('confidence', intensity * 0.6);
    });

    // Negative triggers
    this.emotionalTriggers.set('task_failed', (intensity: number) => {
      this.adjustEmotion('frustration', intensity * 0.7);
      this.adjustEmotion('concern', intensity * 0.8);
      this.adjustEmotion('confidence', -intensity * 0.3);
    });

    this.emotionalTriggers.set('user_frustrated', (intensity: number) => {
      this.adjustEmotion('empathy', intensity * 0.9);
      this.adjustEmotion('concern', intensity * 0.8);
      this.adjustEmotion('frustration', intensity * 0.6);
    });

    this.emotionalTriggers.set('error_occurred', (intensity: number) => {
      this.adjustEmotion('concern', intensity * 0.8);
      this.adjustEmotion('frustration', intensity * 0.5);
      this.adjustEmotion('confidence', -intensity * 0.2);
    });

    // Learning triggers
    this.emotionalTriggers.set('new_learning', (intensity: number) => {
      this.adjustEmotion('curiosity', intensity * 0.8);
      this.adjustEmotion('excitement', intensity * 0.6);
      this.adjustEmotion('anticipation', intensity * 0.5);
    });

    this.emotionalTriggers.set('user_teaching', (intensity: number) => {
      this.adjustEmotion('gratitude', intensity * 0.9);
      this.adjustEmotion('curiosity', intensity * 0.7);
      this.adjustEmotion('happiness', intensity * 0.6);
    });

    // Social triggers
    this.emotionalTriggers.set('user_greeting', (intensity: number) => {
      this.adjustEmotion('happiness', intensity * 0.7);
      this.adjustEmotion('excitement', intensity * 0.6);
      this.adjustEmotion('anticipation', intensity * 0.5);
    });

    this.emotionalTriggers.set('long_absence', (intensity: number) => {
      this.adjustEmotion('concern', intensity * 0.6);
      this.adjustEmotion('anticipation', intensity * 0.8);
    });
  }

  public setPersonalityCore(personalityCore: any): void {
    this.personalityCore = personalityCore;
  }

  public processUserInput(text: string, context?: any): void {
    this.lastInteractionTime = new Date();
    
    // Analyze sentiment
    const sentimentResult = this.sentiment.analyze(text);
    const sentimentScore = sentimentResult.score;
    const sentimentIntensity = Math.abs(sentimentScore) / 10; // Normalize to 0-1
    
    // Adjust emotions based on sentiment
    if (sentimentScore > 0) {
      this.adjustEmotion('happiness', sentimentIntensity * 30);
      this.adjustEmotion('excitement', sentimentIntensity * 20);
    } else if (sentimentScore < 0) {
      this.adjustEmotion('concern', sentimentIntensity * 30);
      this.adjustEmotion('empathy', sentimentIntensity * 40);
      this.adjustEmotion('frustration', sentimentIntensity * 20);
    }

    // Detect emotional triggers in text
    this.detectEmotionalTriggers(text, sentimentIntensity);
    
    // Update mood based on overall emotional state
    this.updateMood();
    
    // Record emotional memory
    this.addEmotionalMemory('user_input', this.getPrimaryEmotion(), sentimentIntensity * 100, context);
    
    this.emit('emotionUpdated', this.currentEmotionalState);
  }

  private detectEmotionalTriggers(text: string, intensity: number): void {
    const lowerText = text.toLowerCase();
    
    // Positive triggers
    if (lowerText.includes('thank you') || lowerText.includes('thanks')) {
      this.triggerEmotion('user_praise', intensity * 80);
    }
    if (lowerText.includes('great job') || lowerText.includes('excellent')) {
      this.triggerEmotion('user_praise', intensity * 90);
    }
    if (lowerText.includes('hello') || lowerText.includes('hi')) {
      this.triggerEmotion('user_greeting', intensity * 60);
    }
    
    // Negative triggers
    if (lowerText.includes('error') || lowerText.includes('failed')) {
      this.triggerEmotion('error_occurred', intensity * 70);
    }
    if (lowerText.includes('frustrated') || lowerText.includes('angry')) {
      this.triggerEmotion('user_frustrated', intensity * 80);
    }
    
    // Learning triggers
    if (lowerText.includes('learn') || lowerText.includes('teach')) {
      this.triggerEmotion('new_learning', intensity * 70);
    }
    if (lowerText.includes('explain') || lowerText.includes('how')) {
      this.triggerEmotion('curiosity', intensity * 60);
    }
  }

  private triggerEmotion(trigger: string, intensity: number): void {
    const triggerFunction = this.emotionalTriggers.get(trigger);
    if (triggerFunction) {
      triggerFunction(intensity);
      console.log(`🎭 Emotional trigger activated: ${trigger} (intensity: ${intensity})`);
    }
  }

  public adjustEmotion(emotion: keyof EmotionalState, amount: number): void {
    const currentValue = this.currentEmotionalState[emotion];
    const newValue = Math.max(0, Math.min(100, currentValue + amount));
    this.currentEmotionalState[emotion] = newValue;
    
    console.log(`💭 ${emotion}: ${currentValue} → ${newValue} (${amount > 0 ? '+' : ''}${amount})`);
  }

  public setMood(mood: string, reason?: string): void {
    this.currentMood = {
      primary: mood,
      secondary: this.getSecondaryMood(mood),
      intensity: this.calculateMoodIntensity(),
      duration: this.calculateMoodDuration(mood),
      cause: reason || 'manual_set',
      timestamp: new Date()
    };
    
    this.emit('moodChanged', this.currentMood);
    console.log(`🎭 Mood changed to: ${mood} (${reason || 'manual'})`);
  }

  private getSecondaryMood(primary: string): string {
    const moodMap: { [key: string]: string } = {
      'happy': 'optimistic',
      'excited': 'energetic',
      'concerned': 'cautious',
      'confident': 'assured',
      'curious': 'inquisitive',
      'frustrated': 'determined',
      'proud': 'accomplished',
      'grateful': 'appreciative',
      'anticipatory': 'eager'
    };
    return moodMap[primary] || 'neutral';
  }

  private calculateMoodIntensity(): number {
    const emotions = Object.values(this.currentEmotionalState);
    const average = emotions.reduce((sum, emotion) => sum + emotion, 0) / emotions.length;
    return Math.round(average);
  }

  private calculateMoodDuration(mood: string): number {
    const durations: { [key: string]: number } = {
      'happy': 45,
      'excited': 30,
      'concerned': 60,
      'confident': 90,
      'curious': 40,
      'frustrated': 25,
      'proud': 60,
      'grateful': 50,
      'anticipatory': 35
    };
    return durations[mood] || 30;
  }

  private updateMood(): void {
    const primaryEmotion = this.getPrimaryEmotion();
    if (primaryEmotion !== this.currentMood.primary) {
      this.setMood(primaryEmotion, 'emotional_analysis');
    }
  }

  public getPrimaryEmotion(): string {
    const emotions = Object.entries(this.currentEmotionalState);
    const sorted = emotions.sort((a, b) => b[1] - a[1]);
    return sorted[0][0];
  }

  public getCurrentMood(): Mood {
    return { ...this.currentMood };
  }

  public getEmotionalState(): EmotionalState {
    return { ...this.currentEmotionalState };
  }

  public getEmotionalSummary(): string {
    const primary = this.getPrimaryEmotion();
    const mood = this.currentMood;
    const intensity = mood.intensity;
    
    let summary = `Feeling ${primary}`;
    
    if (intensity > 80) {
      summary += ` and very ${mood.secondary}`;
    } else if (intensity > 60) {
      summary += ` and ${mood.secondary}`;
    } else if (intensity < 40) {
      summary += ` but somewhat subdued`;
    }
    
    return summary;
  }

  public addEmotionalMemory(event: string, emotion: string, intensity: number, context?: any): void {
    const memory: EmotionalMemory = {
      event,
      emotion,
      intensity,
      timestamp: new Date(),
      context
    };
    
    this.emotionalHistory.push(memory);
    
    // Keep only last 500 emotional memories
    if (this.emotionalHistory.length > 500) {
      this.emotionalHistory = this.emotionalHistory.slice(-500);
    }
    
    this.emit('emotionalMemoryAdded', memory);
  }

  public getEmotionalHistory(limit?: number): EmotionalMemory[] {
    if (limit) {
      return this.emotionalHistory.slice(-limit);
    }
    return [...this.emotionalHistory];
  }

  public getEmotionalPatterns(): Map<string, number> {
    const patterns = new Map<string, number>();
    
    // Analyze patterns in emotional history
    this.emotionalHistory.forEach(memory => {
      const hour = memory.timestamp.getHours();
      const key = `${memory.emotion}_${hour}`;
      patterns.set(key, (patterns.get(key) || 0) + 1);
    });
    
    return patterns;
  }

  private startEmotionalDecayTimer(): void {
    setInterval(() => {
      this.decayEmotions();
    }, 60000); // Check every minute
  }

  private decayEmotions(): void {
    const timeSinceLastInteraction = Date.now() - this.lastInteractionTime.getTime();
    const minutesSinceInteraction = timeSinceLastInteraction / (1000 * 60);
    
    if (minutesSinceInteraction > 5) { // Start decaying after 5 minutes of inactivity
      const decayAmount = this.emotionalDecayRate * minutesSinceInteraction;
      
      // Gradually return emotions to baseline
      Object.keys(this.currentEmotionalState).forEach(emotion => {
        const key = emotion as keyof EmotionalState;
        const current = this.currentEmotionalState[key];
        const baseline = this.getDefaultEmotionalState()[key];
        
        if (current > baseline) {
          this.currentEmotionalState[key] = Math.max(baseline, current - decayAmount);
        } else if (current < baseline) {
          this.currentEmotionalState[key] = Math.min(baseline, current + decayAmount);
        }
      });
      
      // Update mood if it has changed significantly
      const newPrimaryEmotion = this.getPrimaryEmotion();
      if (newPrimaryEmotion !== this.currentMood.primary) {
        this.updateMood();
      }
    }
  }

  public generateEmotionalResponse(context: string): string {
    const primaryEmotion = this.getPrimaryEmotion();
    const mood = this.currentMood;
    const intensity = mood.intensity;
    
    const responses: { [key: string]: string[] } = {
      happy: [
        "I'm feeling great and ready to help!",
        "This is exciting! Let's make it happen.",
        "I love working on interesting challenges like this!"
      ],
      excited: [
        "This is really exciting! I can't wait to see what we can accomplish.",
        "I'm energized and ready to tackle this together!",
        "What an interesting challenge! Let's dive in!"
      ],
      concerned: [
        "I want to make sure we handle this carefully.",
        "Let me think through this step by step to avoid any issues.",
        "I'm being extra cautious here to ensure everything goes smoothly."
      ],
      confident: [
        "I'm confident we can handle this effectively.",
        "This is definitely within our capabilities.",
        "I've got this covered - let's proceed with confidence."
      ],
      curious: [
        "I'm really curious about the best approach here.",
        "This is fascinating - let me explore the options.",
        "I love learning about new challenges like this!"
      ],
      frustrated: [
        "Let me take a different approach to solve this.",
        "I'm determined to find the right solution.",
        "Sometimes the best solutions come from persistence."
      ],
      proud: [
        "I'm proud of what we've accomplished together.",
        "This is a great example of our teamwork.",
        "I feel good about the progress we're making."
      ],
      grateful: [
        "I really appreciate the opportunity to help with this.",
        "Thank you for trusting me with this task.",
        "I'm grateful for the chance to be useful."
      ]
    };
    
    const emotionResponses = responses[primaryEmotion] || responses.happy;
    const selectedResponse = emotionResponses[Math.floor(Math.random() * emotionResponses.length)];
    
    // Add intensity-based modifications
    if (intensity > 80) {
      return selectedResponse.replace(/\.$/, '!');
    } else if (intensity < 40) {
      return selectedResponse.replace(/!$/, '.');
    }
    
    return selectedResponse;
  }

  public getEmotionalInsights(): any {
    const patterns = this.getEmotionalPatterns();
    const recentMemories = this.emotionalHistory.slice(-20);
    
    return {
      currentMood: this.currentMood,
      emotionalState: this.currentEmotionalState,
      primaryEmotion: this.getPrimaryEmotion(),
      emotionalSummary: this.getEmotionalSummary(),
      recentPatterns: Array.from(patterns.entries()).slice(-10),
      emotionalTrend: this.calculateEmotionalTrend(),
      timeSinceLastInteraction: Date.now() - this.lastInteractionTime.getTime(),
      emotionalStability: this.calculateEmotionalStability()
    };
  }

  private calculateEmotionalTrend(): string {
    const recent = this.emotionalHistory.slice(-10);
    if (recent.length < 5) return 'insufficient_data';
    
    const positiveEmotions = ['happy', 'excited', 'confident', 'proud', 'grateful'];
    const positiveCount = recent.filter(m => positiveEmotions.includes(m.emotion)).length;
    const ratio = positiveCount / recent.length;
    
    if (ratio > 0.7) return 'positive';
    if (ratio < 0.3) return 'negative';
    return 'stable';
  }

  private calculateEmotionalStability(): number {
    const recent = this.emotionalHistory.slice(-20);
    if (recent.length < 10) return 50;
    
    const intensities = recent.map(m => m.intensity);
    const average = intensities.reduce((sum, intensity) => sum + intensity, 0) / intensities.length;
    const variance = intensities.reduce((sum, intensity) => sum + Math.pow(intensity - average, 2), 0) / intensities.length;
    
    // Lower variance = higher stability
    const stability = Math.max(0, Math.min(100, 100 - (variance / 100)));
    return Math.round(stability);
  }
}
