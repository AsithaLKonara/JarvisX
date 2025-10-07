# 🐳 Docker Installation & JarvisX Quick Start

## ✅ Docker Desktop Installation in Progress

Docker Desktop 4.25.0 is currently being installed on your Mac!

### Complete These Steps:

1. **Accept Admin Prompt** ⚠️
   - You should see a macOS admin password prompt
   - Enter your password to allow Docker installation

2. **Complete Docker Desktop Setup**
   - Docker Desktop will open automatically
   - Accept the license agreement
   - Optionally skip the tutorial
   - Wait for "Docker Desktop is running" indicator

3. **Verify Installation**
   ```bash
   docker --version
   docker-compose --version
   ```

---

## 🚀 Starting JarvisX with Docker

Once Docker is installed and running, start JarvisX:

### Option 1: Start All Services (Recommended)

```bash
cd /Users/asithalakmal/Documents/web/JarvisX
docker-compose up -d
```

This will start:
- **Orchestrator** (port 3000) - Central brain
- **Avatar Service** (port 8008) - 3D avatar & animations
- **Personality Engine** (port 8007) - Emotional intelligence  
- **STT Service** (port 8001) - Speech-to-text
- **TTS Service** (port 8002) - Text-to-speech
- **Self-Training** (port 8006) - Autonomous learning
- **PC Agent, Trading, WhatsApp** - Other services

### Option 2: Start Individual Services

```bash
# Start just the avatar service
docker-compose up -d avatar

# Start personality + avatar
docker-compose up -d personality avatar

# View logs
docker-compose logs -f avatar
```

### Check Service Status

```bash
# See all running containers
docker-compose ps

# Check avatar service health
curl http://localhost:8008/health

# Check personality service
curl http://localhost:8007/health
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop specific service
docker-compose stop avatar
```

---

## 🎭 Starting the Joi Avatar

### With Docker (After Installation)

```bash
# 1. Start all services
docker-compose up -d

# 2. Wait for services to be healthy (30 seconds)
sleep 30

# 3. Start the desktop app
cd apps/desktop
npm install
npm run dev
```

### Without Docker (Manual)

```bash
# 1. Install avatar service dependencies
cd services/avatar
npm install

# 2. Start avatar service
npm run dev

# 3. In another terminal - start desktop app
cd apps/desktop
npm install
npm run dev
```

---

## 🔧 Docker Troubleshooting

### Docker Desktop Not Starting

1. **Check if Docker daemon is running**:
   ```bash
   ps aux | grep -i docker
   ```

2. **Start Docker Desktop manually**:
   - Open `/Applications/Docker.app`
   - Or use Spotlight: `Cmd + Space`, type "Docker"

3. **Check Docker status**:
   ```bash
   docker info
   ```

### Permission Issues

If you see permission errors:

```bash
# Add your user to docker group (usually not needed on Mac)
sudo dw groupadd docker
sudo usermod -aG docker $USER

# Restart Docker Desktop
```

### Port Conflicts

If ports are already in use:

```bash
# Check what's using port 8008
lsof -i :8008

# Kill the process if needed
kill -9 <PID>
```

---

## 📦 What Gets Installed

When you run `docker-compose up`:

```
┌─────────────────────────────────────────────┐
│       JarvisX Docker Environment            │
├─────────────────────────────────────────────┤
│                                             │
│  🎯 Orchestrator         → Port 3000       │
│  🎭 Avatar Service       → Port 8008       │
│  🧠 Personality Engine   → Port 8007       │
│  🎤 STT Service          → Port 8001       │
│  🔊 TTS Service          → Port 8002       │
│  🧠 Self-Training        → Port 8006       │
│  🤖 PC Agent             → Port varies      │
│  💰 Trading Service      → Port varies      │
│  📞 WhatsApp Service     → Port 8003       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🎨 Next Steps After Docker Installation

1. **Start Docker Desktop** (should auto-start)

2. **Verify Docker Works**:
   ```bash
   docker run hello-world
   ```

3. **Start JarvisX Services**:
   ```bash
   cd /Users/asithalakmal/Documents/web/JarvisX
   docker-compose up -d
   ```

4. **Launch the Joi Avatar**:
   ```bash
   cd apps/desktop
   npm run dev
   ```

5. **See Your Avatar Come to Life!** 🎉

---

## 💡 Useful Docker Commands

```bash
# View all containers
docker ps -a

# View logs for a specific service
docker-compose logs -f avatar

# Restart a service
docker-compose restart avatar

# Rebuild after code changes
docker-compose build avatar

# Remove all containers and volumes
docker-compose down -v

# Clean up unused Docker resources
docker system prune -a
```

---

## 🎭 Testing Your Joi Avatar

Once everything is running:

### Test Avatar Service

```bash
# Check avatar service health
curl http://localhost:8008/health

# Test emotion animation
curl -X POST http://localhost:8008/animation/emotion \
  -H "Content-Type: application/json" \
  -d '{"emotion":"happy","intensity":0.9,"duration":3.0}'

# Test lip-sync
curl -X POST http://localhost:8008/lipsync/process \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, I am Joi!","duration":2.0}'
```

### Open Desktop App

The desktop app will connect to all services and show your beautiful 3D Joi avatar! ✨

---

## 🆘 Need Help?

- **Docker Installation Issues**: See troubleshooting section above
- **Service Won't Start**: Check `docker-compose logs <service-name>`
- **Avatar Not Rendering**: See `AVATAR_SETUP_GUIDE.md`
- **General Issues**: See `JOI_AVATAR_COMPLETE.md`

---

## 🎉 You're Almost There!

After Docker installation completes:
1. ✅ Docker Desktop will be running
2. ✅ You can start JarvisX services with one command
3. ✅ Your Joi avatar will come to life in the desktop app

**Welcome to the future!** 🌟

---

*Built with ❤️ for JarvisX*

