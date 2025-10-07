/**
 * JarvisX 3D Avatar Renderer - Blade Runner 2049 Joi-style Avatar
 * Real-time 3D avatar with emotion-driven animations and lip-sync
 */

import React, { useRef, useState, useEffect, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { 
  OrbitControls, 
  PerspectiveCamera, 
  Environment,
  useGLTF,
  Float,
  MeshTransmissionMaterial,
  Sparkles
} from '@react-three/drei';
import { EffectComposer, Bloom, ChromaticAberration } from '@react-three/postprocessing';
import * as THREE from 'three';
import { motion } from 'framer-motion';

interface AvatarRendererProps {
  emotionalState: {
    mood: string;
    intensity: number;
    color: string;
  };
  isListening: boolean;
  isSpeaking: boolean;
  lipSyncData?: number[];
  onAvatarClick?: () => void;
  joiMode?: boolean; // Holographic Joi effect
}

interface AvatarModelProps {
  emotionalState: {
    mood: string;
    intensity: number;
    color: string;
  };
  isListening: boolean;
  isSpeaking: boolean;
  lipSyncData?: number[];
}

/**
 * The 3D Avatar Model with emotion-driven animations
 */
function AvatarModel({ emotionalState, isListening, isSpeaking, lipSyncData }: AvatarModelProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const headRef = useRef<THREE.Group>(null);
  const eyeLeftRef = useRef<THREE.Mesh>(null);
  const eyeRightRef = useRef<THREE.Mesh>(null);
  const mouthRef = useRef<THREE.Mesh>(null);
  
  const [blinkTimer, setBlinkTimer] = useState(0);
  const [headRotation, setHeadRotation] = useState({ x: 0, y: 0, z: 0 });
  const [breathingPhase, setBreathingPhase] = useState(0);

  // Animation loop
  useFrame((state, delta) => {
    if (!meshRef.current) return;

    // Breathing animation
    setBreathingPhase((prev) => (prev + delta * 0.5) % (Math.PI * 2));
    const breathScale = 1 + Math.sin(breathingPhase) * 0.02;
    meshRef.current.scale.setScalar(breathScale);

    // Head movement - subtle idle motion
    if (headRef.current) {
      const idleX = Math.sin(state.clock.elapsedTime * 0.3) * 0.05;
      const idleY = Math.cos(state.clock.elapsedTime * 0.2) * 0.05;
      headRef.current.rotation.x = idleX + headRotation.x;
      headRef.current.rotation.y = idleY + headRotation.y;
    }

    // Eye tracking - look at camera with slight delay
    if (eyeLeftRef.current && eyeRightRef.current) {
      const lookAtX = Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
      const lookAtY = Math.cos(state.clock.elapsedTime * 0.4) * 0.05;
      
      eyeLeftRef.current.position.x = -0.15 + lookAtX;
      eyeLeftRef.current.position.y = 0.1 + lookAtY;
      eyeRightRef.current.position.x = 0.15 + lookAtX;
      eyeRightRef.current.position.y = 0.1 + lookAtY;
    }

    // Blinking
    setBlinkTimer((prev) => prev + delta);
    if (blinkTimer > 3 + Math.random() * 2) {
      // Trigger blink
      if (eyeLeftRef.current && eyeRightRef.current) {
        const blinkDuration = 0.15;
        const blinkPhase = (blinkTimer % blinkDuration) / blinkDuration;
        const blinkScale = Math.sin(blinkPhase * Math.PI);
        eyeLeftRef.current.scale.y = Math.max(0.1, 1 - blinkScale);
        eyeRightRef.current.scale.y = Math.max(0.1, 1 - blinkScale);
      }
      if (blinkTimer > 3.2) {
        setBlinkTimer(0);
        if (eyeLeftRef.current && eyeRightRef.current) {
          eyeLeftRef.current.scale.y = 1;
          eyeRightRef.current.scale.y = 1;
        }
      }
    }

    // Lip sync animation
    if (isSpeaking && mouthRef.current && lipSyncData && lipSyncData.length > 0) {
      const mouthIndex = Math.floor(state.clock.elapsedTime * 10) % lipSyncData.length;
      const mouthOpen = lipSyncData[mouthIndex] || 0;
      mouthRef.current.scale.y = 0.3 + mouthOpen * 0.7;
    } else if (mouthRef.current) {
      mouthRef.current.scale.y = 0.3;
    }

    // Listening animation - subtle pulse
    if (isListening && meshRef.current) {
      const pulse = 1 + Math.sin(state.clock.elapsedTime * 4) * 0.03;
      meshRef.current.scale.setScalar(pulse);
    }
  });

  // Convert emotion color to Three.js color
  const emotionColor = new THREE.Color(emotionalState.color);
  const glowIntensity = emotionalState.intensity / 100;

  return (
    <group ref={meshRef as any}>
      {/* Head */}
      <group ref={headRef as any} position={[0, 0, 0]}>
        {/* Face mesh */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[1, 32, 32]} />
          <meshStandardMaterial
            color={emotionColor}
            emissive={emotionColor}
            emissiveIntensity={glowIntensity * 0.5}
            metalness={0.3}
            roughness={0.4}
            transparent
            opacity={0.9}
          />
        </mesh>

        {/* Eyes */}
        <mesh ref={eyeLeftRef as any} position={[-0.3, 0.2, 0.85]}>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshStandardMaterial
            color="#ffffff"
            emissive="#4d9eff"
            emissiveIntensity={1.5}
          />
        </mesh>
        <mesh ref={eyeRightRef as any} position={[0.3, 0.2, 0.85]}>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshStandardMaterial
            color="#ffffff"
            emissive="#4d9eff"
            emissiveIntensity={1.5}
          />
        </mesh>

        {/* Eye highlights - iris */}
        <mesh position={[-0.3, 0.2, 0.95]}>
          <sphereGeometry args={[0.06, 16, 16]} />
          <meshStandardMaterial
            color="#000033"
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
        <mesh position={[0.3, 0.2, 0.95]}>
          <sphereGeometry args={[0.06, 16, 16]} />
          <meshStandardMaterial
            color="#000033"
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>

        {/* Mouth */}
        <mesh ref={mouthRef as any} position={[0, -0.2, 0.9]} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.2, 0.05, 8, 16]} />
          <meshStandardMaterial
            color="#ff4d6d"
            emissive="#ff1744"
            emissiveIntensity={isSpeaking ? 0.8 : 0.2}
          />
        </mesh>

        {/* Hair/Glow effect */}
        <mesh position={[0, 0.5, 0]} scale={[1.2, 1.4, 1]}>
          <sphereGeometry args={[0.8, 32, 32]} />
          <meshStandardMaterial
            color={emotionColor}
            emissive={emotionColor}
            emissiveIntensity={glowIntensity * 0.8}
            transparent
            opacity={0.3}
            wireframe
          />
        </mesh>
      </group>

      {/* Ambient particles around avatar */}
      <Sparkles
        count={30}
        scale={3}
        size={2}
        speed={0.4}
        color={emotionColor}
        opacity={0.6}
      />

      {/* Holographic base */}
      <mesh position={[0, -1.5, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[1.5, 64]} />
        <meshStandardMaterial
          color={emotionColor}
          emissive={emotionColor}
          emissiveIntensity={glowIntensity}
          transparent
          opacity={0.2}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
}

/**
 * Loading fallback
 */
function AvatarLoader() {
  return (
    <mesh>
      <sphereGeometry args={[1, 16, 16]} />
      <meshStandardMaterial color="#3B82F6" wireframe />
    </mesh>
  );
}

/**
 * Main Avatar Renderer Component
 */
export function AvatarRenderer({
  emotionalState,
  isListening,
  isSpeaking,
  lipSyncData,
  onAvatarClick,
  joiMode = true
}: AvatarRendererProps) {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  return (
    <motion.div
      className="avatar-renderer relative w-full h-full"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
      onClick={onAvatarClick}
    >
      <Canvas
        shadows
        dpr={[1, 2]}
        gl={{ 
          antialias: true, 
          alpha: true,
          powerPreference: 'high-performance'
        }}
      >
        {/* Camera */}
        <PerspectiveCamera makeDefault position={[0, 0, 5]} fov={50} />

        {/* Lighting */}
        <ambientLight intensity={0.3} />
        <pointLight 
          position={[5, 5, 5]} 
          intensity={1} 
          color={emotionalState.color}
        />
        <pointLight 
          position={[-5, 3, -5]} 
          intensity={0.5} 
          color={emotionalState.color}
        />
        <spotLight
          position={[0, 10, 0]}
          angle={0.3}
          penumbra={1}
          intensity={1}
          castShadow
          color={emotionalState.color}
        />

        {/* Environment */}
        <Environment preset="city" />

        {/* Avatar with floating animation */}
        <Suspense fallback={<AvatarLoader />}>
          <Float
            speed={1.5}
            rotationIntensity={0.2}
            floatIntensity={0.5}
            floatingRange={[-0.1, 0.1]}
          >
            <AvatarModel
              emotionalState={emotionalState}
              isListening={isListening}
              isSpeaking={isSpeaking}
              lipSyncData={lipSyncData}
            />
          </Float>
        </Suspense>

        {/* Post-processing effects for Joi-style holographic look */}
        {joiMode && (
          <EffectComposer>
            <Bloom 
              luminanceThreshold={0.3} 
              luminanceSmoothing={0.9} 
              intensity={1.5}
            />
            <ChromaticAberration offset={[0.001, 0.001]} />
          </EffectComposer>
        )}

        {/* Camera controls */}
        <OrbitControls
          enableZoom={false}
          enablePan={false}
          minPolarAngle={Math.PI / 3}
          maxPolarAngle={Math.PI / 1.5}
          autoRotate={false}
          autoRotateSpeed={0.5}
        />
      </Canvas>

      {/* Emotion label overlay */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 pointer-events-none">
        <motion.div
          className="px-4 py-2 rounded-full backdrop-blur-md border"
          style={{
            backgroundColor: `${emotionalState.color}20`,
            borderColor: `${emotionalState.color}60`,
          }}
          animate={{
            scale: isListening || isSpeaking ? [1, 1.05, 1] : 1,
          }}
          transition={{
            duration: 1.5,
            repeat: isListening || isSpeaking ? Infinity : 0,
          }}
        >
          <span className="text-white text-sm font-medium capitalize">
            {emotionalState.mood}
          </span>
        </motion.div>
      </div>

      {/* Status indicators */}
      {isListening && (
        <div className="absolute top-4 left-4 flex items-center gap-2 px-3 py-2 rounded-full bg-blue-500/20 backdrop-blur-md border border-blue-500/40">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
          <span className="text-blue-100 text-sm">Listening...</span>
        </div>
      )}

      {isSpeaking && (
        <div className="absolute top-4 left-4 flex items-center gap-2 px-3 py-2 rounded-full bg-purple-500/20 backdrop-blur-md border border-purple-500/40">
          <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
          <span className="text-purple-100 text-sm">Speaking...</span>
        </div>
      )}
    </motion.div>
  );
}

export default AvatarRenderer;

