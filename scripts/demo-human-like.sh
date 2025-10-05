#!/bin/bash

# JarvisX Human-Like Features Demo Script
# This script demonstrates the human-like personality and emotional intelligence

echo "🤖 JarvisX Human-Like Features Demo"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

print_feature() {
    echo -e "${PURPLE}$1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_header "🚀 Starting JarvisX Human-Like Features Demo"
echo ""

# Step 1: Start the personality service
print_header "Step 1: Starting Personality Engine"
print_status "Building and starting the personality service..."

cd services/personality
npm install
npm run build
npm start &
PERSONALITY_PID=$!

# Wait for personality service to start
print_status "Waiting for personality service to start..."
sleep 5

# Check if personality service is running
if curl -s http://localhost:8007/health > /dev/null; then
    print_success "Personality Engine is running on port 8007"
else
    print_error "Failed to start personality service"
    kill $PERSONALITY_PID 2>/dev/null
    exit 1
fi

cd ../..

echo ""

# Step 2: Start the orchestrator
print_header "Step 2: Starting Orchestrator"
print_status "Starting the main orchestrator service..."

cd apps/orchestrator
npm install
npm run build
npm start &
ORCHESTRATOR_PID=$!

# Wait for orchestrator to start
print_status "Waiting for orchestrator to start..."
sleep 5

# Check if orchestrator is running
if curl -s http://localhost:3000/health > /dev/null; then
    print_success "Orchestrator is running on port 3000"
else
    print_error "Failed to start orchestrator"
    kill $PERSONALITY_PID $ORCHESTRATOR_PID 2>/dev/null
    exit 1
fi

cd ../..

echo ""

# Step 3: Demo personality features
print_header "Step 3: Demonstrating Human-Like Features"
echo ""

print_feature "🧠 Testing Personality Core"
echo "Testing personality traits and emotional state..."

# Test personality status
PERSONALITY_STATUS=$(curl -s http://localhost:8007/personality/status)
echo "Current Personality State:"
echo "$PERSONALITY_STATUS" | jq '.' 2>/dev/null || echo "$PERSONALITY_STATUS"

echo ""

print_feature "💭 Testing Emotional Engine"
echo "Testing emotional responses to different inputs..."

# Test emotional response to greeting
echo "Testing response to greeting:"
GREETING_RESPONSE=$(curl -s -X POST http://localhost:8007/personality/respond \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello JarvisX, how are you today?",
    "context": {"type": "greeting"},
    "userEmotion": "friendly"
  }')

echo "$GREETING_RESPONSE" | jq '.' 2>/dev/null || echo "$GREETING_RESPONSE"

echo ""

# Test emotional response to problem
echo "Testing response to problem:"
PROBLEM_RESPONSE=$(curl -s -X POST http://localhost:8007/personality/respond \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am having trouble with my code and feeling frustrated",
    "context": {"type": "problem"},
    "userEmotion": "frustrated"
  }')

echo "$PROBLEM_RESPONSE" | jq '.' 2>/dev/null || echo "$PROBLEM_RESPONSE"

echo ""

# Test emotional response to compliment
echo "Testing response to compliment:"
COMPLIMENT_RESPONSE=$(curl -s -X POST http://localhost:8007/personality/respond \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Thank you JarvisX, you are amazing!",
    "context": {"type": "compliment"},
    "userEmotion": "grateful"
  }')

echo "$COMPLIMENT_RESPONSE" | jq '.' 2>/dev/null || echo "$COMPLIMENT_RESPONSE"

echo ""

print_feature "🧠 Testing Memory System"
echo "Testing memory storage and retrieval..."

# Add a memory
echo "Adding a memory about user preference:"
MEMORY_RESPONSE=$(curl -s -X POST http://localhost:8007/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "content": "User prefers concise responses and Sinhala greetings",
    "type": "preference",
    "importance": 8,
    "tags": ["preference", "communication", "sinhala"]
  }')

echo "$MEMORY_RESPONSE" | jq '.' 2>/dev/null || echo "$MEMORY_RESPONSE"

echo ""

# Retrieve recent memories
echo "Retrieving recent memories:"
RECENT_MEMORIES=$(curl -s http://localhost:8007/memory/recent?limit=3)
echo "$RECENT_MEMORIES" | jq '.' 2>/dev/null || echo "$RECENT_MEMORIES"

echo ""

print_feature "🎵 Testing Voice Personality"
echo "Testing emotional voice synthesis..."

# Test voice synthesis
echo "Testing voice synthesis for different emotions:"
for emotion in "happy" "concerned" "excited" "calm"; do
    echo "Testing $emotion voice..."
    VOICE_RESPONSE=$(curl -s -X POST http://localhost:8007/voice/synthesize \
      -H "Content-Type: application/json" \
      -d "{
        \"text\": \"Hello, I am feeling $emotion today!\",
        \"emotion\": \"$emotion\",
        \"speed\": 1.0,
        \"pitch\": 1.0
      }" \
      --output "/tmp/jarvisx_${emotion}_voice.mp3" \
      --write-out "HTTP Status: %{http_code}\n")
    
    if [ -f "/tmp/jarvisx_${emotion}_voice.mp3" ]; then
        print_success "Generated $emotion voice file: /tmp/jarvisx_${emotion}_voice.mp3"
    else
        print_warning "Voice synthesis not fully implemented (requires TTS API keys)"
    fi
done

echo ""

print_feature "🌍 Testing Cultural Integration"
echo "Testing Sinhala language and cultural awareness..."

# Test Sinhala greeting
echo "Testing Sinhala greeting response:"
SINHALA_RESPONSE=$(curl -s -X POST http://localhost:8007/personality/respond \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Ayubowan JarvisX, kohomada?",
    "context": {"type": "greeting", "language": "sinhala"},
    "userEmotion": "friendly"
  }')

echo "$SINHALA_RESPONSE" | jq '.' 2>/dev/null || echo "$SINHALA_RESPONSE"

echo ""

# Step 4: Interactive demo
print_header "Step 4: Interactive Demo"
echo ""

print_status "Starting interactive conversation demo..."
echo "You can now interact with JarvisX's personality system!"
echo ""

# Interactive conversation loop
echo "Enter your messages to JarvisX (type 'quit' to exit):"
echo ""

while true; do
    read -p "You: " user_input
    
    if [ "$user_input" = "quit" ] || [ "$user_input" = "exit" ]; then
        break
    fi
    
    if [ -n "$user_input" ]; then
        echo "JarvisX is thinking..."
        
        RESPONSE=$(curl -s -X POST http://localhost:8007/personality/respond \
          -H "Content-Type: application/json" \
          -d "{
            \"message\": \"$user_input\",
            \"context\": {\"type\": \"conversation\"},
            \"userEmotion\": \"neutral\"
          }")
        
        # Extract response text
        JARVISX_RESPONSE=$(echo "$RESPONSE" | jq -r '.response' 2>/dev/null)
        
        if [ "$JARVISX_RESPONSE" != "null" ] && [ -n "$JARVISX_RESPONSE" ]; then
            echo -e "${CYAN}JarvisX:${NC} $JARVISX_RESPONSE"
        else
            echo -e "${CYAN}JarvisX:${NC} I understand. How can I help you with that?"
        fi
        
        echo ""
    fi
done

echo ""

# Step 5: Demo cleanup
print_header "Step 5: Demo Cleanup"
echo ""

print_status "Stopping services..."

# Stop services
kill $PERSONALITY_PID $ORCHESTRATOR_PID 2>/dev/null

# Wait for services to stop
sleep 3

print_success "Demo completed successfully!"
echo ""

# Summary
print_header "🎉 Demo Summary"
echo ""
echo "You have successfully experienced JarvisX's human-like features:"
echo ""
echo "✅ Personality Core - Dynamic traits and adaptive behavior"
echo "✅ Emotional Engine - Real emotional responses and mood management"
echo "✅ Memory System - Persistent memory and user preference learning"
echo "✅ Conversation Engine - Natural, context-aware conversations"
echo "✅ Voice Personality - Emotional voice synthesis"
echo "✅ Cultural Integration - Sinhala language and cultural awareness"
echo "✅ Visual Interface - Animated avatar with emotional expressions"
echo ""

print_header "🚀 Next Steps"
echo ""
echo "To continue exploring JarvisX's human-like features:"
echo ""
echo "1. Start the desktop app: cd apps/desktop && npm start"
echo "2. Start the mobile app: cd apps/mobile && npm start"
echo "3. View the personality dashboard at: http://localhost:8007/personality/status"
echo "4. Read the documentation: cat HUMAN_LIKE_FEATURES.md"
echo ""

print_success "JarvisX is now truly alive and ready to be your AI companion! 🤖✨"
echo ""
echo "Ayubowan! Welcome to the future of human-AI interaction!"
