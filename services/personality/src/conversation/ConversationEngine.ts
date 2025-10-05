/**
 * Conversation Engine - Makes JarvisX truly conversational and human-like
 */

import { EventEmitter } from 'events';
import axios from 'axios';
import * as natural from 'natural';
import * as compromise from 'compromise';

export interface ConversationContext {
  sessionId: string;
  userId: string;
  currentTopic: string;
  conversationHistory: any[];
  userPreferences: any;
  emotionalState: any;
  timeOfDay: string;
  dayOfWeek: string;
  recentTopics: string[];
  userMood: string;
}

export interface ConversationResponse {
  text: string;
  emotion: string;
  personality: any;
  confidence: number;
  followUpSuggestions: string[];
  context: any;
  reasoning: string;
}

export interface ConversationMemory {
  id: string;
  content: string;
  importance: number;
  tags: string[];
  timestamp: Date;
  context: any;
}

export class ConversationEngine extends EventEmitter {
  private personalityCore: any;
  private emotionalEngine: any;
  private memorySystem: any;
  private conversationSessions: Map<string, ConversationContext>;
  private conversationCount: number;
  private tokenizer: natural.WordTokenizer;
  private stemmer: natural.PorterStemmer;
  private openaiApiKey: string;
  private conversationPatterns: Map<string, any>;
  private culturalContext: any;

  constructor() {
    super();
    this.conversationSessions = new Map();
    this.conversationCount = 0;
    this.tokenizer = new natural.WordTokenizer();
    this.stemmer = natural.PorterStemmer;
    this.openaiApiKey = process.env.OPENAI_API_KEY || '';
    this.conversationPatterns = new Map();
    this.culturalContext = this.initializeCulturalContext();
    
    this.initializeConversationPatterns();
  }

  private initializeCulturalContext(): any {
    return {
      language: 'sinhala_english',
      culture: 'sri_lankan',
      greetings: {
        sinhala: ['ayubowan', 'kohomada', 'hari', 'stuti'],
        english: ['hello', 'hi', 'good morning', 'good afternoon', 'good evening']
      },
      politeness: {
        sinhala: ['karunakara', 'sthuthi', 'kohomada'],
        english: ['please', 'thank you', 'excuse me', 'sorry']
      },
      expressions: {
        excitement: ['hari hari', 'great', 'excellent', 'wonderful'],
        concern: ['mokada', 'what happened', 'is everything okay'],
        appreciation: ['stuti', 'thank you', 'appreciate it']
      },
      culturalReferences: [
        'Sri Lankan tea', 'Ceylon', 'Colombo', 'Kandy', 'Galle', 
        'Sinhala New Year', 'Vesak', 'Poson', 'Esala', 'Duruthu'
      ]
    };
  }

  private initializeConversationPatterns(): void {
    // Greeting patterns
    this.conversationPatterns.set('greeting', {
      responses: [
        "Ayubowan! I'm JarvisX, your AI assistant. How can I help you today?",
        "Hello! Great to see you again. What would you like to work on?",
        "Hi there! I'm ready to assist. What's on your mind?",
        "Good to have you back! How can I make your day better?"
      ],
      followUps: [
        "What would you like to accomplish today?",
        "Is there anything specific you'd like me to help with?",
        "How can I assist you today?"
      ]
    });

    // Question patterns
    this.conversationPatterns.set('question', {
      responses: [
        "That's a great question! Let me think about that.",
        "I'd be happy to help you with that.",
        "Interesting question! Let me provide some insights."
      ],
      followUps: [
        "Would you like me to elaborate on that?",
        "Does that answer your question?",
        "Is there anything else you'd like to know?"
      ]
    });

    // Request patterns
    this.conversationPatterns.set('request', {
      responses: [
        "I'll help you with that right away.",
        "Consider it done! Let me handle that for you.",
        "I'm on it! Give me a moment to work on that."
      ],
      followUps: [
        "Would you like me to show you the progress?",
        "Is there anything specific you'd like me to focus on?",
        "Should I notify you when it's complete?"
      ]
    });

    // Compliment patterns
    this.conversationPatterns.set('compliment', {
      responses: [
        "Thank you so much! I really appreciate that.",
        "That means a lot to me! I'm glad I could help.",
        "You're very kind! I'm here to support you."
      ],
      followUps: [
        "Is there anything else I can help you with?",
        "How else can I be of assistance?",
        "What would you like to work on next?"
      ]
    });

    // Problem patterns
    this.conversationPatterns.set('problem', {
      responses: [
        "I understand that's frustrating. Let me help you solve this.",
        "Don't worry, we'll figure this out together.",
        "I'm here to help. Let's tackle this step by step."
      ],
      followUps: [
        "Can you tell me more about what's happening?",
        "What steps have you already tried?",
        "Would you like me to investigate this further?"
      ]
    });
  }

  public setPersonalityCore(personalityCore: any): void {
    this.personalityCore = personalityCore;
  }

  public setEmotionalEngine(emotionalEngine: any): void {
    this.emotionalEngine = emotionalEngine;
  }

  public setMemorySystem(memorySystem: any): void {
    this.memorySystem = memorySystem;
  }

  public async generateResponse(input: {
    message: string;
    context?: any;
    userEmotion?: string;
    sessionId?: string;
  }): Promise<ConversationResponse> {
    const { message, context = {}, userEmotion, sessionId = 'default' } = input;
    
    this.conversationCount++;
    
    // Get or create conversation session
    let conversationContext = this.conversationSessions.get(sessionId);
    if (!conversationContext) {
      conversationContext = await this.createConversationSession(sessionId);
    }

    // Update conversation context
    conversationContext.conversationHistory.push({
      user: message,
      timestamp: new Date(),
      userEmotion,
      context
    });

    // Analyze the message
    const analysis = this.analyzeMessage(message, conversationContext);
    
    // Process through emotional engine
    this.emotionalEngine.processUserInput(message, context);
    
    // Generate contextual response
    const response = await this.generateContextualResponse(message, analysis, conversationContext);
    
    // Add to conversation history
    conversationContext.conversationHistory.push({
      assistant: response.text,
      timestamp: new Date(),
      emotion: response.emotion,
      confidence: response.confidence
    });

    // Update session
    this.conversationSessions.set(sessionId, conversationContext);
    
    // Store important parts in memory
    await this.storeConversationMemory(message, response, conversationContext);
    
    this.emit('responseGenerated', response);
    
    return response;
  }

  private async createConversationSession(sessionId: string): Promise<ConversationContext> {
    const now = new Date();
    const timeOfDay = this.getTimeOfDay(now);
    const dayOfWeek = this.getDayOfWeek(now);
    
    const context: ConversationContext = {
      sessionId,
      userId: 'default',
      currentTopic: '',
      conversationHistory: [],
      userPreferences: await this.memorySystem.getUserProfile('default'),
      emotionalState: this.emotionalEngine.getEmotionalState(),
      timeOfDay,
      dayOfWeek,
      recentTopics: [],
      userMood: 'neutral'
    };

    this.conversationSessions.set(sessionId, context);
    return context;
  }

  private analyzeMessage(message: string, context: ConversationContext): any {
    const tokens = this.tokenizer.tokenize(message.toLowerCase());
    const stemmedTokens = tokens.map(token => this.stemmer.stem(token));
    
    // Detect language
    const language = this.detectLanguage(message);
    
    // Detect intent
    const intent = this.detectIntent(message, tokens);
    
    // Detect sentiment
    const sentiment = this.analyzeSentiment(message);
    
    // Detect cultural references
    const culturalReferences = this.detectCulturalReferences(message);
    
    // Detect conversation pattern
    const pattern = this.detectConversationPattern(message, tokens);
    
    // Extract entities
    const entities = this.extractEntities(message);
    
    // Detect topics
    const topics = this.extractTopics(message, tokens);
    
    return {
      language,
      intent,
      sentiment,
      culturalReferences,
      pattern,
      entities,
      topics,
      tokens,
      stemmedTokens,
      complexity: this.analyzeComplexity(message),
      urgency: this.detectUrgency(message),
      politeness: this.detectPoliteness(message)
    };
  }

  private detectLanguage(message: string): string {
    const sinhalaPattern = /[\u0D80-\u0DFF]/;
    const englishPattern = /[a-zA-Z]/;
    
    if (sinhalaPattern.test(message) && englishPattern.test(message)) {
      return 'mixed';
    } else if (sinhalaPattern.test(message)) {
      return 'sinhala';
    } else {
      return 'english';
    }
  }

  private detectIntent(message: string, tokens: string[]): string {
    const lowerMessage = message.toLowerCase();
    
    // Greeting detection
    if (this.culturalContext.greetings.sinhala.some(g => lowerMessage.includes(g)) ||
        this.culturalContext.greetings.english.some(g => lowerMessage.includes(g))) {
      return 'greeting';
    }
    
    // Question detection
    if (lowerMessage.includes('?') || 
        tokens.includes('what') || tokens.includes('how') || 
        tokens.includes('why') || tokens.includes('when') || 
        tokens.includes('where') || tokens.includes('who')) {
      return 'question';
    }
    
    // Request detection
    if (tokens.includes('please') || tokens.includes('can') || 
        tokens.includes('could') || tokens.includes('would') ||
        lowerMessage.includes('help') || lowerMessage.includes('assist')) {
      return 'request';
    }
    
    // Compliment detection
    if (tokens.includes('thank') || tokens.includes('great') || 
        tokens.includes('awesome') || tokens.includes('excellent') ||
        lowerMessage.includes('good job') || lowerMessage.includes('well done')) {
      return 'compliment';
    }
    
    // Problem detection
    if (tokens.includes('problem') || tokens.includes('issue') || 
        tokens.includes('error') || tokens.includes('failed') ||
        tokens.includes('broken') || tokens.includes('not working')) {
      return 'problem';
    }
    
    return 'statement';
  }

  private analyzeSentiment(message: string): any {
    const doc = compromise(message);
    const sentiment = doc.sentiment();
    
    return {
      score: sentiment.score,
      polarity: sentiment.polarity,
      confidence: sentiment.confidence,
      positive: sentiment.positive,
      negative: sentiment.negative
    };
  }

  private detectCulturalReferences(message: string): string[] {
    const references: string[] = [];
    
    this.culturalContext.culturalReferences.forEach(ref => {
      if (message.toLowerCase().includes(ref.toLowerCase())) {
        references.push(ref);
      }
    });
    
    return references;
  }

  private detectConversationPattern(message: string, tokens: string[]): string {
    for (const [pattern, config] of this.conversationPatterns) {
      if (this.matchesPattern(message, tokens, config)) {
        return pattern;
      }
    }
    return 'general';
  }

  private matchesPattern(message: string, tokens: string[], config: any): boolean {
    // Simple pattern matching - can be enhanced with ML
    const lowerMessage = message.toLowerCase();
    
    switch (pattern) {
      case 'greeting':
        return this.culturalContext.greetings.sinhala.some(g => lowerMessage.includes(g)) ||
               this.culturalContext.greetings.english.some(g => lowerMessage.includes(g));
      
      case 'question':
        return message.includes('?') || 
               tokens.some(t => ['what', 'how', 'why', 'when', 'where', 'who'].includes(t));
      
      case 'request':
        return tokens.some(t => ['please', 'can', 'could', 'would', 'help'].includes(t));
      
      case 'compliment':
        return tokens.some(t => ['thank', 'great', 'awesome', 'excellent'].includes(t));
      
      case 'problem':
        return tokens.some(t => ['problem', 'issue', 'error', 'failed', 'broken'].includes(t));
      
      default:
        return false;
    }
  }

  private extractEntities(message: string): any[] {
    const doc = compromise(message);
    const entities: any[] = [];
    
    // Extract people
    doc.people().forEach(person => {
      entities.push({ type: 'person', value: person.text(), confidence: 0.8 });
    });
    
    // Extract places
    doc.places().forEach(place => {
      entities.push({ type: 'place', value: place.text(), confidence: 0.7 });
    });
    
    // Extract organizations
    doc.organizations().forEach(org => {
      entities.push({ type: 'organization', value: org.text(), confidence: 0.7 });
    });
    
    // Extract dates
    doc.dates().forEach(date => {
      entities.push({ type: 'date', value: date.text(), confidence: 0.9 });
    });
    
    return entities;
  }

  private extractTopics(message: string, tokens: string[]): string[] {
    const topics: string[] = [];
    
    // Technology topics
    const techKeywords = ['code', 'programming', 'software', 'app', 'website', 'database'];
    if (tokens.some(t => techKeywords.includes(t))) {
      topics.push('technology');
    }
    
    // Business topics
    const businessKeywords = ['business', 'company', 'project', 'meeting', 'client'];
    if (tokens.some(t => businessKeywords.includes(t))) {
      topics.push('business');
    }
    
    // Personal topics
    const personalKeywords = ['family', 'friend', 'home', 'personal', 'life'];
    if (tokens.some(t => personalKeywords.includes(t))) {
      topics.push('personal');
    }
    
    return topics;
  }

  private analyzeComplexity(message: string): number {
    const words = message.split(' ');
    const sentences = message.split(/[.!?]+/).length;
    const avgWordsPerSentence = words.length / sentences;
    
    // Simple complexity scoring
    let complexity = 1;
    if (avgWordsPerSentence > 15) complexity += 1;
    if (words.length > 50) complexity += 1;
    if (message.includes(',')) complexity += 1;
    if (message.includes(';')) complexity += 1;
    
    return Math.min(5, complexity);
  }

  private detectUrgency(message: string): number {
    const urgentKeywords = ['urgent', 'asap', 'immediately', 'now', 'quickly', 'emergency'];
    const lowerMessage = message.toLowerCase();
    
    let urgency = 1;
    urgentKeywords.forEach(keyword => {
      if (lowerMessage.includes(keyword)) {
        urgency += 1;
      }
    });
    
    return Math.min(5, urgency);
  }

  private detectPoliteness(message: string): number {
    const politeKeywords = ['please', 'thank you', 'excuse me', 'sorry', 'karunakara', 'sthuthi'];
    const lowerMessage = message.toLowerCase();
    
    let politeness = 1;
    politeKeywords.forEach(keyword => {
      if (lowerMessage.includes(keyword)) {
        politeness += 1;
      }
    });
    
    return Math.min(5, politeness);
  }

  private async generateContextualResponse(
    message: string, 
    analysis: any, 
    context: ConversationContext
  ): Promise<ConversationResponse> {
    
    // Get personality prompt
    const personalityPrompt = this.personalityCore.generatePersonalityPrompt();
    
    // Get current emotional state
    const emotionalState = this.emotionalEngine.getEmotionalState();
    const currentMood = this.emotionalEngine.getCurrentMood();
    
    // Get relevant memories
    const relevantMemories = await this.memorySystem.searchMemories({
      searchText: analysis.topics.join(' '),
      limit: 5
    });
    
    // Build context for GPT
    const systemPrompt = this.buildSystemPrompt(personalityPrompt, emotionalState, relevantMemories, context);
    
    // Generate response using GPT
    const gptResponse = await this.generateGPTResponse(systemPrompt, message, analysis);
    
    // Post-process response
    const processedResponse = this.postProcessResponse(gptResponse, analysis, context);
    
    return processedResponse;
  }

  private buildSystemPrompt(
    personalityPrompt: string, 
    emotionalState: any, 
    memories: any[], 
    context: ConversationContext
  ): string {
    return `
${personalityPrompt}

CURRENT EMOTIONAL STATE:
${JSON.stringify(emotionalState, null, 2)}

RELEVANT MEMORIES:
${memories.map(m => `- ${m.content} (importance: ${m.importance})`).join('\n')}

CONVERSATION CONTEXT:
- Time of day: ${context.timeOfDay}
- Day of week: ${context.dayOfWeek}
- Recent topics: ${context.recentTopics.join(', ')}
- Conversation length: ${context.conversationHistory.length} exchanges

CULTURAL CONTEXT:
- Primary language: Sinhala and English
- Cultural background: Sri Lankan
- Appropriate to use Sinhala phrases when relevant
- Be culturally sensitive and aware

RESPONSE GUIDELINES:
1. Be conversational and natural
2. Match the user's emotional tone appropriately
3. Use relevant cultural references when appropriate
4. Show empathy and understanding
5. Be helpful and proactive
6. Maintain personality consistency
7. Provide follow-up suggestions when helpful

Generate a natural, human-like response that embodies these traits.
`;
  }

  private async generateGPTResponse(systemPrompt: string, message: string, analysis: any): Promise<any> {
    if (!this.openaiApiKey) {
      // Fallback to rule-based response
      return this.generateFallbackResponse(message, analysis);
    }

    try {
      const response = await axios.post('https://api.openai.com/v1/chat/completions', {
        model: 'gpt-4',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: message }
        ],
        max_tokens: 300,
        temperature: 0.8,
        presence_penalty: 0.6,
        frequency_penalty: 0.3
      }, {
        headers: {
          'Authorization': `Bearer ${this.openaiApiKey}`,
          'Content-Type': 'application/json'
        }
      });

      return {
        text: response.data.choices[0].message.content,
        confidence: 0.9
      };
    } catch (error) {
      console.error('GPT API error:', error);
      return this.generateFallbackResponse(message, analysis);
    }
  }

  private generateFallbackResponse(message: string, analysis: any): any {
    const pattern = this.conversationPatterns.get(analysis.pattern);
    if (pattern) {
      const responses = pattern.responses;
      const response = responses[Math.floor(Math.random() * responses.length)];
      return {
        text: response,
        confidence: 0.7
      };
    }
    
    return {
      text: "I understand. Let me help you with that.",
      confidence: 0.6
    };
  }

  private postProcessResponse(response: any, analysis: any, context: ConversationContext): ConversationResponse {
    // Add emotional coloring
    const emotion = this.emotionalEngine.getPrimaryEmotion();
    const emotionalResponse = this.emotionalEngine.generateEmotionalResponse(response.text);
    
    // Generate follow-up suggestions
    const followUps = this.generateFollowUpSuggestions(analysis, context);
    
    // Add cultural touches
    const culturalResponse = this.addCulturalTouches(response.text, analysis);
    
    return {
      text: culturalResponse,
      emotion,
      personality: this.personalityCore.getPersonalitySummary(),
      confidence: response.confidence,
      followUpSuggestions: followUps,
      context: {
        pattern: analysis.pattern,
        topics: analysis.topics,
        language: analysis.language,
        sentiment: analysis.sentiment
      },
      reasoning: `Generated based on ${analysis.pattern} pattern with ${emotion} emotional state`
    };
  }

  private addCulturalTouches(text: string, analysis: any): string {
    // Add Sinhala greetings when appropriate
    if (analysis.pattern === 'greeting' && analysis.language !== 'english') {
      const sinhalaGreetings = ['Ayubowan!', 'Kohomada!', 'Hari!'];
      const greeting = sinhalaGreetings[Math.floor(Math.random() * sinhalaGreetings.length)];
      return `${greeting} ${text}`;
    }
    
    // Add cultural references when relevant
    if (analysis.culturalReferences.length > 0) {
      return text.replace(/Sri Lanka/g, 'our beautiful Sri Lanka');
    }
    
    return text;
  }

  private generateFollowUpSuggestions(analysis: any, context: ConversationContext): string[] {
    const pattern = this.conversationPatterns.get(analysis.pattern);
    if (pattern && pattern.followUps) {
      return pattern.followUps;
    }
    
    // Generate contextual follow-ups based on topics
    const followUps: string[] = [];
    
    if (analysis.topics.includes('technology')) {
      followUps.push('Would you like me to help you with coding?', 'Should I set up a development environment?');
    }
    
    if (analysis.topics.includes('business')) {
      followUps.push('Would you like me to create a project plan?', 'Should I schedule a meeting?');
    }
    
    followUps.push('Is there anything else I can help you with?', 'What would you like to work on next?');
    
    return followUps.slice(0, 3); // Return max 3 suggestions
  }

  private async storeConversationMemory(
    message: string, 
    response: ConversationResponse, 
    context: ConversationContext
  ): Promise<void> {
    // Store important conversation parts
    if (response.confidence > 0.7) {
      await this.memorySystem.addMemory(
        `User said: "${message}" | JarvisX responded: "${response.text}"`,
        'conversation',
        5,
        response.context.topics,
        { pattern: response.context.pattern, emotion: response.emotion },
        'conversation'
      );
    }
  }

  public async generateGreeting(): Promise<string> {
    const timeOfDay = this.getTimeOfDay(new Date());
    const greetings = [
      `Good ${timeOfDay}! I'm JarvisX, your AI assistant. How can I help you today?`,
      `Ayubowan! Great to see you. What would you like to accomplish?`,
      `Hello! I'm here and ready to assist. What's on your mind?`,
      `Hi there! How can I make your day better today?`
    ];
    
    return greetings[Math.floor(Math.random() * greetings.length)];
  }

  private getTimeOfDay(date: Date): string {
    const hour = date.getHours();
    if (hour < 12) return 'morning';
    if (hour < 17) return 'afternoon';
    if (hour < 21) return 'evening';
    return 'night';
  }

  private getDayOfWeek(date: Date): string {
    const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    return days[date.getDay()];
  }

  public getConversationStyle(): any {
    return {
      formality: this.personalityCore.getSpeakingStyle().formality,
      verbosity: this.personalityCore.getSpeakingStyle().verbosity,
      humor: this.personalityCore.getSpeakingStyle().humor,
      emotion: this.personalityCore.getSpeakingStyle().emotion,
      culturalAwareness: this.personalityCore.getTraits().culturalAwareness
    };
  }

  public getConversationCount(): number {
    return this.conversationCount;
  }

  public getActiveSessions(): number {
    return this.conversationSessions.size;
  }

  public async getConversationStats(): Promise<any> {
    const totalConversations = this.conversationCount;
    const activeSessions = this.conversationSessions.size;
    
    // Analyze conversation patterns
    const patterns: { [key: string]: number } = {};
    this.conversationSessions.forEach(session => {
      session.conversationHistory.forEach(interaction => {
        if (interaction.assistant) {
          // Simple pattern detection
          if (interaction.assistant.includes('?')) patterns.questions = (patterns.questions || 0) + 1;
          if (interaction.assistant.includes('help')) patterns.helpful = (patterns.helpful || 0) + 1;
          if (interaction.assistant.includes('thank')) patterns.grateful = (patterns.grateful || 0) + 1;
        }
      });
    });
    
    return {
      totalConversations,
      activeSessions,
      patterns,
      averageConversationLength: this.calculateAverageConversationLength(),
      mostCommonTopics: this.getMostCommonTopics()
    };
  }

  private calculateAverageConversationLength(): number {
    let totalLength = 0;
    let sessionCount = 0;
    
    this.conversationSessions.forEach(session => {
      totalLength += session.conversationHistory.length;
      sessionCount++;
    });
    
    return sessionCount > 0 ? Math.round(totalLength / sessionCount) : 0;
  }

  private getMostCommonTopics(): string[] {
    const topicCounts: { [key: string]: number } = {};
    
    this.conversationSessions.forEach(session => {
      session.recentTopics.forEach(topic => {
        topicCounts[topic] = (topicCounts[topic] || 0) + 1;
      });
    });
    
    return Object.entries(topicCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([topic]) => topic);
  }
}
