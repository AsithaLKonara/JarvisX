/**
 * Action Event Service for JarvisX PC Agent
 * Tracks and streams user interactions and system events
 */

import { EventEmitter } from 'events';

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
    timestamp?: string;
    type?: 'mouse' | 'keyboard' | 'system' | 'voice' | 'web';
    confidence?: number;
    error?: string;
  };
  timestamp: string;
}

export interface UserInteraction {
  type: 'click' | 'keypress' | 'scroll' | 'drag' | 'focus' | 'hover';
  target?: string;
  position?: { x: number; y: number };
  value?: string;
  timestamp: number;
  sessionId?: string;
}

export class ActionEventService extends EventEmitter {
  private eventHistory: ActionEvent[] = [];
  private interactionHistory: UserInteraction[] = [];
  private currentStepId: number = 0;
  private activeSessionId: string | null = null;
  private isMonitoring: boolean = false;
  private eventBuffer: ActionEvent[] = [];
  private maxHistorySize: number = 1000;

  constructor() {
    super();
    this.startMonitoring();
  }

  public startMonitoring(): void {
    if (this.isMonitoring) return;
    
    this.isMonitoring = true;
    console.log('👁️ Started action event monitoring');
    
    // Start monitoring system events
    this.monitorSystemEvents();
  }

  public stopMonitoring(): void {
    this.isMonitoring = false;
    console.log('👁️ Stopped action event monitoring');
  }

  public startSession(sessionId: string): void {
    this.activeSessionId = sessionId;
    this.currentStepId = 0;
    this.eventHistory = [];
    this.interactionHistory = [];
    
    console.log(`🎬 Started session: ${sessionId}`);
    
    // Emit session start event
    this.emitActionEvent({
      sessionId,
      stepId: 0,
      action: 'session_started',
      status: 'completed',
      timestamp: new Date().toISOString(),
      meta: {
        type: 'system',
        log: `Session ${sessionId} started`
      }
    });
  }

  public endSession(): void {
    if (!this.activeSessionId) return;
    
    const sessionId = this.activeSessionId;
    
    // Emit session end event
    this.emitActionEvent({
      sessionId,
      stepId: this.currentStepId + 1,
      action: 'session_ended',
      status: 'completed',
      timestamp: new Date().toISOString(),
      meta: {
        type: 'system',
        log: `Session ${sessionId} ended`
      }
    });
    
    this.activeSessionId = null;
    this.currentStepId = 0;
    
    console.log(`🎬 Ended session: ${sessionId}`);
  }

  public emitActionEvent(event: ActionEvent): void {
    // Add to history
    this.eventHistory.push(event);
    
    // Maintain history size limit
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory = this.eventHistory.slice(-this.maxHistorySize);
    }
    
    // Add to buffer for real-time streaming
    this.eventBuffer.push(event);
    
    // Emit to listeners
    this.emit('actionEvent', event);
    
    console.log(`📡 Action event: ${event.action} (${event.status})`);
  }

  public recordUserInteraction(interaction: UserInteraction): void {
    interaction.sessionId = this.activeSessionId || undefined;
    interaction.timestamp = Date.now();
    
    // Add to interaction history
    this.interactionHistory.push(interaction);
    
    // Maintain history size limit
    if (this.interactionHistory.length > this.maxHistorySize) {
      this.interactionHistory = this.interactionHistory.slice(-this.maxHistorySize);
    }
    
    // Emit interaction event
    this.emit('userInteraction', interaction);
    
    console.log(`👤 User interaction: ${interaction.type} at (${interaction.position?.x}, ${interaction.position?.y})`);
  }

  public createActionEvent(
    action: string,
    status: ActionEvent['status'],
    meta?: ActionEvent['meta']
  ): ActionEvent {
    if (!this.activeSessionId) {
      throw new Error('No active session');
    }
    
    this.currentStepId++;
    
    const event: ActionEvent = {
      sessionId: this.activeSessionId,
      stepId: this.currentStepId,
      action,
      status,
      timestamp: new Date().toISOString(),
      meta: {
        timestamp: Date.now().toString(),
        type: 'system',
        ...meta
      }
    };
    
    return event;
  }

  public recordMouseAction(
    action: string,
    x: number,
    y: number,
    button?: string,
    status: ActionEvent['status'] = 'completed'
  ): void {
    const event = this.createActionEvent(
      `mouse_${action}`,
      status,
      {
        type: 'mouse',
        log: `Mouse ${action} at (${x}, ${y})${button ? ` with ${button} button` : ''}`,
        cursor: { x, y }
      }
    );
    
    this.emitActionEvent(event);
    
    // Also record as user interaction
    this.recordUserInteraction({
      type: action as any,
      position: { x, y },
      timestamp: Date.now()
    });
  }

  public recordKeyboardAction(
    action: string,
    key: string,
    modifiers?: string[],
    status: ActionEvent['status'] = 'completed'
  ): void {
    const event = this.createActionEvent(
      `keyboard_${action}`,
      status,
      {
        type: 'keyboard',
        log: `Keyboard ${action}: ${modifiers ? modifiers.join('+') + '+' : ''}${key}`,
        confidence: 1.0
      }
    );
    
    this.emitActionEvent(event);
    
    // Also record as user interaction
    this.recordUserInteraction({
      type: 'keypress',
      value: key,
      timestamp: Date.now()
    });
  }

  public recordSystemAction(
    action: string,
    command?: string,
    status: ActionEvent['status'] = 'completed',
    error?: string
  ): void {
    const event = this.createActionEvent(
      `system_${action}`,
      status,
      {
        type: 'system',
        log: command ? `System ${action}: ${command}` : `System ${action}`,
        error: error,
        confidence: status === 'completed' ? 1.0 : 0.0
      }
    );
    
    this.emitActionEvent(event);
  }

  public recordWebAction(
    action: string,
    url?: string,
    selector?: string,
    status: ActionEvent['status'] = 'completed'
  ): void {
    const event = this.createActionEvent(
      `web_${action}`,
      status,
      {
        type: 'web',
        log: `Web ${action}${url ? ` on ${url}` : ''}${selector ? ` targeting ${selector}` : ''}`,
        confidence: status === 'completed' ? 0.9 : 0.0
      }
    );
    
    if (selector) {
      event.selector = selector;
    }
    
    this.emitActionEvent(event);
  }

  public recordVoiceAction(
    action: string,
    text?: string,
    confidence?: number,
    status: ActionEvent['status'] = 'completed'
  ): void {
    const event = this.createActionEvent(
      `voice_${action}`,
      status,
      {
        type: 'voice',
        log: `Voice ${action}${text ? `: "${text}"` : ''}`,
        confidence: confidence || 0.8
      }
    );
    
    this.emitActionEvent(event);
  }

  private monitorSystemEvents(): void {
    // Monitor clipboard changes
    let lastClipboard = '';
    setInterval(() => {
      try {
        const currentClipboard = this.getClipboard();
        if (currentClipboard !== lastClipboard) {
          lastClipboard = currentClipboard;
          this.recordSystemAction('clipboard_change', undefined, 'completed');
        }
      } catch (error) {
        // Clipboard access might not be available
      }
    }, 1000);

    // Monitor window focus changes
    let lastActiveWindow = '';
    setInterval(() => {
      try {
        const currentWindow = this.getActiveWindow();
        if (currentWindow !== lastActiveWindow) {
          lastActiveWindow = currentWindow;
          this.recordSystemAction('window_focus_change', currentWindow, 'completed');
        }
      } catch (error) {
        // Window monitoring might not be available
      }
    }, 2000);

    // Monitor application launches
    setInterval(() => {
      try {
        this.monitorApplicationLaunches();
      } catch (error) {
        // Application monitoring might not be available
      }
    }, 5000);
  }

  private getClipboard(): string {
    // Platform-specific clipboard access
    // This is a simplified implementation
    return '';
  }

  private getActiveWindow(): string {
    // Platform-specific active window detection
    // This is a simplified implementation
    return '';
  }

  private monitorApplicationLaunches(): void {
    // Monitor for new application launches
    // This would be platform-specific implementation
  }

  public getEventHistory(sessionId?: string): ActionEvent[] {
    if (sessionId) {
      return this.eventHistory.filter(event => event.sessionId === sessionId);
    }
    return [...this.eventHistory];
  }

  public getInteractionHistory(sessionId?: string): UserInteraction[] {
    if (sessionId) {
      return this.interactionHistory.filter(interaction => interaction.sessionId === sessionId);
    }
    return [...this.interactionHistory];
  }

  public getEventBuffer(): ActionEvent[] {
    const buffer = [...this.eventBuffer];
    this.eventBuffer = []; // Clear buffer after reading
    return buffer;
  }

  public getSessionStats(sessionId: string): any {
    const sessionEvents = this.getEventHistory(sessionId);
    const sessionInteractions = this.getInteractionHistory(sessionId);
    
    const stats = {
      sessionId,
      totalEvents: sessionEvents.length,
      totalInteractions: sessionInteractions.length,
      eventTypes: {} as Record<string, number>,
      interactionTypes: {} as Record<string, number>,
      duration: 0,
      startTime: null as Date | null,
      endTime: null as Date | null
    };
    
    // Count event types
    sessionEvents.forEach(event => {
      stats.eventTypes[event.action] = (stats.eventTypes[event.action] || 0) + 1;
    });
    
    // Count interaction types
    sessionInteractions.forEach(interaction => {
      stats.interactionTypes[interaction.type] = (stats.interactionTypes[interaction.type] || 0) + 1;
    });
    
    // Calculate duration
    if (sessionEvents.length > 0) {
      stats.startTime = new Date(sessionEvents[0].timestamp);
      stats.endTime = new Date(sessionEvents[sessionEvents.length - 1].timestamp);
      stats.duration = stats.endTime.getTime() - stats.startTime.getTime();
    }
    
    return stats;
  }

  public clearHistory(): void {
    this.eventHistory = [];
    this.interactionHistory = [];
    this.eventBuffer = [];
    console.log('🗑️ Cleared action event history');
  }

  public exportSession(sessionId: string): any {
    const events = this.getEventHistory(sessionId);
    const interactions = this.getInteractionHistory(sessionId);
    const stats = this.getSessionStats(sessionId);
    
    return {
      sessionId,
      stats,
      events,
      interactions,
      exportedAt: new Date().toISOString()
    };
  }

  public isSessionActive(): boolean {
    return this.activeSessionId !== null;
  }

  public getActiveSessionId(): string | null {
    return this.activeSessionId;
  }

  public getCurrentStepId(): number {
    return this.currentStepId;
  }
}
