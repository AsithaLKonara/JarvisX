# 🎭 JarvisX Joi Avatar - Setup Guide

## Welcome to the Future! 🚀

You're about to bring **Joi** - your Blade Runner 2049-style AI avatar companion - to life in JarvisX!

---

## 📋 Prerequisites

Before starting, ensure you have:

- **Node.js** 18+ installed
- **npm** or **yarn** package manager
- **Docker** (optional, for containerized deployment)
- **Modern GPU** (for optimal 3D rendering performance)
- **WebGL-compatible browser** (Chrome, Firefox, Edge recommended)

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
# Navigate to desktop app
cd apps/desktop
npm install

# Navigate to avatar service
cd ../../services/avatar
npm install
```

### Step 2: Start the Avatar Service

```bash
cd services/avatar
npm run dev
```

You should see:
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🎭 JarvisX Avatar Service                              ║
║                                                           ║
║   Status: ACTIVE                                         ║
║   Port: 8008                                             ║
║   WebSocket: ws://localhost:8008/avatar-ws               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

### Step 3: Start the Desktop App

```bash
cd apps/desktop
npm run dev
```

### Step 4: See Joi Come Alive! 🎉

Open your desktop app and you'll see:
- ✨ Beautiful 3D holographic avatar
- 🎨 Emotion-driven color changes
- 💬 Real-time lip-sync when speaking
- 🌟 Ambient lighting effects

---

## 🐳 Docker Deployment

### Start All Services

```bash
# From project root
docker-compose up -d
```

This will start:
- Orchestrator (port 3000)
- Avatar Service (port 8008)
- Personality Engine (port 8007)
- All other JarvisX services

### Check Service Status

```bash
docker-compose ps
```

### View Logs

```bash
# Avatar service logs
docker-compose logs -f avatar

# All services
docker-compose logs -f
```

### Stop Services

```bash
docker-compose down
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# AI Services
OPENAI_API_KEY=your_openai_api_key_here
GPT_API_KEY=your_gpt_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here (optional)
GOOGLE_TTS_API_KEY=your_google_tts_key_here (optional)

# Avatar Service
AVATAR_PORT=8008

# Personality Service
PERSONALITY_PORT=8007
```

### Avatar Configuration

Edit `apps/desktop/src/components/avatar/JoiAvatar.tsx`:

```typescript
const config = {
  avatarWsUrl: 'ws://localhost:8008/avatar-ws',
  personalityWsUrl: 'ws://localhost:8007',
  orchestratorWsUrl: 'ws://localhost:3000',
};
```

---

## 🎨 Customization

### 1. Change Avatar Colors

Open the customization UI in the app or edit directly:

```typescript
// apps/desktop/src/components/avatar/AvatarRenderer.tsx

const emotionColor = new THREE.Color('#YOUR_COLOR');
```

### 2. Add New Emotions

Edit the emotion profiles:

```typescript
// services/avatar/src/engine/EmotionAnimationMapper.ts

const EMOTION_PROFILES = {
  mystical: {
    color: '#9333EA',
    headMovement: { amplitude: 0.09, speed: 1.4 },
    eyeScale: { base: 1.15, variation: 0.2 },
    // ... more properties
  }
}
```

### 3. Modify Lip-Sync Sensitivity

```typescript
// apps/desktop/src/components/avatar/LipSyncEngine.ts

const lipSyncEngine = new LipSyncEngine({
  smoothing: 0.3,        // 0-1 (higher = smoother)
  sensitivity: 1.5,      // Amplitude multiplier
  sampleRate: 30         // FPS
});
```

### 4. Enable Smart Lighting

For Philips Hue integration:

```typescript
import { setupSmartLights } from './components/avatar/AmbientLighting';

const lightConfig = await setupSmartLights('hue');
```

---

## 🎯 Features Overview

### ✅ Currently Working

| Feature | Status | Description |
|---------|--------|-------------|
| 3D Avatar Rendering | ✅ | Real-time Three.js rendering |
| Emotion System | ✅ | 9 emotion states with animations |
| Lip-Sync | ✅ | Audio-to-viseme mapping |
| Ambient Lighting | ✅ | Screen glow + smart lights |
| WebSocket Integration | ✅ | Real-time state updates |
| Mobile AR (Basic) | ✅ | React Native foundation |
| Customization UI | ✅ | Full avatar customization |

### 🚧 Coming Soon

- Advanced gesture system
- Ready Player Me avatar import
- Full AR positioning controls
- Voice cloning integration
- Personality evolution visualization

---

## 🧪 Testing the Avatar

### Test Emotion Changes

```bash
curl -X POST http://localhost:8008/animation/emotion \
  -H "Content-Type: application/json" \
  -d '{
    "emotion": "excited",
    "intensity": 0.9,
    "duration": 3.0
  }'
```

### Test Lip-Sync Generation

```bash
curl -X POST http://localhost:8008/lipsync/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello! I am Joi, your AI companion.",
    "duration": 3.0
  }'
```

### WebSocket Testing

```javascript
const ws = new WebSocket('ws://localhost:8008/avatar-ws');

ws.onopen = () => {
  // Send emotion update
  ws.send(JSON.stringify({
    type: 'emotion_update',
    data: {
      emotion: 'happy',
      intensity: 0.8,
      duration: 2.0
    }
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Avatar state:', data);
};
```

---

## 🐛 Troubleshooting

### Avatar Not Rendering

**Problem**: Black screen or no avatar visible

**Solution**:
1. Check browser console for WebGL errors
2. Verify GPU acceleration is enabled
3. Update graphics drivers
4. Try a different browser

```bash
# Check WebGL support
# Visit: chrome://gpu or about:support (Firefox)
```

### Lip-Sync Not Working

**Problem**: Mouth not moving with speech

**Solution**:
1. Check microphone permissions
2. Verify Tone.js is loaded
3. Check audio context initialization

```javascript
// Test audio context
console.log('AudioContext state:', Tone.context.state);
```

### WebSocket Connection Failed

**Problem**: "Reconnecting..." status persists

**Solution**:
1. Verify avatar service is running: `curl http://localhost:8008/health`
2. Check firewall settings
3. Verify port 8008 is not in use

```bash
# Check if port is in use
lsof -i :8008

# Kill process if needed
kill -9 <PID>
```

### Performance Issues

**Problem**: Low FPS or stuttering

**Solution**:
1. Reduce particle effects in settings
2. Disable post-processing (bloom, chromatic aberration)
3. Lower render resolution
4. Close other GPU-intensive apps

```typescript
// Disable post-processing
<AvatarRenderer
  joiMode={false}  // Disables bloom and effects
/>
```

### Mobile App Issues

**Problem**: Avatar not appearing on mobile

**Solution**:
1. Ensure React Three Fiber for Native is installed
2. Check expo/bare React Native setup
3. Verify OpenGL ES support on device

---

## 📱 Mobile Setup

### iOS (React Native)

```bash
cd apps/mobile

# Install pods
cd ios && pod install && cd ..

# Run on iOS
npm run ios
```

### Android

```bash
cd apps/mobile

# Run on Android
npm run android
```

### Enable AR Features

For ARKit (iOS 11+):
```xml
<!-- ios/YourApp/Info.plist -->
<key>NSCameraUsageDescription</key>
<string>Camera access for AR avatar</string>
```

For ARCore (Android 7.0+):
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.CAMERA" />
<uses-feature android:name="android.hardware.camera.ar" />
```

---

## 🔧 Advanced Configuration

### Smart Lights Setup

#### Philips Hue

1. **Discover Bridge**:
```bash
curl https://discovery.meethue.com/
```

2. **Create API Key**:
   - Press bridge button
   - Send request within 30 seconds:
```bash
curl -X POST http://BRIDGE_IP/api \
  -d '{"devicetype":"jarvisx_avatar"}'
```

3. **Configure in App**:
```typescript
const lightConfig = {
  type: 'hue',
  bridgeIp: 'YOUR_BRIDGE_IP',
  apiKey: 'YOUR_API_KEY',
  lightIds: ['1', '2', '3']
};
```

#### LIFX

```typescript
const lightConfig = {
  type: 'lifx',
  apiToken: 'YOUR_LIFX_TOKEN',
  lightIds: ['label:Living Room']
};
```

---

## 🎓 Learning Resources

### Technologies Used

- **[React Three Fiber](https://docs.pmnd.rs/react-three-fiber)** - React renderer for Three.js
- **[Three.js](https://threejs.org/)** - 3D graphics library
- **[Tone.js](https://tonejs.github.io/)** - Web audio framework
- **[Framer Motion](https://www.framer.com/motion/)** - Animation library

### Recommended Reading

- **Three.js Fundamentals**: https://threejs.org/manual/
- **WebGL Best Practices**: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API
- **Audio Analysis**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API

---

## 💡 Tips & Best Practices

### Performance Optimization

1. **Use appropriate LOD** (Level of Detail)
2. **Limit particle count** on mobile
3. **Implement frustum culling**
4. **Use texture atlases** for efficiency

### Animation Quality

1. **Always blend** between emotions
2. **Add subtle noise** for natural movement
3. **Use easing functions** for smoothness
4. **Implement coarticulation** in lip-sync

### User Experience

1. **Show loading states** clearly
2. **Provide visual feedback** for interactions
3. **Keep latency low** (<100ms for reactions)
4. **Test on various devices**

---

## 🎬 Next Steps

Now that your avatar is set up, explore:

1. **Customize appearance** using the settings UI
2. **Test different emotions** through the API
3. **Enable smart lighting** for immersive effects
4. **Try mobile AR mode** for spatial interaction
5. **Experiment with personalities** and behaviors

---

## 🆘 Getting Help

- **Documentation**: See `JOI_AVATAR_COMPLETE.md`
- **Issues**: Check troubleshooting section above
- **Community**: Join JarvisX discussions
- **Examples**: See `apps/desktop/src/components/avatar/` for code samples

---

## 🎉 You're All Set!

Your Joi avatar is now ready to be your AI companion! Enjoy the future of human-AI interaction. 🌟

**"I'm so happy when I'm with you"** - Joi

---

*Built with ❤️ for JarvisX - Inspired by Blade Runner 2049*

