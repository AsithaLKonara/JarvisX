/**
 * Device Information Utilities
 * Platform detection and device ID generation
 */

import type { DeviceType, Platform } from '../types';

/**
 * Get current platform
 */
export function getPlatform(): Platform {
  if (typeof window !== 'undefined') {
    // Browser/Tauri environment
    const userAgent = window.navigator.userAgent.toLowerCase();
    
    if (userAgent.indexOf('mac') !== -1) return 'macos';
    if (userAgent.indexOf('win') !== -1) return 'windows';
    if (userAgent.indexOf('linux') !== -1) return 'linux';
  }

  // Node.js environment
  if (typeof process !== 'undefined') {
    const platform = process.platform;
    if (platform === 'darwin') return 'macos';
    if (platform === 'win32') return 'windows';
    if (platform === 'linux') return 'linux';
  }

  return 'linux'; // default
}

/**
 * Get device type
 */
export function getDeviceType(): DeviceType {
  // Check if React Native
  if (typeof navigator !== 'undefined' && navigator.product === 'ReactNative') {
    return 'mobile';
  }

  // Check if Tauri
  if (typeof window !== 'undefined' && (window as any).__TAURI__) {
    return 'desktop';
  }

  return 'web';
}

/**
 * Generate device ID (persistent across sessions)
 */
export function generateDeviceId(): string {
  const stored = getStoredDeviceId();
  if (stored) return stored;

  // Generate new ID
  const id = `${getPlatform()}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  storeDeviceId(id);
  return id;
}

/**
 * Get stored device ID
 */
function getStoredDeviceId(): string | null {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      return localStorage.getItem('jarvisx_device_id');
    }
  } catch (error) {
    // Storage not available
  }
  return null;
}

/**
 * Store device ID
 */
function storeDeviceId(id: string): void {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('jarvisx_device_id', id);
    }
  } catch (error) {
    console.error('Failed to store device ID:', error);
  }
}

/**
 * Get device name
 */
export function getDeviceName(): string {
  const platform = getPlatform();
  const deviceType = getDeviceType();

  if (deviceType === 'desktop') {
    return `${platform.charAt(0).toUpperCase() + platform.slice(1)} Desktop`;
  } else if (deviceType === 'mobile') {
    return `${platform === 'ios' ? 'iPhone' : 'Android'} Mobile`;
  }

  return 'Web Browser';
}

/**
 * Get full device info
 */
export function getDeviceInfo() {
  return {
    deviceId: generateDeviceId(),
    deviceType: getDeviceType(),
    platform: getPlatform(),
    deviceName: getDeviceName(),
    userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
    timestamp: new Date().toISOString()
  };
}

