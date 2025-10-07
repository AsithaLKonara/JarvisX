/**
 * Ambient Lighting System
 * Syncs RGB/smart lighting with avatar emotions (supports Philips Hue, LIFX, etc.)
 */

import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';

interface AmbientLightingProps {
  emotionColor: string;
  intensity: number;
  enabled?: boolean;
  syncMode?: 'screen' | 'smart_lights' | 'both';
}

interface LightConfig {
  type: 'hue' | 'lifx' | 'homekit' | 'screen';
  bridgeIp?: string;
  apiKey?: string;
  lightIds?: string[];
}

export function AmbientLighting({
  emotionColor,
  intensity,
  enabled = true,
  syncMode = 'screen'
}: AmbientLightingProps) {
  const [screenGlow, setScreenGlow] = useState(emotionColor);
  const [lightConfig, setLightConfig] = useState<LightConfig | null>(null);
  const animationRef = useRef<number>();

  /**
   * Update screen glow effect
   */
  useEffect(() => {
    if (!enabled) return;

    // Smooth color transition
    setScreenGlow(emotionColor);

    // Create ambient glow animation
    if (syncMode === 'screen' || syncMode === 'both') {
      animateScreenGlow();
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [emotionColor, intensity, enabled, syncMode]);

  /**
   * Sync with smart lights
   */
  useEffect(() => {
    if (!enabled || !lightConfig) return;

    if (syncMode === 'smart_lights' || syncMode === 'both') {
      syncSmartLights();
    }
  }, [emotionColor, intensity, enabled, syncMode, lightConfig]);

  /**
   * Animate screen glow
   */
  const animateScreenGlow = () => {
    let phase = 0;
    
    const animate = () => {
      phase += 0.02;
      const pulseIntensity = intensity + Math.sin(phase) * 0.1;
      
      // Update CSS custom property for global glow effect
      document.documentElement.style.setProperty('--avatar-glow-color', emotionColor);
      document.documentElement.style.setProperty('--avatar-glow-intensity', `${pulseIntensity}`);
      
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();
  };

  /**
   * Sync with smart lights (Philips Hue example)
   */
  const syncSmartLights = async () => {
    if (!lightConfig) return;

    try {
      switch (lightConfig.type) {
        case 'hue':
          await syncPhilipsHue();
          break;
        case 'lifx':
          await syncLIFX();
          break;
        default:
          console.log('Smart light type not supported yet');
      }
    } catch (error) {
      console.error('❌ Failed to sync smart lights:', error);
    }
  };

  /**
   * Sync with Philips Hue
   */
  const syncPhilipsHue = async () => {
    if (!lightConfig?.bridgeIp || !lightConfig?.apiKey) return;

    const rgb = hexToRgb(emotionColor);
    const xy = rgbToXY(rgb.r, rgb.g, rgb.b);

    const lightIds = lightConfig.lightIds || ['1', '2', '3'];

    for (const lightId of lightIds) {
      try {
        await axios.put(
          `http://${lightConfig.bridgeIp}/api/${lightConfig.apiKey}/lights/${lightId}/state`,
          {
            on: true,
            xy: [xy.x, xy.y],
            bri: Math.round(intensity * 254),
            transitiontime: 10 // 1 second transition
          }
        );
      } catch (error) {
        console.error(`❌ Failed to update Hue light ${lightId}:`, error);
      }
    }
  };

  /**
   * Sync with LIFX
   */
  const syncLIFX = async () => {
    // LIFX API implementation
    console.log('LIFX sync not yet implemented');
  };

  /**
   * Convert hex color to RGB
   */
  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : { r: 0, g: 0, b: 0 };
  };

  /**
   * Convert RGB to Philips Hue XY color space
   */
  const rgbToXY = (r: number, g: number, b: number) => {
    // Normalize RGB values
    r = r / 255;
    g = g / 255;
    b = b / 255;

    // Apply gamma correction
    r = (r > 0.04045) ? Math.pow((r + 0.055) / 1.055, 2.4) : (r / 12.92);
    g = (g > 0.04045) ? Math.pow((g + 0.055) / 1.055, 2.4) : (g / 12.92);
    b = (b > 0.04045) ? Math.pow((b + 0.055) / 1.055, 2.4) : (b / 12.92);

    // Convert to XYZ
    const X = r * 0.664511 + g * 0.154324 + b * 0.162028;
    const Y = r * 0.283881 + g * 0.668433 + b * 0.047685;
    const Z = r * 0.000088 + g * 0.072310 + b * 0.986039;

    // Convert to xy
    const x = X / (X + Y + Z);
    const y = Y / (X + Y + Z);

    return { x, y };
  };

  /**
   * Setup light configuration
   */
  const setupLightConfig = async (config: LightConfig) => {
    setLightConfig(config);
  };

  return (
    <>
      {/* Screen glow overlay */}
      {enabled && (syncMode === 'screen' || syncMode === 'both') && (
        <div
          className="ambient-lighting-overlay fixed inset-0 pointer-events-none z-0"
          style={{
            background: `radial-gradient(circle at 50% 50%, ${emotionColor}${Math.round(intensity * 25).toString(16).padStart(2, '0')} 0%, transparent 70%)`,
            mixBlendMode: 'screen',
            transition: 'background 1s ease-in-out'
          }}
        />
      )}

      {/* Corner accent lights */}
      {enabled && (
        <>
          <div
            className="fixed top-0 left-0 w-64 h-64 pointer-events-none z-0"
            style={{
              background: `radial-gradient(circle at 0% 0%, ${emotionColor}${Math.round(intensity * 40).toString(16).padStart(2, '0')} 0%, transparent 70%)`,
              filter: 'blur(80px)',
              transition: 'background 1s ease-in-out'
            }}
          />
          <div
            className="fixed top-0 right-0 w-64 h-64 pointer-events-none z-0"
            style={{
              background: `radial-gradient(circle at 100% 0%, ${emotionColor}${Math.round(intensity * 40).toString(16).padStart(2, '0')} 0%, transparent 70%)`,
              filter: 'blur(80px)',
              transition: 'background 1s ease-in-out'
            }}
          />
          <div
            className="fixed bottom-0 left-0 w-64 h-64 pointer-events-none z-0"
            style={{
              background: `radial-gradient(circle at 0% 100%, ${emotionColor}${Math.round(intensity * 40).toString(16).padStart(2, '0')} 0%, transparent 70%)`,
              filter: 'blur(80px)',
              transition: 'background 1s ease-in-out'
            }}
          />
          <div
            className="fixed bottom-0 right-0 w-64 h-64 pointer-events-none z-0"
            style={{
              background: `radial-gradient(circle at 100% 100%, ${emotionColor}${Math.round(intensity * 40).toString(16).padStart(2, '0')} 0%, transparent 70%)`,
              filter: 'blur(80px)',
              transition: 'background 1s ease-in-out'
            }}
          />
        </>
      )}

      {/* CSS for global glow effects */}
      <style jsx global>{`
        :root {
          --avatar-glow-color: ${emotionColor};
          --avatar-glow-intensity: ${intensity};
        }

        .avatar-glow-effect {
          box-shadow: 0 0 30px var(--avatar-glow-color),
                      0 0 60px var(--avatar-glow-color),
                      0 0 90px var(--avatar-glow-color);
          filter: brightness(calc(1 + var(--avatar-glow-intensity) * 0.3));
        }

        @keyframes avatar-pulse {
          0%, 100% {
            opacity: calc(var(--avatar-glow-intensity) * 0.8);
          }
          50% {
            opacity: var(--avatar-glow-intensity);
          }
        }
      `}</style>
    </>
  );
}

// Export utility function for setting up smart lights
export async function setupSmartLights(type: 'hue' | 'lifx' | 'homekit'): Promise<LightConfig | null> {
  switch (type) {
    case 'hue':
      // Auto-discover Philips Hue bridge
      try {
        const response = await axios.get('https://discovery.meethue.com/');
        if (response.data && response.data.length > 0) {
          const bridgeIp = response.data[0].internalipaddress;
          console.log('🌈 Found Philips Hue bridge:', bridgeIp);
          
          // User needs to press the bridge button and then create API key
          // This should be done through a setup flow in the UI
          return {
            type: 'hue',
            bridgeIp,
            apiKey: '', // Will be filled during setup
            lightIds: []
          };
        }
      } catch (error) {
        console.error('❌ Failed to discover Hue bridge:', error);
      }
      break;

    case 'lifx':
      // LIFX setup
      console.log('LIFX setup not yet implemented');
      break;

    case 'homekit':
      // HomeKit setup
      console.log('HomeKit setup not yet implemented');
      break;
  }

  return null;
}

export default AmbientLighting;

