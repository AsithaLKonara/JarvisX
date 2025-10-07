/**
 * Avatar State Manager
 * Manages the current state of the avatar including emotion, position, and activity
 */

export interface AvatarState {
  currentEmotion: string;
  emotionIntensity: number;
  isListening: boolean;
  isSpeaking: boolean;
  isThinking: boolean;
  lipSyncData: number[];
  animation: any;
  position: { x: number; y: number; z: number };
  rotation: { x: number; y: number; z: number };
  scale: number;
  visibility: boolean;
  joiMode: boolean; // Holographic effect enabled
  ambientLighting: {
    enabled: boolean;
    color: string;
    intensity: number;
  };
  lastUpdate: string;
}

export class AvatarStateManager {
  private state: AvatarState;
  private stateHistory: AvatarState[] = [];
  private maxHistorySize: number = 100;

  constructor() {
    this.state = this.getDefaultState();
  }

  /**
   * Get default avatar state
   */
  private getDefaultState(): AvatarState {
    return {
      currentEmotion: 'optimistic',
      emotionIntensity: 0.7,
      isListening: false,
      isSpeaking: false,
      isThinking: false,
      lipSyncData: [],
      animation: null,
      position: { x: 0, y: 0, z: 0 },
      rotation: { x: 0, y: 0, z: 0 },
      scale: 1.0,
      visibility: true,
      joiMode: true,
      ambientLighting: {
        enabled: true,
        color: '#3B82F6',
        intensity: 0.7
      },
      lastUpdate: new Date().toISOString()
    };
  }

  /**
   * Get current avatar state
   */
  getState(): AvatarState {
    return { ...this.state };
  }

  /**
   * Update avatar state
   */
  updateState(updates: Partial<AvatarState>): void {
    // Save current state to history
    this.stateHistory.push({ ...this.state });
    
    // Trim history if too large
    if (this.stateHistory.length > this.maxHistorySize) {
      this.stateHistory.shift();
    }

    // Apply updates
    this.state = {
      ...this.state,
      ...updates,
      lastUpdate: new Date().toISOString()
    };

    // Auto-update ambient lighting color based on emotion
    if (updates.currentEmotion) {
      this.state.ambientLighting.color = this.getEmotionColor(updates.currentEmotion);
    }
  }

  /**
   * Set emotion
   */
  setEmotion(emotion: string, intensity: number = 0.7): void {
    this.updateState({
      currentEmotion: emotion,
      emotionIntensity: intensity
    });
  }

  /**
   * Set speaking state with lip-sync data
   */
  setSpeaking(isSpeaking: boolean, lipSyncData?: number[]): void {
    this.updateState({
      isSpeaking,
      lipSyncData: lipSyncData || [],
      isListening: false // Can't listen while speaking
    });
  }

  /**
   * Set listening state
   */
  setListening(isListening: boolean): void {
    this.updateState({
      isListening,
      isSpeaking: false // Can't speak while listening
    });
  }

  /**
   * Set thinking state
   */
  setThinking(isThinking: boolean): void {
    this.updateState({
      isThinking
    });
  }

  /**
   * Set animation
   */
  setAnimation(animation: any): void {
    this.updateState({
      animation
    });
  }

  /**
   * Set avatar position
   */
  setPosition(x: number, y: number, z: number): void {
    this.updateState({
      position: { x, y, z }
    });
  }

  /**
   * Set avatar rotation
   */
  setRotation(x: number, y: number, z: number): void {
    this.updateState({
      rotation: { x, y, z }
    });
  }

  /**
   * Set avatar scale
   */
  setScale(scale: number): void {
    this.updateState({
      scale: Math.max(0.1, Math.min(3.0, scale)) // Clamp between 0.1 and 3.0
    });
  }

  /**
   * Set avatar visibility
   */
  setVisibility(visible: boolean): void {
    this.updateState({
      visibility: visible
    });
  }

  /**
   * Toggle Joi holographic mode
   */
  toggleJoiMode(): void {
    this.updateState({
      joiMode: !this.state.joiMode
    });
  }

  /**
   * Set ambient lighting
   */
  setAmbientLighting(enabled: boolean, color?: string, intensity?: number): void {
    this.updateState({
      ambientLighting: {
        enabled,
        color: color || this.state.ambientLighting.color,
        intensity: intensity !== undefined ? intensity : this.state.ambientLighting.intensity
      }
    });
  }

  /**
   * Reset avatar to idle state
   */
  resetToIdle(): void {
    this.updateState({
      isListening: false,
      isSpeaking: false,
      isThinking: false,
      lipSyncData: [],
      currentEmotion: 'optimistic',
      emotionIntensity: 0.7
    });
  }

  /**
   * Get state history
   */
  getStateHistory(limit?: number): AvatarState[] {
    if (limit) {
      return this.stateHistory.slice(-limit);
    }
    return [...this.stateHistory];
  }

  /**
   * Clear state history
   */
  clearHistory(): void {
    this.stateHistory = [];
  }

  /**
   * Revert to previous state
   */
  revertToPreviousState(): boolean {
    if (this.stateHistory.length === 0) {
      return false;
    }

    const previousState = this.stateHistory.pop();
    if (previousState) {
      this.state = previousState;
      return true;
    }

    return false;
  }

  /**
   * Get emotion color
   */
  private getEmotionColor(emotion: string): string {
    const emotionColors: { [key: string]: string } = {
      'happy': '#10B981',
      'excited': '#F59E0B',
      'concerned': '#EF4444',
      'confident': '#3B82F6',
      'curious': '#8B5CF6',
      'proud': '#EC4899',
      'grateful': '#06B6D4',
      'optimistic': '#84CC16',
      'neutral': '#6B7280'
    };

    return emotionColors[emotion] || '#3B82F6';
  }

  /**
   * Export state as JSON
   */
  exportState(): string {
    return JSON.stringify(this.state, null, 2);
  }

  /**
   * Import state from JSON
   */
  importState(stateJson: string): boolean {
    try {
      const importedState = JSON.parse(stateJson);
      this.updateState(importedState);
      return true;
    } catch (error) {
      console.error('❌ Failed to import state:', error);
      return false;
    }
  }

  /**
   * Get state summary
   */
  getSummary(): string {
    return `Avatar State: ${this.state.currentEmotion} (${Math.round(this.state.emotionIntensity * 100)}%) | ` +
           `Speaking: ${this.state.isSpeaking} | Listening: ${this.state.isListening} | ` +
           `Visible: ${this.state.visibility} | Joi Mode: ${this.state.joiMode}`;
  }
}

export default AvatarStateManager;

