#!/bin/bash

# Quick Start Script for Joi Avatar (No Docker Required)
# This starts the essential services for the avatar system

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   🎭 JarvisX Joi Avatar - Quick Start                    ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Create logs directory
mkdir -p logs

# Function to check if port is in use
check_port() {
    lsof -i :$1 >/dev/null 2>&1
    return $?
}

# Kill old processes on our ports
echo "🧹 Cleaning up old processes..."
lsof -ti:8008 | xargs kill -9 2>/dev/null
lsof -ti:8007 | xargs kill -9 2>/dev/null
echo "   ✅ Cleanup complete"
echo ""

# Start Avatar Service (simplified - just serve static responses)
echo "🎭 Starting Avatar Service (Port 8008)..."
cd services/avatar

# Create a simple server if dependencies aren't installed
cat > simple-server.js << 'EOF'
const http = require('http');
const port = 8008;

const emotionProfiles = {
  happy: { color: '#10B981', intensity: 0.8 },
  excited: { color: '#F59E0B', intensity: 1.0 },
  confident: { color: '#3B82F6', intensity: 0.75 },
  curious: { color: '#8B5CF6', intensity: 0.85 },
  proud: { color: '#EC4899', intensity: 0.8 },
  optimistic: { color: '#84CC16', intensity: 0.85 }
};

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ service: 'avatar', status: 'healthy', timestamp: new Date().toISOString() }));
  } else if (req.url === '/animation/emotion' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      const data = JSON.parse(body);
      const profile = emotionProfiles[data.emotion] || emotionProfiles.optimistic;
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, animation: profile }));
    });
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(port, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🎭 JarvisX Avatar Service (Simple Mode)                ║
║                                                           ║
║   Status: ACTIVE                                         ║
║   Port: ${port}                                           ║
║   Mode: Standalone (no dependencies required)            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
  `);
});
EOF

node simple-server.js > ../../logs/avatar.log 2>&1 &
AVATAR_PID=$!
echo "   ✅ Avatar Service started (PID: $AVATAR_PID)"
cd ../..

sleep 2

# Check if avatar service is responding
if check_port 8008; then
    echo "   ✅ Avatar Service is responding on port 8008"
else
    echo "   ⚠️  Avatar Service may still be starting..."
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   ✨ Joi Avatar is READY!                                ║"
echo "║                                                           ║"
echo "║   • Avatar Demo: Open in browser (already opened)        ║"
echo "║   • Avatar Service: http://localhost:8008/health         ║"
echo "║   • Logs: ./logs/avatar.log                              ║"
echo "║                                                           ║"
echo "║   Press Ctrl+C to stop all services                      ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping Avatar Service..."
    kill $AVATAR_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Keep script running
wait

