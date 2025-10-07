/**
 * Emotion Animation Mapper
 * Maps emotional states to avatar animations and expressions
 */

export interface EmotionAnimationRequest {
  emotion: string;
  intensity: number;
  duration: number;
}

export interface AnimationKeyframe {
  timestamp: number;
  headRotation: { x: number; y: number; z: number };
  eyeScale: { left: number; right: number };
  mouthScale: number;
  blinkRate: number;
  breathingRate: number;
  bodyLanguage: string;
  microExpression?: string;
}

export interface EmotionAnimation {
  emotion: string;
  intensity: number;
  duration: number;
  keyframes: AnimationKeyframe[];
  color: string;
  glowIntensity: number;
  particleEffect: string;
}

/**
 * Emotion to animation characteristics mapping
 */
const EMOTION_PROFILES = {
  happy: {
    color: '#10B981',
    headMovement: { amplitude: 0.08, speed: 1.2 },
    eyeScale: { base: 1.1, variation: 0.15 },
    mouthScale: { base: 0.7, variation: 0.2 },
    blinkRate: 0.4,
    breathingRate: 1.1,
    bodyLanguage: 'open',
    microExpressions: ['smile', 'sparkle', 'joy'],
    glowIntensity: 0.8,
    particleEffect: 'sparkles'
  },
  excited: {
    color: '#F59E0B',
    headMovement: { amplitude: 0.12, speed: 1.8 },
    eyeScale: { base: 1.2, variation: 0.25 },
    mouthScale: { base: 0.8, variation: 0.3 },
    blinkRate: 0.5,
    breathingRate: 1.4,
    bodyLanguage: 'energetic',
    microExpressions: ['wide_eyes', 'grin', 'bounce'],
    glowIntensity: 1.0,
    particleEffect: 'burst'
  },
  concerned: {
    color: '#EF4444',
    headMovement: { amplitude: 0.04, speed: 0.8 },
    eyeScale: { base: 0.95, variation: 0.1 },
    mouthScale: { base: 0.35, variation: 0.05 },
    blinkRate: 0.6,
    breathingRate: 1.2,
    bodyLanguage: 'tense',
    microExpressions: ['frown', 'tilt', 'worry'],
    glowIntensity: 0.6,
    particleEffect: 'pulse'
  },
  confident: {
    color: '#3B82F6',
    headMovement: { amplitude: 0.06, speed: 1.0 },
    eyeScale: { base: 1.05, variation: 0.1 },
    mouthScale: { base: 0.5, variation: 0.15 },
    blinkRate: 0.3,
    breathingRate: 0.9,
    bodyLanguage: 'strong',
    microExpressions: ['smirk', 'nod', 'assured'],
    glowIntensity: 0.75,
    particleEffect: 'steady'
  },
  curious: {
    color: '#8B5CF6',
    headMovement: { amplitude: 0.1, speed: 1.3 },
    eyeScale: { base: 1.15, variation: 0.2 },
    mouthScale: { base: 0.45, variation: 0.1 },
    blinkRate: 0.45,
    breathingRate: 1.0,
    bodyLanguage: 'interested',
    microExpressions: ['raised_brow', 'tilt', 'wonder'],
    glowIntensity: 0.85,
    particleEffect: 'swirl'
  },
  proud: {
    color: '#EC4899',
    headMovement: { amplitude: 0.05, speed: 0.9 },
    eyeScale: { base: 1.0, variation: 0.12 },
    mouthScale: { base: 0.6, variation: 0.15 },
    blinkRate: 0.35,
    breathingRate: 0.95,
    bodyLanguage: 'upright',
    microExpressions: ['smile', 'chest_out', 'satisfied'],
    glowIntensity: 0.8,
    particleEffect: 'glow'
  },
  grateful: {
    color: '#06B6D4',
    headMovement: { amplitude: 0.06, speed: 0.85 },
    eyeScale: { base: 1.05, variation: 0.1 },
    mouthScale: { base: 0.55, variation: 0.12 },
    blinkRate: 0.4,
    breathingRate: 0.9,
    bodyLanguage: 'warm',
    microExpressions: ['soft_smile', 'bow', 'appreciate'],
    glowIntensity: 0.7,
    particleEffect: 'gentle'
  },
  optimistic: {
    color: '#84CC16',
    headMovement: { amplitude: 0.07, speed: 1.1 },
    eyeScale: { base: 1.08, variation: 0.15 },
    mouthScale: { base: 0.6, variation: 0.18 },
    blinkRate: 0.38,
    breathingRate: 1.05,
    bodyLanguage: 'forward',
    microExpressions: ['bright_eyes', 'smile', 'hopeful'],
    glowIntensity: 0.85,
    particleEffect: 'rise'
  },
  neutral: {
    color: '#6B7280',
    headMovement: { amplitude: 0.03, speed: 0.7 },
    eyeScale: { base: 1.0, variation: 0.05 },
    mouthScale: { base: 0.4, variation: 0.05 },
    blinkRate: 0.3,
    breathingRate: 0.85,
    bodyLanguage: 'relaxed',
    microExpressions: ['calm', 'attentive'],
    glowIntensity: 0.5,
    particleEffect: 'ambient'
  }
};

export class EmotionAnimationMapper {
  private fps: number = 30;

  constructor() {}

  /**
   * Generate animation sequence from emotion
   */
  async generateAnimation(request: EmotionAnimationRequest): Promise<EmotionAnimation> {
    const profile = EMOTION_PROFILES[request.emotion as keyof typeof EMOTION_PROFILES] 
                    || EMOTION_PROFILES.neutral;

    const keyframes = this.generateKeyframes(profile, request.intensity, request.duration);

    return {
      emotion: request.emotion,
      intensity: request.intensity,
      duration: request.duration,
      keyframes,
      color: profile.color,
      glowIntensity: profile.glowIntensity * request.intensity,
      particleEffect: profile.particleEffect
    };
  }

  /**
   * Generate animation keyframes based on emotion profile
   */
  private generateKeyframes(
    profile: any,
    intensity: number,
    duration: number
  ): AnimationKeyframe[] {
    const keyframes: AnimationKeyframe[] = [];
    const totalFrames = Math.floor(duration * this.fps);

    for (let frame = 0; frame < totalFrames; frame++) {
      const timestamp = frame / this.fps;
      const progress = frame / totalFrames;

      // Generate head rotation with sinusoidal movement
      const headX = Math.sin(timestamp * profile.headMovement.speed * 2) 
                    * profile.headMovement.amplitude * intensity;
      const headY = Math.cos(timestamp * profile.headMovement.speed * 1.5) 
                    * profile.headMovement.amplitude * intensity;
      const headZ = Math.sin(timestamp * profile.headMovement.speed) 
                    * profile.headMovement.amplitude * 0.5 * intensity;

      // Generate eye scale with subtle variation
      const eyeVariation = Math.sin(timestamp * 3) * profile.eyeScale.variation;
      const eyeLeft = profile.eyeScale.base + eyeVariation;
      const eyeRight = profile.eyeScale.base + eyeVariation;

      // Generate mouth scale
      const mouthVariation = Math.cos(timestamp * 2) * profile.mouthScale.variation;
      const mouthScale = profile.mouthScale.base + mouthVariation * intensity;

      // Micro-expression selection (changes periodically)
      const microExpressionIndex = Math.floor(timestamp * 0.5) % profile.microExpressions.length;
      const microExpression = profile.microExpressions[microExpressionIndex];

      keyframes.push({
        timestamp,
        headRotation: { x: headX, y: headY, z: headZ },
        eyeScale: { left: eyeLeft, right: eyeRight },
        mouthScale,
        blinkRate: profile.blinkRate,
        breathingRate: profile.breathingRate,
        bodyLanguage: profile.bodyLanguage,
        microExpression
      });
    }

    return keyframes;
  }

  /**
   * Blend between two emotions
   */
  async blendEmotions(
    emotionA: string,
    emotionB: string,
    blendFactor: number,
    duration: number
  ): Promise<EmotionAnimation> {
    const profileA = EMOTION_PROFILES[emotionA as keyof typeof EMOTION_PROFILES] 
                     || EMOTION_PROFILES.neutral;
    const profileB = EMOTION_PROFILES[emotionB as keyof typeof EMOTION_PROFILES] 
                     || EMOTION_PROFILES.neutral;

    // Blend characteristics
    const blendedProfile = {
      color: this.blendColors(profileA.color, profileB.color, blendFactor),
      headMovement: {
        amplitude: this.lerp(profileA.headMovement.amplitude, profileB.headMovement.amplitude, blendFactor),
        speed: this.lerp(profileA.headMovement.speed, profileB.headMovement.speed, blendFactor)
      },
      eyeScale: {
        base: this.lerp(profileA.eyeScale.base, profileB.eyeScale.base, blendFactor),
        variation: this.lerp(profileA.eyeScale.variation, profileB.eyeScale.variation, blendFactor)
      },
      mouthScale: {
        base: this.lerp(profileA.mouthScale.base, profileB.mouthScale.base, blendFactor),
        variation: this.lerp(profileA.mouthScale.variation, profileB.mouthScale.variation, blendFactor)
      },
      blinkRate: this.lerp(profileA.blinkRate, profileB.blinkRate, blendFactor),
      breathingRate: this.lerp(profileA.breathingRate, profileB.breathingRate, blendFactor),
      bodyLanguage: blendFactor < 0.5 ? profileA.bodyLanguage : profileB.bodyLanguage,
      microExpressions: [...profileA.microExpressions, ...profileB.microExpressions],
      glowIntensity: this.lerp(profileA.glowIntensity, profileB.glowIntensity, blendFactor),
      particleEffect: blendFactor < 0.5 ? profileA.particleEffect : profileB.particleEffect
    };

    const keyframes = this.generateKeyframes(blendedProfile, 1.0, duration);

    return {
      emotion: `${emotionA}_to_${emotionB}`,
      intensity: 1.0,
      duration,
      keyframes,
      color: blendedProfile.color,
      glowIntensity: blendedProfile.glowIntensity,
      particleEffect: blendedProfile.particleEffect
    };
  }

  /**
   * Linear interpolation
   */
  private lerp(a: number, b: number, t: number): number {
    return a + (b - a) * t;
  }

  /**
   * Blend two hex colors
   */
  private blendColors(colorA: string, colorB: string, factor: number): string {
    const hexToRgb = (hex: string) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      } : { r: 0, g: 0, b: 0 };
    };

    const rgbToHex = (r: number, g: number, b: number) => {
      return '#' + [r, g, b].map(x => {
        const hex = Math.round(x).toString(16);
        return hex.length === 1 ? '0' + hex : hex;
      }).join('');
    };

    const rgbA = hexToRgb(colorA);
    const rgbB = hexToRgb(colorB);

    const r = this.lerp(rgbA.r, rgbB.r, factor);
    const g = this.lerp(rgbA.g, rgbB.g, factor);
    const b = this.lerp(rgbA.b, rgbB.b, factor);

    return rgbToHex(r, g, b);
  }

  /**
   * Get emotion profile for reference
   */
  getEmotionProfile(emotion: string): any {
    return EMOTION_PROFILES[emotion as keyof typeof EMOTION_PROFILES] || EMOTION_PROFILES.neutral;
  }

  /**
   * Get all available emotions
   */
  getAvailableEmotions(): string[] {
    return Object.keys(EMOTION_PROFILES);
  }
}

export default EmotionAnimationMapper;

