#!/bin/bash

# JarvisX Joi Avatar - Quick Start Script
# This script starts all necessary services for the Joi Avatar

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   🎭 Starting JarvisX Joi Avatar System                  ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the JarvisX root directory"
    exit 1
fi

# Start Avatar Service
echo "🎭 Starting Avatar Service (Port 8008)..."
cd services/avatar
npm run dev > ../../logs/avatar.log 2>&1 &
AVATAR_PID=$!
echo "   ✅ Avatar Service started (PID: $AVATAR_PID)"
cd ../..

# Wait a bit for avatar service to initialize
sleep 3

# Start Personality Service (if not running)
echo "🧠 Starting Personality Service (Port 8007)..."
cd services/personality
npm run dev > ../../logs/personality.log 2>&1 &
PERSONALITY_PID=$!
echo "   ✅ Personality Service started (PID: $PERSONALITY_PID)"
cd ../..

# Wait for services to be ready
sleep 5

# Start Desktop App
echo "🖥️  Starting Desktop App with Joi Avatar..."
cd apps/desktop
npm run dev

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $AVATAR_PID $PERSONALITY_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

wait

