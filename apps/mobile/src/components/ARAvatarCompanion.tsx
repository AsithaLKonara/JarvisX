/**
 * AR Avatar Companion - Mobile AR implementation
 * Projects Joi avatar in real space using ARKit/ARCore
 */

import React, { useEffect, useState, useRef } from 'react';
import { View, StyleSheet, Dimensions, Platform, TouchableOpacity, Text } from 'react-native';
import { Canvas, useFrame } from '@react-three/fiber/native';
import { useGLTF, Environment, Float } from '@react-three/drei/native';
import * as THREE from 'three';

interface ARAvatarCompanionProps {
  emotionColor: string;
  isListening: boolean;
  isSpeaking: boolean;
  lipSyncData?: number[];
  onAvatarTap?: () => void;
}

/**
 * Simplified 3D Avatar for Mobile AR
 */
function MobileAvatar({
  emotionColor,
  isListening,
  isSpeaking,
  lipSyncData
}: Omit<ARAvatarCompanionProps, 'onAvatarTap'>) {
  const meshRef = useRef<THREE.Mesh>(null);
  const headRef = useRef<THREE.Group>(null);
  const mouthRef = useRef<THREE.Mesh>(null);
  
  const [breathingPhase, setBreathingPhase] = useState(0);

  useFrame((state, delta) => {
    if (!meshRef.current) return;

    // Breathing animation
    const breathing = Math.sin(breathingPhase) * 0.02;
    setBreathingPhase((prev) => prev + delta * 0.5);
    meshRef.current.scale.setScalar(1 + breathing);

    // Head idle motion
    if (headRef.current) {
      headRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.1;
      headRef.current.rotation.x = Math.cos(state.clock.elapsedTime * 0.2) * 0.05;
    }

    // Lip sync
    if (isSpeaking && mouthRef.current && lipSyncData && lipSyncData.length > 0) {
      const index = Math.floor(state.clock.elapsedTime * 10) % lipSyncData.length;
      const mouthOpen = lipSyncData[index] || 0;
      mouthRef.current.scale.y = 0.3 + mouthOpen * 0.7;
    } else if (mouthRef.current) {
      mouthRef.current.scale.y = 0.3;
    }
  });

  return (
    <group ref={meshRef as any} scale={0.5}>
      {/* Head */}
      <group ref={headRef as any}>
        <mesh>
          <sphereGeometry args={[1, 24, 24]} />
          <meshStandardMaterial
            color={emotionColor}
            emissive={emotionColor}
            emissiveIntensity={0.5}
            transparent
            opacity={0.85}
          />
        </mesh>

        {/* Eyes */}
        <mesh position={[-0.25, 0.15, 0.8]}>
          <sphereGeometry args={[0.1, 12, 12]} />
          <meshStandardMaterial
            color="#ffffff"
            emissive="#4d9eff"
            emissiveIntensity={1.2}
          />
        </mesh>
        <mesh position={[0.25, 0.15, 0.8]}>
          <sphereGeometry args={[0.1, 12, 12]} />
          <meshStandardMaterial
            color="#ffffff"
            emissive="#4d9eff"
            emissiveIntensity={1.2}
          />
        </mesh>

        {/* Mouth */}
        <mesh ref={mouthRef as any} position={[0, -0.15, 0.85]} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.15, 0.04, 8, 12]} />
          <meshStandardMaterial
            color="#ff4d6d"
            emissive="#ff1744"
            emissiveIntensity={isSpeaking ? 0.6 : 0.2}
          />
        </mesh>
      </group>

      {/* Holographic base */}
      <mesh position={[0, -1.2, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[1.2, 32]} />
        <meshStandardMaterial
          color={emotionColor}
          emissive={emotionColor}
          emissiveIntensity={0.6}
          transparent
          opacity={0.15}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
}

/**
 * Main AR Avatar Companion Component
 */
export function ARAvatarCompanion({
  emotionColor,
  isListening,
  isSpeaking,
  lipSyncData,
  onAvatarTap
}: ARAvatarCompanionProps) {
  const [isARSupported, setIsARSupported] = useState(false);
  const [arMode, setArMode] = useState<'ar' | '3d'>('3d');

  useEffect(() => {
    checkARSupport();
  }, []);

  /**
   * Check if AR is supported on this device
   */
  const checkARSupport = async () => {
    // ARKit is available on iOS 11+
    // ARCore is available on Android 7.0+
    const supported = Platform.OS === 'ios' 
      ? Platform.Version >= '11.0'
      : Platform.Version >= 24; // Android 7.0

    setIsARSupported(supported);
  };

  /**
   * Toggle between AR and 3D mode
   */
  const toggleARMode = () => {
    if (!isARSupported) return;
    setArMode(arMode === 'ar' ? '3d' : 'ar');
  };

  return (
    <View style={styles.container}>
      {/* 3D Avatar Canvas */}
      <Canvas
        camera={{ position: [0, 0, 3], fov: 50 }}
        gl={{ antialias: true, alpha: true }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <pointLight 
          position={[3, 3, 3]} 
          intensity={0.8} 
          color={emotionColor}
        />
        <pointLight 
          position={[-3, 2, -3]} 
          intensity={0.4} 
          color={emotionColor}
        />

        {/* Environment */}
        <Environment preset="city" />

        {/* Avatar with floating effect */}
        <Float
          speed={1.2}
          rotationIntensity={0.15}
          floatIntensity={0.4}
          floatingRange={[-0.1, 0.1]}
        >
          <MobileAvatar
            emotionColor={emotionColor}
            isListening={isListening}
            isSpeaking={isSpeaking}
            lipSyncData={lipSyncData}
          />
        </Float>
      </Canvas>

      {/* AR Mode Toggle (if supported) */}
      {isARSupported && (
        <TouchableOpacity 
          style={styles.arToggle}
          onPress={toggleARMode}
        >
          <Text style={styles.arToggleText}>
            {arMode === 'ar' ? '3D' : 'AR'} Mode
          </Text>
        </TouchableOpacity>
      )}

      {/* Status Indicator */}
      {isListening && (
        <View style={styles.statusIndicator}>
          <View style={[styles.statusDot, { backgroundColor: '#3B82F6' }]} />
          <Text style={styles.statusText}>Listening...</Text>
        </View>
      )}

      {isSpeaking && (
        <View style={styles.statusIndicator}>
          <View style={[styles.statusDot, { backgroundColor: '#8B5CF6' }]} />
          <Text style={styles.statusText}>Speaking...</Text>
        </View>
      )}

      {/* Tap handler */}
      <TouchableOpacity 
        style={StyleSheet.absoluteFill}
        activeOpacity={0.9}
        onPress={onAvatarTap}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  arToggle: {
    position: 'absolute',
    top: 20,
    right: 20,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  arToggleText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  statusIndicator: {
    position: 'absolute',
    top: 20,
    left: 20,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '500',
  },
});

export default ARAvatarCompanion;

