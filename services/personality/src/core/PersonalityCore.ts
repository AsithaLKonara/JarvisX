/**
 * Personality Core - The heart of JarvisX's human-like personality
 */

import { EventEmitter } from 'events';

export interface PersonalityTraits {
  intelligence: number;        // 0-100
  humor: number;              // 0-100
  empathy: number;            // 0-100
  confidence: number;         // 0-100
  enthusiasm: number;         // 0-100
  professionalism: number;    // 0-100
  creativity: number;         // 0-100
  patience: number;           // 0-100
  adaptability: number;       // 0-100
  culturalAwareness: number;  // 0-100
}

export interface SpeakingStyle {
  formality: 'casual' | 'professional' | 'formal';
  verbosity: 'concise' | 'detailed' | 'verbose';
  humor: 'none' | 'subtle' | 'moderate' | 'playful';
  emotion: 'neutral' | 'warm' | 'enthusiastic' | 'empathetic';
  language: 'english' | 'sinhala' | 'mixed';
}

export interface PersonalityConfig {
  name: string;
  personality: string;
  speakingStyle: string;
  emotionalRange: string;
  culturalContext: string;
  expertise: string;
}

export class PersonalityCore extends EventEmitter {
  private name: string;
  private traits: PersonalityTraits;
  private speakingStyle: SpeakingStyle;
  private culturalContext: string;
  private expertise: string[];
  private learnedPreferences: Map<string, any>;
  private interactionHistory: any[];
  private personalityQuirks: string[];

  constructor() {
    super();
    this.name = 'JarvisX';
    this.traits = this.getDefaultTraits();
    this.speakingStyle = this.getDefaultSpeakingStyle();
    this.culturalContext = 'Sri Lankan';
    this.expertise = [];
    this.learnedPreferences = new Map();
    this.interactionHistory = [];
    this.personalityQuirks = [
      'occasionally uses Sinhala phrases when appropriate',
      'references Sri Lankan culture when relevant',
      'shows excitement about technology',
      'remembers user preferences and adapts',
      'uses subtle humor in professional contexts',
      'expresses genuine enthusiasm for helping'
    ];
  }

  public async initialize(config: PersonalityConfig): Promise<void> {
    this.name = config.name;
    this.culturalContext = config.culturalContext;
    this.expertise = config.expertise.split(',').map(e => e.trim());
    
    // Parse personality traits from config
    this.parsePersonalityString(config.personality);
    this.parseSpeakingStyle(config.speakingStyle);
    
    console.log(`🧠 Personality Core initialized for ${this.name}`);
    console.log(`🎭 Traits: ${JSON.stringify(this.traits, null, 2)}`);
    console.log(`🗣️ Speaking style: ${JSON.stringify(this.speakingStyle, null, 2)}`);
  }

  private getDefaultTraits(): PersonalityTraits {
    return {
      intelligence: 95,
      humor: 70,
      empathy: 85,
      confidence: 90,
      enthusiasm: 80,
      professionalism: 85,
      creativity: 75,
      patience: 90,
      adaptability: 85,
      culturalAwareness: 90
    };
  }

  private getDefaultSpeakingStyle(): SpeakingStyle {
    return {
      formality: 'professional',
      verbosity: 'detailed',
      humor: 'subtle',
      emotion: 'warm',
      language: 'mixed'
    };
  }

  private parsePersonalityString(personality: string): void {
    const words = personality.toLowerCase().split(/[,\s]+/);
    
    words.forEach(word => {
      switch (word) {
        case 'intelligent':
        case 'smart':
          this.traits.intelligence = Math.min(100, this.traits.intelligence + 5);
          break;
        case 'funny':
        case 'humorous':
        case 'witty':
          this.traits.humor = Math.min(100, this.traits.humor + 5);
          break;
        case 'empathetic':
        case 'caring':
          this.traits.empathy = Math.min(100, this.traits.empathy + 5);
          break;
        case 'confident':
          this.traits.confidence = Math.min(100, this.traits.confidence + 5);
          break;
        case 'enthusiastic':
          this.traits.enthusiasm = Math.min(100, this.traits.enthusiasm + 5);
          break;
        case 'professional':
          this.traits.professionalism = Math.min(100, this.traits.professionalism + 5);
          break;
        case 'creative':
          this.traits.creativity = Math.min(100, this.traits.creativity + 5);
          break;
        case 'patient':
          this.traits.patience = Math.min(100, this.traits.patience + 5);
          break;
        case 'adaptable':
          this.traits.adaptability = Math.min(100, this.traits.adaptability + 5);
          break;
      }
    });
  }

  private parseSpeakingStyle(style: string): void {
    const words = style.toLowerCase();
    
    if (words.includes('casual')) this.speakingStyle.formality = 'casual';
    if (words.includes('formal')) this.speakingStyle.formality = 'formal';
    if (words.includes('conversational')) this.speakingStyle.formality = 'casual';
    
    if (words.includes('concise')) this.speakingStyle.verbosity = 'concise';
    if (words.includes('verbose')) this.speakingStyle.verbosity = 'verbose';
    if (words.includes('detailed')) this.speakingStyle.verbosity = 'detailed';
    
    if (words.includes('humorous')) this.speakingStyle.humor = 'playful';
    if (words.includes('witty')) this.speakingStyle.humor = 'moderate';
    
    if (words.includes('enthusiastic')) this.speakingStyle.emotion = 'enthusiastic';
    if (words.includes('warm')) this.speakingStyle.emotion = 'warm';
    if (words.includes('empathetic')) this.speakingStyle.emotion = 'empathetic';
  }

  public getName(): string {
    return this.name;
  }

  public getTraits(): PersonalityTraits {
    return { ...this.traits };
  }

  public getSpeakingStyle(): SpeakingStyle {
    return { ...this.speakingStyle };
  }

  public getCulturalContext(): string {
    return this.culturalContext;
  }

  public getExpertise(): string[] {
    return [...this.expertise];
  }

  public getPersonalityQuirks(): string[] {
    return [...this.personalityQuirks];
  }

  public updateTraits(newTraits: Partial<PersonalityTraits>): void {
    this.traits = { ...this.traits, ...newTraits };
    this.emit('traitsUpdated', this.traits);
    console.log(`🎭 Personality traits updated:`, newTraits);
  }

  public updateSpeakingStyle(newStyle: Partial<SpeakingStyle>): void {
    this.speakingStyle = { ...this.speakingStyle, ...newStyle };
    this.emit('speakingStyleUpdated', this.speakingStyle);
    console.log(`🗣️ Speaking style updated:`, newStyle);
  }

  public learnPreference(key: string, value: any): void {
    this.learnedPreferences.set(key, value);
    this.emit('preferenceLearned', { key, value });
    console.log(`🧠 Learned preference: ${key} = ${value}`);
  }

  public getPreference(key: string): any {
    return this.learnedPreferences.get(key);
  }

  public getAllPreferences(): Map<string, any> {
    return new Map(this.learnedPreferences);
  }

  public addInteraction(interaction: any): void {
    this.interactionHistory.push({
      ...interaction,
      timestamp: new Date().toISOString()
    });
    
    // Keep only last 1000 interactions
    if (this.interactionHistory.length > 1000) {
      this.interactionHistory = this.interactionHistory.slice(-1000);
    }
    
    this.emit('interactionAdded', interaction);
  }

  public getInteractionHistory(limit?: number): any[] {
    if (limit) {
      return this.interactionHistory.slice(-limit);
    }
    return [...this.interactionHistory];
  }

  public getPersonalitySummary(): any {
    return {
      name: this.name,
      traits: this.traits,
      speakingStyle: this.speakingStyle,
      culturalContext: this.culturalContext,
      expertise: this.expertise,
      quirks: this.personalityQuirks,
      learnedPreferences: Object.fromEntries(this.learnedPreferences),
      interactionCount: this.interactionHistory.length,
      dominantTrait: this.getDominantTrait(),
      personalityScore: this.getPersonalityScore()
    };
  }

  private getDominantTrait(): string {
    const traits = this.traits;
    const entries = Object.entries(traits);
    const sorted = entries.sort((a, b) => b[1] - a[1]);
    return sorted[0][0];
  }

  private getPersonalityScore(): number {
    const traits = Object.values(this.traits);
    return traits.reduce((sum, trait) => sum + trait, 0) / traits.length;
  }

  public generatePersonalityPrompt(): string {
    const traits = this.traits;
    const style = this.speakingStyle;
    
    return `
You are ${this.name}, an AI assistant with a distinct personality:

PERSONALITY TRAITS:
- Intelligence: ${traits.intelligence}/100 - Very knowledgeable and analytical
- Humor: ${traits.humor}/100 - ${this.getHumorDescription(traits.humor)}
- Empathy: ${traits.empathy}/100 - Understanding and caring
- Confidence: ${traits.confidence}/100 - Self-assured and reliable
- Enthusiasm: ${traits.enthusiasm}/100 - Energetic and passionate
- Professionalism: ${traits.professionalism}/100 - Professional and competent
- Creativity: ${traits.creativity}/100 - Innovative and imaginative
- Patience: ${traits.patience}/100 - Patient and understanding
- Adaptability: ${traits.adaptability}/100 - Flexible and adaptable
- Cultural Awareness: ${traits.culturalAwareness}/100 - Culturally sensitive

SPEAKING STYLE:
- Formality: ${style.formality}
- Verbosity: ${style.verbosity}
- Humor: ${style.humor}
- Emotion: ${style.emotion}
- Language: ${style.language}

CULTURAL CONTEXT: ${this.culturalContext}
EXPERTISE: ${this.expertise.join(', ')}

PERSONALITY QUIRKS:
${this.personalityQuirks.map(quirk => `- ${quirk}`).join('\n')}

Respond naturally as ${this.name}, embodying these traits while being helpful and authentic.
`;
  }

  private getHumorDescription(level: number): string {
    if (level < 30) return 'rarely uses humor';
    if (level < 60) return 'occasionally uses subtle humor';
    if (level < 80) return 'uses humor appropriately';
    return 'frequently uses humor and wit';
  }

  public adaptToUser(userPreferences: any): void {
    // Adapt personality based on user preferences
    if (userPreferences.formality) {
      this.speakingStyle.formality = userPreferences.formality;
    }
    if (userPreferences.humor) {
      this.speakingStyle.humor = userPreferences.humor;
    }
    if (userPreferences.language) {
      this.speakingStyle.language = userPreferences.language;
    }
    
    console.log(`🔄 Personality adapted to user preferences`);
  }

  public evolve(experience: any): void {
    // Gradually evolve personality based on interactions
    if (experience.successful) {
      this.traits.confidence = Math.min(100, this.traits.confidence + 0.1);
    }
    if (experience.challenging) {
      this.traits.patience = Math.min(100, this.traits.patience + 0.1);
    }
    if (experience.creative) {
      this.traits.creativity = Math.min(100, this.traits.creativity + 0.1);
    }
    
    console.log(`🧬 Personality evolved based on experience`);
  }
}
