/**
 * Shared TypeScript types for JarvisX cross-platform apps
 */

// Device types
export type DeviceType = 'desktop' | 'mobile' | 'web';
export type Platform = 'macos' | 'windows' | 'linux' | 'ios' | 'android';

// Auth types
export interface AuthCredentials {
  email: string;
  password: string;
  deviceId: string;
  deviceType: DeviceType;
  platform: Platform;
}

export interface AuthToken {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  userId: string;
  deviceId: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'guest';
  permissions: string[];
  devices: RegisteredDevice[];
  createdAt: string;
}

export interface RegisteredDevice {
  id: string;
  type: DeviceType;
  platform: Platform;
  name: string;
  lastActive: string;
  isOnline: boolean;
}

// Task types
export interface Task {
  id: string;
  userId: string;
  type: string;
  status: 'pending' | 'approved' | 'running' | 'completed' | 'failed';
  input: any;
  output?: any;
  error?: string;
  createdAt: string;
  updatedAt: string;
  executedBy?: string; // deviceId that executed it
}

// Avatar types
export interface AvatarState {
  currentEmotion: string;
  emotionIntensity: number;
  isListening: boolean;
  isSpeaking: boolean;
  isThinking: boolean;
  lipSyncData: number[];
  position?: { x: number; y: number; z: number };
  visibility: boolean;
}

// Voice types
export interface VoiceCommand {
  id: string;
  text: string;
  language: 'si' | 'en';
  confidence: number;
  timestamp: string;
}

export interface VoiceSynthesis {
  text: string;
  language: 'si' | 'en';
  emotion?: string;
  speed?: number;
  pitch?: number;
}

// Sync types
export interface SyncEvent {
  id: string;
  type: 'task_update' | 'avatar_update' | 'voice_command' | 'screen_stream' | 'permission_request';
  data: any;
  deviceId: string;
  timestamp: string;
}

// Screen streaming
export interface ScreenStreamConfig {
  deviceId: string;
  quality: 'low' | 'medium' | 'high';
  fps: number;
  enableAudio: boolean;
}

// Permissions
export interface Permission {
  resource: string;
  action: string;
  granted: boolean;
}

// Config
export interface JarvisXConfig {
  apiUrl: string;
  wsUrl: string;
  deviceId: string;
  deviceType: DeviceType;
  platform: Platform;
  enableOfflineMode: boolean;
  enableLocalWhisper: boolean;
  enableAvatar: boolean;
}

