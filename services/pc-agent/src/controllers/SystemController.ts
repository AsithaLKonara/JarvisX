/**
 * System Controller for JarvisX PC Agent
 * Provides full mouse, keyboard, and system control capabilities
 */

import { EventEmitter } from 'events';
import * as robot from 'robotjs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface MouseAction {
  type: 'click' | 'move' | 'scroll' | 'drag';
  x?: number;
  y?: number;
  button?: 'left' | 'right' | 'middle';
  clicks?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
  steps?: number;
}

export interface KeyboardAction {
  type: 'type' | 'key' | 'shortcut' | 'combo';
  text?: string;
  key?: string;
  modifiers?: string[];
  duration?: number;
}

export interface SystemAction {
  type: 'execute' | 'open' | 'focus' | 'minimize' | 'maximize' | 'close';
  command?: string;
  application?: string;
  window?: string;
  path?: string;
}

export interface ActionResult {
  success: boolean;
  result?: any;
  error?: string;
  timestamp: string;
  actionId: string;
}

export class SystemController extends EventEmitter {
  private isInitialized: boolean = false;
  private actionHistory: Map<string, ActionResult> = new Map();
  private isRecording: boolean = false;
  private recordingBuffer: any[] = [];

  constructor() {
    super();
    this.initialize();
  }

  private async initialize(): Promise<void> {
    try {
      console.log('🎮 Initializing System Controller...');
      
      // Configure robotjs
      robot.setMouseDelay(1);
      robot.setKeyboardDelay(1);
      
      this.isInitialized = true;
      console.log('✅ System Controller initialized');

    } catch (error) {
      console.error('❌ Failed to initialize System Controller:', error);
      throw error;
    }
  }

  public async executeCommand(command: string, params: any, sessionId?: string): Promise<ActionResult> {
    const actionId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    try {
      console.log(`🎮 Executing system command: ${command}`, params);

      let result: any;

      switch (command) {
        case 'mouse_action':
          result = await this.executeMouseAction(params as MouseAction);
          break;
        
        case 'keyboard_action':
          result = await this.executeKeyboardAction(params as KeyboardAction);
          break;
        
        case 'system_action':
          result = await this.executeSystemAction(params as SystemAction);
          break;
        
        case 'get_screen_info':
          result = await this.getScreenInfo();
          break;
        
        case 'get_window_list':
          result = await this.getWindowList();
          break;
        
        case 'focus_window':
          result = await this.focusWindow(params.windowTitle);
          break;
        
        case 'start_recording':
          result = await this.startRecording();
          break;
        
        case 'stop_recording':
          result = await this.stopRecording();
          break;
        
        case 'playback_recording':
          result = await this.playbackRecording(params.recordingId);
          break;
        
        default:
          throw new Error(`Unknown command: ${command}`);
      }

      const actionResult: ActionResult = {
        success: true,
        result,
        timestamp: new Date().toISOString(),
        actionId
      };

      this.actionHistory.set(actionId, actionResult);
      this.emit('actionExecuted', { actionId, result, sessionId });

      return actionResult;

    } catch (error: any) {
      const actionResult: ActionResult = {
        success: false,
        error: error.message,
        timestamp: new Date().toISOString(),
        actionId
      };

      this.actionHistory.set(actionId, actionResult);
      this.emit('actionFailed', { actionId, error: error.message, sessionId });

      return actionResult;
    }
  }

  private async executeMouseAction(action: MouseAction): Promise<any> {
    switch (action.type) {
      case 'click':
        if (action.x !== undefined && action.y !== undefined) {
          robot.moveMouse(action.x, action.y);
        }
        robot.mouseClick(action.button || 'left', action.clicks || 1);
        return { type: 'click', position: { x: action.x, y: action.y }, button: action.button };

      case 'move':
        robot.moveMouse(action.x || 0, action.y || 0);
        return { type: 'move', position: { x: action.x, y: action.y } };

      case 'scroll':
        robot.scrollMouse(action.direction === 'up' ? 1 : -1, action.steps || 1);
        return { type: 'scroll', direction: action.direction, steps: action.steps };

      case 'drag':
        if (action.x !== undefined && action.y !== undefined) {
          robot.dragMouse(action.x, action.y);
        }
        return { type: 'drag', position: { x: action.x, y: action.y } };

      default:
        throw new Error(`Unknown mouse action: ${action.type}`);
    }
  }

  private async executeKeyboardAction(action: KeyboardAction): Promise<any> {
    switch (action.type) {
      case 'type':
        if (action.text) {
          robot.typeString(action.text);
        }
        return { type: 'type', text: action.text };

      case 'key':
        if (action.key) {
          robot.keyTap(action.key, action.modifiers);
        }
        return { type: 'key', key: action.key, modifiers: action.modifiers };

      case 'shortcut':
        if (action.key && action.modifiers) {
          robot.keyTap(action.key, action.modifiers);
        }
        return { type: 'shortcut', key: action.key, modifiers: action.modifiers };

      case 'combo':
        // Execute key combination
        if (action.modifiers && action.key) {
          // Hold modifiers and press key
          action.modifiers.forEach(modifier => robot.keyToggle(modifier, 'down'));
          robot.keyTap(action.key);
          action.modifiers.forEach(modifier => robot.keyToggle(modifier, 'up'));
        }
        return { type: 'combo', key: action.key, modifiers: action.modifiers };

      default:
        throw new Error(`Unknown keyboard action: ${action.type}`);
    }
  }

  private async executeSystemAction(action: SystemAction): Promise<any> {
    switch (action.type) {
      case 'execute':
        if (action.command) {
          const { stdout, stderr } = await execAsync(action.command);
          return { type: 'execute', command: action.command, output: stdout, error: stderr };
        }
        break;

      case 'open':
        if (action.application) {
          // Platform-specific application opening
          const platform = process.platform;
          let command: string;
          
          switch (platform) {
            case 'darwin': // macOS
              command = `open -a "${action.application}"`;
              break;
            case 'win32': // Windows
              command = `start "${action.application}"`;
              break;
            case 'linux': // Linux
              command = `${action.application}`;
              break;
            default:
              throw new Error(`Unsupported platform: ${platform}`);
          }
          
          const { stdout, stderr } = await execAsync(command);
          return { type: 'open', application: action.application, output: stdout, error: stderr };
        }
        break;

      case 'focus':
        if (action.window) {
          return await this.focusWindow(action.window);
        }
        break;

      case 'minimize':
        robot.keyTap('m', ['command']); // macOS
        return { type: 'minimize' };

      case 'maximize':
        robot.keyTap('f', ['command']); // macOS
        return { type: 'maximize' };

      case 'close':
        robot.keyTap('q', ['command']); // macOS
        return { type: 'close' };

      default:
        throw new Error(`Unknown system action: ${action.type}`);
    }
  }

  public async getScreenInfo(): Promise<any> {
    const screenSize = robot.getScreenSize();
    const mousePos = robot.getMousePos();
    
    return {
      width: screenSize.width,
      height: screenSize.height,
      mousePosition: mousePos,
      colorDepth: robot.getPixelColor(mousePos.x, mousePos.y)
    };
  }

  public async getWindowList(): Promise<any> {
    try {
      const platform = process.platform;
      let command: string;

      switch (platform) {
        case 'darwin': // macOS
          command = `osascript -e 'tell application "System Events" to get name of every process whose visible is true'`;
          break;
        case 'win32': // Windows
          command = `tasklist /fo csv | findstr /i "window"`;
          break;
        case 'linux': // Linux
          command = `wmctrl -l`;
          break;
        default:
          throw new Error(`Unsupported platform: ${platform}`);
      }

      const { stdout } = await execAsync(command);
      return { windows: stdout.split('\n').filter(w => w.trim()) };

    } catch (error) {
      console.warn('⚠️ Failed to get window list:', error);
      return { windows: [] };
    }
  }

  public async focusWindow(windowTitle: string): Promise<any> {
    try {
      const platform = process.platform;
      let command: string;

      switch (platform) {
        case 'darwin': // macOS
          command = `osascript -e 'tell application "${windowTitle}" to activate'`;
          break;
        case 'win32': // Windows
          command = `powershell -command "Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.Interaction]::AppActivate('${windowTitle}')"`;
          break;
        case 'linux': // Linux
          command = `wmctrl -a "${windowTitle}"`;
          break;
        default:
          throw new Error(`Unsupported platform: ${platform}`);
      }

      await execAsync(command);
      return { type: 'focus', window: windowTitle };

    } catch (error) {
      console.warn('⚠️ Failed to focus window:', error);
      throw error;
    }
  }

  public async startRecording(): Promise<any> {
    this.isRecording = true;
    this.recordingBuffer = [];
    
    // Start monitoring mouse and keyboard events
    this.startEventMonitoring();
    
    return { type: 'recording_started', timestamp: new Date().toISOString() };
  }

  public async stopRecording(): Promise<any> {
    this.isRecording = false;
    
    const recording = {
      id: `recording_${Date.now()}`,
      timestamp: new Date().toISOString(),
      events: this.recordingBuffer,
      duration: Date.now() - (this.recordingBuffer[0]?.timestamp || Date.now())
    };

    return { type: 'recording_stopped', recording };
  }

  public async playbackRecording(recordingId: string): Promise<any> {
    // This would retrieve and replay a recording
    // Implementation depends on how recordings are stored
    return { type: 'playback_started', recordingId };
  }

  private startEventMonitoring(): void {
    // Monitor mouse position changes
    setInterval(() => {
      if (this.isRecording) {
        const pos = robot.getMousePos();
        this.recordingBuffer.push({
          type: 'mouse_move',
          x: pos.x,
          y: pos.y,
          timestamp: Date.now()
        });
      }
    }, 100); // Sample every 100ms
  }

  public async captureScreenshot(x?: number, y?: number, width?: number, height?: number): Promise<string> {
    try {
      if (x !== undefined && y !== undefined && width !== undefined && height !== undefined) {
        // Capture specific region
        const img = robot.screen.capture(x, y, width, height);
        return img.toDataURL(); // Convert to base64
      } else {
        // Capture full screen
        const img = robot.screen.capture();
        return img.toDataURL();
      }
    } catch (error) {
      console.error('❌ Failed to capture screenshot:', error);
      throw error;
    }
  }

  public async getPixelColor(x: number, y: number): Promise<string> {
    try {
      const color = robot.getPixelColor(x, y);
      return `#${color}`;
    } catch (error) {
      console.error('❌ Failed to get pixel color:', error);
      throw error;
    }
  }

  public getActionHistory(): Map<string, ActionResult> {
    return this.actionHistory;
  }

  public clearActionHistory(): void {
    this.actionHistory.clear();
  }

  public isReady(): boolean {
    return this.isInitialized;
  }

  // Safety methods
  public async emergencyStop(): Promise<void> {
    console.log('🛑 Emergency stop triggered - stopping all actions');
    
    // Stop any ongoing recordings
    this.isRecording = false;
    
    // Clear action history
    this.clearActionHistory();
    
    // Emit emergency stop event
    this.emit('emergencyStop');
  }

  public async validateAction(action: any): Promise<{ valid: boolean; reason?: string }> {
    // Implement safety checks for actions
    try {
      // Check if action is in whitelist
      const allowedActions = ['mouse_action', 'keyboard_action', 'system_action'];
      if (!allowedActions.includes(action.type)) {
        return { valid: false, reason: 'Action type not allowed' };
      }

      // Check for dangerous operations
      if (action.type === 'system_action' && action.command) {
        const dangerousCommands = ['rm -rf', 'del /f', 'format', 'shutdown', 'reboot'];
        const isDangerous = dangerousCommands.some(cmd => action.command.includes(cmd));
        if (isDangerous) {
          return { valid: false, reason: 'Dangerous command detected' };
        }
      }

      return { valid: true };

    } catch (error) {
      return { valid: false, reason: 'Validation error' };
    }
  }
}
