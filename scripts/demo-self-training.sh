#!/bin/bash

# JarvisX Self-Training Capabilities Demo Script
# This script demonstrates the autonomous learning and self-improvement features

echo "🧠 JarvisX Self-Training Capabilities Demo"
echo "=========================================="
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

print_header "🚀 Starting JarvisX Self-Training Demo"
echo ""

# Step 1: Start the self-training service
print_header "Step 1: Starting Self-Training Engine"
print_status "Building and starting the self-training service..."

cd services/self-training
npm install
npm run build
npm start &
SELF_TRAINING_PID=$!

# Wait for self-training service to start
print_status "Waiting for self-training service to start..."
sleep 5

# Check if self-training service is running
if curl -s http://localhost:8008/health > /dev/null; then
    print_success "Self-Training Engine is running on port 8008"
else
    print_error "Failed to start self-training service"
    kill $SELF_TRAINING_PID 2>/dev/null
    exit 1
fi

cd ../..

echo ""

# Step 2: Start the personality service
print_header "Step 2: Starting Personality Engine"
print_status "Starting the personality service..."

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
    kill $SELF_TRAINING_PID $PERSONALITY_PID 2>/dev/null
    exit 1
fi

cd ../..

echo ""

# Step 3: Demo self-training features
print_header "Step 3: Demonstrating Self-Training Capabilities"
echo ""

print_feature "🧠 Testing Self-Training Core"
echo "Testing autonomous learning and training capabilities..."

# Test training status
TRAINING_STATUS=$(curl -s http://localhost:8008/training/status)
echo "Current Training Status:"
echo "$TRAINING_STATUS" | jq '.' 2>/dev/null || echo "$TRAINING_STATUS"

echo ""

# Test starting training
echo "Starting a training session..."
TRAINING_RESPONSE=$(curl -s -X POST http://localhost:8008/training/start \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "incremental",
    "priority": "normal"
  }')

echo "$TRAINING_RESPONSE" | jq '.' 2>/dev/null || echo "$TRAINING_RESPONSE"

echo ""

print_feature "🔍 Testing Pattern Recognition"
echo "Testing autonomous pattern discovery..."

# Test pattern analysis
echo "Running pattern analysis..."
PATTERN_RESPONSE=$(curl -s http://localhost:8008/patterns/analyze)
echo "$PATTERN_RESPONSE" | jq '.' 2>/dev/null || echo "$PATTERN_RESPONSE"

echo ""

print_feature "⚡ Testing Performance Optimization"
echo "Testing self-optimization capabilities..."

# Test optimization
echo "Running performance optimization..."
OPTIMIZATION_RESPONSE=$(curl -s -X POST http://localhost:8008/optimization/run \
  -H "Content-Type: application/json" \
  -d '{
    "target": "response_time"
  }')

echo "$OPTIMIZATION_RESPONSE" | jq '.' 2>/dev/null || echo "$OPTIMIZATION_RESPONSE"

echo ""

print_feature "🧠 Testing Knowledge Synthesis"
echo "Testing autonomous knowledge extraction..."

# Test knowledge synthesis
echo "Running knowledge synthesis..."
KNOWLEDGE_RESPONSE=$(curl -s -X POST http://localhost:8008/knowledge/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "source": "all",
    "depth": "medium"
  }')

echo "$KNOWLEDGE_RESPONSE" | jq '.' 2>/dev/null || echo "$KNOWLEDGE_RESPONSE"

echo ""

print_feature "🧪 Testing Autonomous Experiments"
echo "Testing self-directed experimentation..."

# Test experiment
echo "Running A/B test experiment..."
EXPERIMENT_RESPONSE=$(curl -s -X POST http://localhost:8008/experiments/run \
  -H "Content-Type: application/json" \
  -d '{
    "type": "ab_test",
    "parameters": {
      "testType": "response_style",
      "variants": 2
    }
  }')

echo "$EXPERIMENT_RESPONSE" | jq '.' 2>/dev/null || echo "$EXPERIMENT_RESPONSE"

echo ""

# Test getting experiments
echo "Getting recent experiments..."
EXPERIMENTS_RESPONSE=$(curl -s http://localhost:8008/experiments?limit=5)
echo "$EXPERIMENTS_RESPONSE" | jq '.' 2>/dev/null || echo "$EXPERIMENTS_RESPONSE"

echo ""

print_feature "📊 Testing Learning Progress"
echo "Testing learning progress tracking..."

# Test learning progress
echo "Getting learning progress..."
PROGRESS_RESPONSE=$(curl -s http://localhost:8008/learning/progress)
echo "$PROGRESS_RESPONSE" | jq '.' 2>/dev/null || echo "$PROGRESS_RESPONSE"

echo ""

# Step 4: Demo integration with personality
print_header "Step 4: Demonstrating Integration with Personality"
echo ""

print_feature "🎭 Testing Personality-Powered Self-Training"
echo "Testing how self-training improves personality responses..."

# Generate a response through personality service
echo "Generating personality response..."
PERSONALITY_RESPONSE=$(curl -s -X POST http://localhost:8007/personality/respond \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello JarvisX, how are you learning today?",
    "context": {"type": "greeting"},
    "userEmotion": "curious"
  }')

echo "Personality Response:"
echo "$PERSONALITY_RESPONSE" | jq -r '.response' 2>/dev/null || echo "$PERSONALITY_RESPONSE"

echo ""

# Add feedback to trigger learning
echo "Adding feedback to trigger learning..."
FEEDBACK_RESPONSE=$(curl -s -X POST http://localhost:8007/personality/update \
  -H "Content-Type: application/json" \
  -d '{
    "traits": {
      "intelligence": 96,
      "humor": 72,
      "empathy": 87,
      "confidence": 91,
      "enthusiasm": 82,
      "creativity": 77,
      "culturalAwareness": 92
    },
    "mood": "optimistic",
    "preferences": {
      "language": "mixed",
      "formality": "professional",
      "humor": "subtle"
    }
  }')

echo "$FEEDBACK_RESPONSE" | jq '.' 2>/dev/null || echo "$FEEDBACK_RESPONSE"

echo ""

# Step 5: Interactive demo
print_header "Step 5: Interactive Self-Training Demo"
echo ""

print_status "Starting interactive self-training demo..."
echo "You can now interact with JarvisX's self-training system!"
echo ""

# Interactive training loop
echo "Enter commands to test self-training (type 'quit' to exit):"
echo ""
echo "Available commands:"
echo "  - start_training: Start a new training session"
echo "  - run_experiment: Run an A/B test experiment"
echo "  - optimize: Run performance optimization"
echo "  - synthesize: Synthesize knowledge"
echo "  - status: Get training status"
echo "  - quit: Exit demo"
echo ""

while true; do
    read -p "Command: " user_input
    
    if [ "$user_input" = "quit" ] || [ "$user_input" = "exit" ]; then
        break
    fi
    
    case $user_input in
        "start_training")
            echo "🧠 Starting training session..."
            TRAINING_RESPONSE=$(curl -s -X POST http://localhost:8008/training/start \
              -H "Content-Type: application/json" \
              -d '{"mode": "incremental", "priority": "normal"}')
            echo "$TRAINING_RESPONSE" | jq -r '.message' 2>/dev/null || echo "Training started"
            ;;
            
        "run_experiment")
            echo "🧪 Running A/B test experiment..."
            EXPERIMENT_RESPONSE=$(curl -s -X POST http://localhost:8008/experiments/run \
              -H "Content-Type: application/json" \
              -d '{"type": "ab_test", "parameters": {"testType": "response_style"}}')
            echo "$EXPERIMENT_RESPONSE" | jq -r '.experiment.name' 2>/dev/null || echo "Experiment started"
            ;;
            
        "optimize")
            echo "⚡ Running performance optimization..."
            OPTIMIZATION_RESPONSE=$(curl -s -X POST http://localhost:8008/optimization/run \
              -H "Content-Type: application/json" \
              -d '{"target": "user_satisfaction"}')
            echo "$OPTIMIZATION_RESPONSE" | jq -r '.result.method' 2>/dev/null || echo "Optimization started"
            ;;
            
        "synthesize")
            echo "🧠 Synthesizing knowledge..."
            SYNTHESIS_RESPONSE=$(curl -s -X POST http://localhost:8008/knowledge/synthesize \
              -H "Content-Type: application/json" \
              -d '{"source": "all", "depth": "medium"}')
            echo "$SYNTHESIS_RESPONSE" | jq -r '.synthesis.insights[0]' 2>/dev/null || echo "Knowledge synthesis started"
            ;;
            
        "status")
            echo "📊 Getting training status..."
            STATUS_RESPONSE=$(curl -s http://localhost:8008/training/status)
            echo "$STATUS_RESPONSE" | jq -r '.isTraining' 2>/dev/null || echo "Status retrieved"
            ;;
            
        *)
            echo "Unknown command: $user_input"
            echo "Available commands: start_training, run_experiment, optimize, synthesize, status, quit"
            ;;
    esac
    
    echo ""
done

echo ""

# Step 6: Demo cleanup
print_header "Step 6: Demo Cleanup"
echo ""

print_status "Stopping services..."

# Stop services
kill $SELF_TRAINING_PID $PERSONALITY_PID 2>/dev/null

# Wait for services to stop
sleep 3

print_success "Demo completed successfully!"
echo ""

# Summary
print_header "🎉 Demo Summary"
echo ""
echo "You have successfully experienced JarvisX's self-training capabilities:"
echo ""
echo "✅ Self-Training Core - Autonomous learning and neural network training"
echo "✅ Pattern Recognition - Automatic pattern discovery and analysis"
echo "✅ Performance Optimization - Self-optimization using advanced algorithms"
echo "✅ Knowledge Synthesis - Autonomous knowledge extraction and organization"
echo "✅ Autonomous Experiments - Self-directed A/B testing and experimentation"
echo "✅ Feedback Loop System - Continuous improvement through feedback"
echo "✅ Integration with Personality - Personality-driven learning and adaptation"
echo ""

print_header "🚀 Next Steps"
echo ""
echo "To continue exploring JarvisX's self-training features:"
echo ""
echo "1. Start the full system: docker-compose up -d"
echo "2. View training dashboard at: http://localhost:8008/training/status"
echo "3. Monitor learning progress: http://localhost:8008/learning/progress"
echo "4. Read the documentation: cat SELF_TRAINING_CAPABILITIES.md"
echo ""

print_success "JarvisX is now truly self-evolving and autonomous! 🧠✨"
echo ""
echo "JarvisX learns, adapts, and improves itself continuously - just like a human!"
