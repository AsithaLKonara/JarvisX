/**
 * Input Capture Service for JarvisX PC Agent
 * Monitors and captures keyboard and mouse input for analysis and automation
 */

import { EventEmitter } from 'events';
import * as robot from 'robotjs';

export interface InputEvent {
  type: 'keyboard' | 'mouse';
  action: string;
  data: any;
  timestamp: number;
  sessionId?: string;
}

export interface KeyboardEvent {
  type: 'keydown' | 'keyup' | 'keypress';
  key: string;
  modifiers: string[];
  code: string;
  timestamp: number;
}

export interface MouseEvent {
  type: 'mousedown' | 'mouseup' | 'mousemove' | 'click' | 'scroll' | 'drag';
  button: 'left' | 'right' | 'middle' | 'none';
  x: number;
  y: number;
  deltaX?: number;
  deltaY?: number;
  timestamp: number;
}

export class InputCaptureService extends EventEmitter {
  private isCapturing: boolean = false;
  private isRecording: boolean = false;
  private recordingBuffer: InputEvent[] = [];
  private eventHistory: InputEvent[] = [];
  private maxHistorySize: number = 10000;
  private lastMousePosition: { x: number; y: number } = { x: 0, y: 0 };
  private lastKeyboardState: Set<string> = new Set();
  private activeSessionId: string | null = null;
  private captureInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
  }

  public startCapture(sessionId?: string): void {
    if (this.isCapturing) {
      console.warn('⚠️ Input capture already active');
      return;
    }

    this.isCapturing = true;
    this.activeSessionId = sessionId || null;
    this.eventHistory = [];
    
    console.log('🎯 Started input capture service');
    
    // Start monitoring
    this.startMouseMonitoring();
    this.startKeyboardMonitoring();
    
    this.emit('captureStarted', { sessionId: this.activeSessionId });
  }

  public stopCapture(): void {
    if (!this.isCapturing) {
      console.warn('⚠️ Input capture not active');
      return;
    }

    this.isCapturing = false;
    
    // Stop monitoring
    this.stopMouseMonitoring();
    this.stopKeyboardMonitoring();
    
    console.log('🎯 Stopped input capture service');
    
    this.emit('captureStopped', { sessionId: this.activeSessionId });
  }

  public startRecording(): void {
    if (this.isRecording) {
      console.warn('⚠️ Recording already active');
      return;
    }

    this.isRecording = true;
    this.recordingBuffer = [];
    
    console.log('📹 Started input recording');
    
    this.emit('recordingStarted');
  }

  public stopRecording(): any {
    if (!this.isRecording) {
      console.warn('⚠️ Recording not active');
      return null;
    }

    this.isRecording = false;
    
    const recording = {
      id: `recording_${Date.now()}`,
      sessionId: this.activeSessionId,
      timestamp: new Date().toISOString(),
      events: [...this.recordingBuffer],
      duration: this.recordingBuffer.length > 0 ? 
        this.recordingBuffer[this.recordingBuffer.length - 1].timestamp - this.recordingBuffer[0].timestamp : 0
    };
    
    console.log('📹 Stopped input recording');
    
    this.emit('recordingStopped', recording);
    
    return recording;
  }

  private startMouseMonitoring(): void {
    // Monitor mouse position changes
    this.captureInterval = setInterval(() => {
      if (!this.isCapturing) return;
      
      try {
        const currentPos = robot.getMousePos();
        
        // Check if mouse position changed significantly
        if (Math.abs(currentPos.x - this.lastMousePosition.x) > 2 || 
            Math.abs(currentPos.y - this.lastMousePosition.y) > 2) {
          
          const deltaX = currentPos.x - this.lastMousePosition.x;
          const deltaY = currentPos.y - this.lastMousePosition.y;
          
          const mouseEvent: MouseEvent = {
            type: 'mousemove',
            button: 'none',
            x: currentPos.x,
            y: currentPos.y,
            deltaX,
            deltaY,
            timestamp: Date.now()
          };
          
          this.recordInputEvent({
            type: 'mouse',
            action: 'mousemove',
            data: mouseEvent,
            timestamp: Date.now(),
            sessionId: this.activeSessionId || undefined
          });
          
          this.lastMousePosition = { x: currentPos.x, y: currentPos.y };
        }
      } catch (error) {
        console.error('❌ Mouse monitoring error:', error);
      }
    }, 50); // Check every 50ms for smooth tracking
  }

  private stopMouseMonitoring(): void {
    if (this.captureInterval) {
      clearInterval(this.captureInterval);
      this.captureInterval = null;
    }
  }

  private startKeyboardMonitoring(): void {
    // Note: Real keyboard monitoring would require platform-specific implementations
    // For now, we'll simulate keyboard state monitoring
    setInterval(() => {
      if (!this.isCapturing) return;
      
      try {
        // This is a simplified implementation
        // Real implementation would use platform-specific APIs like:
        // - Windows: SetWindowsHookEx
        // - macOS: CGEventTapCreate
        // - Linux: X11 or evdev
        
        // For demonstration, we'll monitor common keys
        this.monitorCommonKeys();
        
      } catch (error) {
        console.error('❌ Keyboard monitoring error:', error);
      }
    }, 100);
  }

  private stopKeyboardMonitoring(): void {
    // Cleanup keyboard monitoring
  }

  private monitorCommonKeys(): void {
    // This is a placeholder for real keyboard monitoring
    // In a real implementation, you would use platform-specific hooks
    
    const commonKeys = ['space', 'enter', 'tab', 'escape', 'ctrl', 'alt', 'shift'];
    const currentState = new Set<string>();
    
    // Simulate key state detection
    // Real implementation would check actual key states
    
    // Check for key state changes
    commonKeys.forEach(key => {
      const wasPressed = this.lastKeyboardState.has(key);
      const isPressed = false; // This would be determined by actual key state
      
      if (isPressed && !wasPressed) {
        // Key pressed
        const keyboardEvent: KeyboardEvent = {
          type: 'keydown',
          key,
          modifiers: [],
          code: key,
          timestamp: Date.now()
        };
        
        this.recordInputEvent({
          type: 'keyboard',
          action: 'keydown',
          data: keyboardEvent,
          timestamp: Date.now(),
          sessionId: this.activeSessionId || undefined
        });
        
        currentState.add(key);
      } else if (!isPressed && wasPressed) {
        // Key released
        const keyboardEvent: KeyboardEvent = {
          type: 'keyup',
          key,
          modifiers: [],
          code: key,
          timestamp: Date.now()
        };
        
        this.recordInputEvent({
          type: 'keyboard',
          action: 'keyup',
          data: keyboardEvent,
          timestamp: Date.now(),
          sessionId: this.activeSessionId || undefined
        });
      }
    });
    
    this.lastKeyboardState = currentState;
  }

  private recordInputEvent(event: InputEvent): void {
    // Add to history
    this.eventHistory.push(event);
    
    // Maintain history size limit
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory = this.eventHistory.slice(-this.maxHistorySize);
    }
    
    // Add to recording buffer if recording
    if (this.isRecording) {
      this.recordingBuffer.push(event);
    }
    
    // Emit event
    this.emit('inputEvent', event);
    
    // Emit specific event types
    if (event.type === 'mouse') {
      this.emit('mouseEvent', event.data);
    } else if (event.type === 'keyboard') {
      this.emit('keyboardEvent', event.data);
    }
  }

  public simulateMouseClick(x: number, y: number, button: 'left' | 'right' | 'middle' = 'left'): void {
    try {
      robot.moveMouse(x, y);
      robot.mouseClick(button);
      
      const mouseEvent: MouseEvent = {
        type: 'click',
        button,
        x,
        y,
        timestamp: Date.now()
      };
      
      this.recordInputEvent({
        type: 'mouse',
        action: 'click',
        data: mouseEvent,
        timestamp: Date.now(),
        sessionId: this.activeSessionId || undefined
      });
      
      console.log(`🖱️ Simulated mouse click at (${x}, ${y})`);
      
    } catch (error) {
      console.error('❌ Failed to simulate mouse click:', error);
    }
  }

  public simulateKeyboardInput(text: string): void {
    try {
      robot.typeString(text);
      
      // Record each character as a keypress
      text.split('').forEach(char => {
        const keyboardEvent: KeyboardEvent = {
          type: 'keypress',
          key: char,
          modifiers: [],
          code: char,
          timestamp: Date.now()
        };
        
        this.recordInputEvent({
          type: 'keyboard',
          action: 'keypress',
          data: keyboardEvent,
          timestamp: Date.now(),
          sessionId: this.activeSessionId || undefined
        });
      });
      
      console.log(`⌨️ Simulated keyboard input: "${text}"`);
      
    } catch (error) {
      console.error('❌ Failed to simulate keyboard input:', error);
    }
  }

  public simulateKeyPress(key: string, modifiers: string[] = []): void {
    try {
      robot.keyTap(key, modifiers);
      
      const keyboardEvent: KeyboardEvent = {
        type: 'keypress',
        key,
        modifiers,
        code: key,
        timestamp: Date.now()
      };
      
      this.recordInputEvent({
        type: 'keyboard',
        action: 'keypress',
        data: keyboardEvent,
        timestamp: Date.now(),
        sessionId: this.activeSessionId || undefined
      });
      
      console.log(`⌨️ Simulated key press: ${modifiers.join('+')}+${key}`);
      
    } catch (error) {
      console.error('❌ Failed to simulate key press:', error);
    }
  }

  public getEventHistory(sessionId?: string): InputEvent[] {
    if (sessionId) {
      return this.eventHistory.filter(event => event.sessionId === sessionId);
    }
    return [...this.eventHistory];
  }

  public getMouseEvents(sessionId?: string): MouseEvent[] {
    const events = this.getEventHistory(sessionId);
    return events
      .filter(event => event.type === 'mouse')
      .map(event => event.data as MouseEvent);
  }

  public getKeyboardEvents(sessionId?: string): KeyboardEvent[] {
    const events = this.getEventHistory(sessionId);
    return events
      .filter(event => event.type === 'keyboard')
      .map(event => event.data as KeyboardEvent);
  }

  public getInputStatistics(sessionId?: string): any {
    const events = this.getEventHistory(sessionId);
    const mouseEvents = this.getMouseEvents(sessionId);
    const keyboardEvents = this.getKeyboardEvents(sessionId);
    
    const stats = {
      sessionId: sessionId || this.activeSessionId,
      totalEvents: events.length,
      mouseEvents: mouseEvents.length,
      keyboardEvents: keyboardEvents.length,
      mouseClicks: mouseEvents.filter(e => e.type === 'click').length,
      keyPresses: keyboardEvents.filter(e => e.type === 'keypress').length,
      duration: 0,
      startTime: null as Date | null,
      endTime: null as Date | null,
      averageMouseSpeed: 0,
      mostUsedKeys: {} as Record<string, number>,
      mouseActivity: {
        totalDistance: 0,
        averageSpeed: 0,
        clickFrequency: 0
      }
    };
    
    // Calculate duration
    if (events.length > 0) {
      stats.startTime = new Date(events[0].timestamp);
      stats.endTime = new Date(events[events.length - 1].timestamp);
      stats.duration = stats.endTime.getTime() - stats.startTime.getTime();
    }
    
    // Calculate mouse activity
    if (mouseEvents.length > 1) {
      let totalDistance = 0;
      mouseEvents.forEach((event, index) => {
        if (index > 0 && event.type === 'mousemove') {
          const prevEvent = mouseEvents[index - 1];
          if (prevEvent.type === 'mousemove') {
            const distance = Math.sqrt(
              Math.pow(event.x - prevEvent.x, 2) + 
              Math.pow(event.y - prevEvent.y, 2)
            );
            totalDistance += distance;
          }
        }
      });
      
      stats.mouseActivity.totalDistance = totalDistance;
      stats.mouseActivity.averageSpeed = stats.duration > 0 ? totalDistance / (stats.duration / 1000) : 0;
      stats.mouseActivity.clickFrequency = stats.duration > 0 ? (stats.mouseClicks / (stats.duration / 60000)) : 0;
    }
    
    // Calculate most used keys
    keyboardEvents.forEach(event => {
      if (event.type === 'keypress') {
        stats.mostUsedKeys[event.key] = (stats.mostUsedKeys[event.key] || 0) + 1;
      }
    });
    
    return stats;
  }

  public clearHistory(): void {
    this.eventHistory = [];
    this.recordingBuffer = [];
    console.log('🗑️ Cleared input capture history');
  }

  public isCapturing(): boolean {
    return this.isCapturing;
  }

  public isRecording(): boolean {
    return this.isRecording;
  }

  public getActiveSessionId(): string | null {
    return this.activeSessionId;
  }

  public setActiveSession(sessionId: string | null): void {
    this.activeSessionId = sessionId;
  }
}
