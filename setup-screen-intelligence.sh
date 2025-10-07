#!/bin/bash

# JarvisX Screen Intelligence Setup Script
# Week 1: Screen Intelligence Implementation

echo "🚀 Setting up JarvisX Screen Intelligence..."
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the JarvisX root directory"
    exit 1
fi

# Install Tesseract OCR (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Installing Tesseract OCR for macOS..."
    if ! command -v tesseract &> /dev/null; then
        brew install tesseract tesseract-lang
        echo "✅ Tesseract OCR installed"
    else
        echo "✅ Tesseract OCR already installed"
    fi
fi

# Install Tesseract OCR (Ubuntu/Debian)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Installing Tesseract OCR for Linux..."
    if ! command -v tesseract &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-sin tesseract-ocr-eng
        echo "✅ Tesseract OCR installed"
    else
        echo "✅ Tesseract OCR already installed"
    fi
fi

# Install Node.js dependencies for new services
echo "📦 Installing dependencies for new services..."

# OCR Service
echo "  - Installing OCR service dependencies..."
cd services/ocr
npm install
cd ../..

# Vision Service
echo "  - Installing Vision service dependencies..."
cd services/vision
npm install
cd ../..

# Screen Analyzer Service
echo "  - Installing Screen Analyzer service dependencies..."
cd services/screen-analyzer
npm install
cd ../..

# PC Agent Service
echo "  - Installing PC Agent service dependencies..."
cd services/pc-agent
npm install
cd ../..

echo "✅ All dependencies installed"

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose build ocr vision screen-analyzer pc-agent

# Start the services
echo "🚀 Starting Screen Intelligence services..."
docker-compose up -d ocr vision screen-analyzer pc-agent

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Test the services
echo "🧪 Testing services..."

# Test OCR service
echo "  - Testing OCR service..."
if curl -s http://localhost:8011/health | grep -q "healthy"; then
    echo "    ✅ OCR service is running"
else
    echo "    ❌ OCR service is not responding"
fi

# Test Vision service
echo "  - Testing Vision service..."
if curl -s http://localhost:8005/health | grep -q "healthy"; then
    echo "    ✅ Vision service is running"
else
    echo "    ❌ Vision service is not responding"
fi

# Test Screen Analyzer service
echo "  - Testing Screen Analyzer service..."
if curl -s http://localhost:8010/health | grep -q "healthy"; then
    echo "    ✅ Screen Analyzer service is running"
else
    echo "    ❌ Screen Analyzer service is not responding"
fi

# Test PC Agent service
echo "  - Testing PC Agent service..."
if curl -s http://localhost:8004/health | grep -q "healthy"; then
    echo "    ✅ PC Agent service is running"
else
    echo "    ❌ PC Agent service is not responding"
fi

echo ""
echo "🎉 Screen Intelligence Setup Complete!"
echo "======================================"
echo ""
echo "Services running on:"
echo "  - OCR Service: http://localhost:8011"
echo "  - Vision Service: http://localhost:8005"
echo "  - Screen Analyzer: http://localhost:8010"
echo "  - PC Agent: http://localhost:8004"
echo ""
echo "Test the functionality:"
echo "  - Run: node test-screen-intelligence.js"
echo ""
echo "Example usage:"
echo "  - 'Click the blue button' → Finds and clicks blue buttons"
echo "  - 'What's on my screen?' → Describes screen content"
echo "  - 'Find the submit button' → Locates specific elements"
echo ""
echo "Next steps:"
echo "  - Start Week 2: Enhanced System Control"
echo "  - Add real mouse/keyboard control libraries"
echo "  - Implement browser automation with Playwright"
echo ""
