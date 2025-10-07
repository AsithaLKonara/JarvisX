import React, { useRef, useEffect, useState, useMemo } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { 
  OrbitControls, 
  useGLTF, 
  Environment, 
  PerspectiveCamera,
  useAnimations
} from '@react-three/drei';
import * as THREE from 'three';

/**
 * 🎭 REALISTIC AVATAR RENDERER
 * 
 * Supports:
 * - Ready Player Me avatars
 * - Custom GLB/GLTF models
 * - Facial animations (morph targets/blend shapes)
 * - Realistic lip-sync with ARKit visemes
 * - Eye tracking and blinking
 * - Emotion-based animations
 * 
 * Celebrity Avatars:
 * You can use models that look like celebrities by:
 * 1. Using Ready Player Me with custom photo
 * 2. Importing custom GLB models from:
 *    - Sketchfab
 *    - TurboSquid
 *    - CGTrader
 *    - Custom 3D artists
 */

// ARKit Viseme Names (52 blend shapes for realistic facial animation)
const ARKIT_VISEMES = [
  'viseme_sil',    // silence
  'viseme_PP',     // p, b, m
  'viseme_FF',     // f, v
  'viseme_TH',     // th
  'viseme_DD',     // d, t, n, l
  'viseme_kk',     // k, g
  'viseme_CH',     // ch, j, sh
  'viseme_SS',     // s, z
  'viseme_nn',     // n, ng
  'viseme_RR',     // r
  'viseme_aa',     // a (cat)
  'viseme_E',      // e (bed)
  'viseme_I',      // i (sit)
  'viseme_O',      // o (hot)
  'viseme_U',      // u (book)
];

// Emotion to blend shape mapping
const EMOTION_BLEND_SHAPES = {
  happy: {
    mouthSmile: 0.7,
    eyeSquintLeft: 0.3,
    eyeSquintRight: 0.3,
    cheekSquintLeft: 0.5,
    cheekSquintRight: 0.5,
  },
  excited: {
    mouthSmile: 0.9,
    jawOpen: 0.3,
    eyeWideLeft: 0.6,
    eyeWideRight: 0.6,
    browInnerUp: 0.5,
  },
  concerned: {
    browDownLeft: 0.6,
    browDownRight: 0.6,
    mouthFrownLeft: 0.4,
    mouthFrownRight: 0.4,
  },
  confident: {
    mouthSmile: 0.4,
    headUp: 0.2,
  },
  curious: {
    browInnerUp: 0.7,
    eyeWideLeft: 0.5,
    eyeWideRight: 0.5,
    mouthOpen: 0.2,
  },
  proud: {
    mouthSmile: 0.6,
    headUp: 0.3,
    chestOut: 0.4,
  },
  grateful: {
    mouthSmile: 0.5,
    eyesClosed: 0.3,
    headDown: 0.1,
  },
  optimistic: {
    mouthSmile: 0.5,
    eyesLookUp: 0.3,
  },
  neutral: {},
};

// Phoneme to viseme mapping for lip-sync
const PHONEME_TO_VISEME: { [key: string]: string } = {
  'p': 'viseme_PP', 'b': 'viseme_PP', 'm': 'viseme_PP',
  'f': 'viseme_FF', 'v': 'viseme_FF',
  'th': 'viseme_TH',
  'd': 'viseme_DD', 't': 'viseme_DD', 'n': 'viseme_DD', 'l': 'viseme_DD',
  'k': 'viseme_kk', 'g': 'viseme_kk',
  'ch': 'viseme_CH', 'j': 'viseme_CH', 'sh': 'viseme_CH',
  's': 'viseme_SS', 'z': 'viseme_SS',
  'r': 'viseme_RR',
  'aa': 'viseme_aa', 'ae': 'viseme_aa',
  'eh': 'viseme_E', 'e': 'viseme_E',
  'ih': 'viseme_I', 'i': 'viseme_I',
  'oh': 'viseme_O', 'o': 'viseme_O',
  'uh': 'viseme_U', 'u': 'viseme_U',
};

interface RealisticAvatarProps {
  modelUrl?: string; // GLB/GLTF URL (Ready Player Me or custom)
  emotion?: string;
  intensity?: number;
  isSpeaking?: boolean;
  lipSyncData?: number[];
  currentPhoneme?: string;
  lookAt?: [number, number, number];
  className?: string;
  enablePostProcessing?: boolean;
  cameraPosition?: [number, number, number];
  cameraFov?: number;
}

interface AvatarModelProps {
  modelUrl: string;
  emotion: string;
  intensity: number;
  isSpeaking: boolean;
  lipSyncData: number[];
  currentPhoneme?: string;
  lookAt: [number, number, number];
}

function AvatarModel({
  modelUrl,
  emotion,
  intensity,
  isSpeaking,
  lipSyncData,
  currentPhoneme,
  lookAt,
}: AvatarModelProps) {
  const { scene, animations } = useGLTF(modelUrl);
  const { actions } = useAnimations(animations, scene);
  const modelRef = useRef<THREE.Group>(null);
  const headRef = useRef<THREE.Bone | null>(null);
  const leftEyeRef = useRef<THREE.Bone | null>(null);
  const rightEyeRef = useRef<THREE.Bone | null>(null);
  
  const [morphTargetDictionary, setMorphTargetDictionary] = useState<{ [key: string]: number }>({});
  const [morphTargetMeshes, setMorphTargetMeshes] = useState<THREE.Mesh[]>([]);
  const [blinkTimer, setBlinkTimer] = useState(0);
  const [nextBlinkTime, setNextBlinkTime] = useState(3);
  const [isBlinking, setIsBlinking] = useState(false);
  
  const lipSyncFrame = useRef(0);

  // Find morph target meshes and build dictionary
  useEffect(() => {
    if (!scene) return;

    const meshes: THREE.Mesh[] = [];
    let dictionary: { [key: string]: number } = {};

    scene.traverse((child) => {
      if (child instanceof THREE.Mesh && child.morphTargetDictionary) {
        meshes.push(child);
        // Merge all dictionaries
        Object.assign(dictionary, child.morphTargetDictionary);
      }

      // Find head bone for head rotation
      if (child instanceof THREE.Bone) {
        const name = child.name.toLowerCase();
        if (name.includes('head') && !headRef.current) {
          headRef.current = child;
        }
        if (name.includes('lefteye') && !leftEyeRef.current) {
          leftEyeRef.current = child;
        }
        if (name.includes('righteye') && !rightEyeRef.current) {
          rightEyeRef.current = child;
        }
      }
    });

    setMorphTargetMeshes(meshes);
    setMorphTargetDictionary(dictionary);

    console.log('🎭 Avatar morph targets found:', Object.keys(dictionary).length);
    console.log('Available blend shapes:', Object.keys(dictionary).slice(0, 20).join(', '));
  }, [scene]);

  // Apply emotion blend shapes
  useEffect(() => {
    if (morphTargetMeshes.length === 0) return;

    const emotionShapes = EMOTION_BLEND_SHAPES[emotion as keyof typeof EMOTION_BLEND_SHAPES] || {};

    morphTargetMeshes.forEach((mesh) => {
      if (!mesh.morphTargetInfluences || !mesh.morphTargetDictionary) return;

      // Reset all morph targets to 0
      mesh.morphTargetInfluences.fill(0);

      // Apply emotion blend shapes
      Object.entries(emotionShapes).forEach(([shapeName, value]) => {
        const index = mesh.morphTargetDictionary[shapeName];
        if (index !== undefined) {
          mesh.morphTargetInfluences[index] = (value as number) * intensity;
        }
      });
    });
  }, [emotion, intensity, morphTargetMeshes]);

  // Animation loop
  useFrame((state, delta) => {
    if (!modelRef.current) return;

    const time = state.clock.elapsedTime;

    // === LIP-SYNC ===
    if (isSpeaking && lipSyncData.length > 0) {
      lipSyncFrame.current = (lipSyncFrame.current + 1) % lipSyncData.length;
      const mouthOpenAmount = lipSyncData[lipSyncFrame.current];

      // Apply lip-sync to morph targets
      morphTargetMeshes.forEach((mesh) => {
        if (!mesh.morphTargetInfluences || !mesh.morphTargetDictionary) return;

        // Apply current phoneme viseme
        if (currentPhoneme) {
          const visemeName = PHONEME_TO_VISEME[currentPhoneme.toLowerCase()];
          const visemeIndex = mesh.morphTargetDictionary[visemeName];
          if (visemeIndex !== undefined) {
            mesh.morphTargetInfluences[visemeIndex] = mouthOpenAmount;
          }
        }

        // Fallback to general jaw open
        const jawOpenIndex = mesh.morphTargetDictionary['jawOpen'];
        if (jawOpenIndex !== undefined) {
          mesh.morphTargetInfluences[jawOpenIndex] = mouthOpenAmount * 0.6;
        }
      });
    }

    // === BLINKING ===
    setBlinkTimer((prev) => {
      const newTimer = prev + delta;
      
      if (newTimer >= nextBlinkTime && !isBlinking) {
        setIsBlinking(true);
        setTimeout(() => {
          setIsBlinking(false);
          setNextBlinkTime(3 + Math.random() * 3); // 3-6 seconds
        }, 150); // 150ms blink duration
      }

      if (newTimer >= nextBlinkTime + 0.15) {
        return 0;
      }

      return newTimer;
    });

    // Apply blink
    if (isBlinking) {
      morphTargetMeshes.forEach((mesh) => {
        if (!mesh.morphTargetInfluences || !mesh.morphTargetDictionary) return;

        const blinkLeftIndex = mesh.morphTargetDictionary['eyeBlinkLeft'];
        const blinkRightIndex = mesh.morphTargetDictionary['eyeBlinkRight'];
        
        if (blinkLeftIndex !== undefined) {
          mesh.morphTargetInfluences[blinkLeftIndex] = 1.0;
        }
        if (blinkRightIndex !== undefined) {
          mesh.morphTargetInfluences[blinkRightIndex] = 1.0;
        }
      });
    } else {
      // Reset blink
      morphTargetMeshes.forEach((mesh) => {
        if (!mesh.morphTargetInfluences || !mesh.morphTargetDictionary) return;

        const blinkLeftIndex = mesh.morphTargetDictionary['eyeBlinkLeft'];
        const blinkRightIndex = mesh.morphTargetDictionary['eyeBlinkRight'];
        
        if (blinkLeftIndex !== undefined) {
          mesh.morphTargetInfluences[blinkLeftIndex] = 0;
        }
        if (blinkRightIndex !== undefined) {
          mesh.morphTargetInfluences[blinkRightIndex] = 0;
        }
      });
    }

    // === HEAD ROTATION (Look At) ===
    if (headRef.current) {
      const targetPosition = new THREE.Vector3(...lookAt);
      const headWorldPosition = new THREE.Vector3();
      headRef.current.getWorldPosition(headWorldPosition);

      // Calculate look direction
      const direction = targetPosition.clone().sub(headWorldPosition).normalize();
      
      // Smooth rotation
      const targetQuaternion = new THREE.Quaternion().setFromUnitVectors(
        new THREE.Vector3(0, 1, 0),
        direction
      );

      headRef.current.quaternion.slerp(targetQuaternion, 0.1);
    }

    // === EYE TRACKING ===
    if (leftEyeRef.current && rightEyeRef.current) {
      const targetPosition = new THREE.Vector3(...lookAt);
      
      [leftEyeRef.current, rightEyeRef.current].forEach((eyeBone) => {
        const eyeWorldPosition = new THREE.Vector3();
        eyeBone.getWorldPosition(eyeWorldPosition);

        const direction = targetPosition.clone().sub(eyeWorldPosition).normalize();
        const targetQuaternion = new THREE.Quaternion().setFromUnitVectors(
          new THREE.Vector3(0, 0, 1),
          direction
        );

        eyeBone.quaternion.slerp(targetQuaternion, 0.15);
      });
    }

    // === IDLE BREATHING ANIMATION ===
    if (!isSpeaking) {
      const breathScale = 1 + Math.sin(time * Math.PI) * 0.01;
      modelRef.current.scale.set(breathScale, breathScale, breathScale);
    }
  });

  return (
    <group ref={modelRef}>
      <primitive object={scene} />
    </group>
  );
}

export default function RealisticAvatarRenderer({
  modelUrl = 'https://models.readyplayer.me/64bfa15f0e72c63d7c3934a6.glb', // Default Ready Player Me avatar
  emotion = 'neutral',
  intensity = 0.7,
  isSpeaking = false,
  lipSyncData = [],
  currentPhoneme,
  lookAt = [0, 0, 2],
  className = '',
  enablePostProcessing = true,
  cameraPosition = [0, 1.6, 3],
  cameraFov = 50,
}: RealisticAvatarProps) {
  return (
    <div className={`w-full h-full ${className}`}>
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
        <PerspectiveCamera
          makeDefault
          position={cameraPosition}
          fov={cameraFov}
        />

        {/* Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight
          position={[5, 5, 5]}
          intensity={1}
          castShadow
          shadow-mapSize={[1024, 1024]}
        />
        <directionalLight
          position={[-5, 3, -5]}
          intensity={0.5}
        />
        <spotLight
          position={[0, 5, 0]}
          angle={0.3}
          penumbra={1}
          intensity={0.5}
          castShadow
        />

        {/* Environment */}
        <Environment preset="city" />

        {/* Avatar Model */}
        <React.Suspense fallback={null}>
          <AvatarModel
            modelUrl={modelUrl}
            emotion={emotion}
            intensity={intensity}
            isSpeaking={isSpeaking}
            lipSyncData={lipSyncData}
            currentPhoneme={currentPhoneme}
            lookAt={lookAt}
          />
        </React.Suspense>

        {/* Controls */}
        <OrbitControls
          enableZoom={true}
          enablePan={true}
          minDistance={1}
          maxDistance={10}
          target={[0, 1.6, 0]}
        />
      </Canvas>

      {/* Emotion Label */}
      <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-sm px-4 py-2 rounded-lg">
        <div className="text-sm text-white/70">Emotion</div>
        <div className="text-xl font-bold text-white capitalize">{emotion}</div>
        <div className="text-xs text-white/50 mt-1">
          Intensity: {Math.round(intensity * 100)}%
        </div>
      </div>

      {/* Speaking Indicator */}
      {isSpeaking && (
        <div className="absolute bottom-4 left-4 bg-green-500/80 backdrop-blur-sm px-4 py-2 rounded-full flex items-center gap-2">
          <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
          <span className="text-white text-sm font-medium">Speaking...</span>
        </div>
      )}
    </div>
  );
}

// Preload the default model
useGLTF.preload('https://models.readyplayer.me/64bfa15f0e72c63d7c3934a6.glb');

