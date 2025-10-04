#!/bin/bash

# Demo script for STT service
# Tests Sinhala speech-to-text transcription

echo "🎤 JarvisX STT Service Demo"
echo "=========================="

# Check if STT service is running
echo "Checking STT service health..."
curl -s http://localhost:8001/health | jq '.' || {
    echo "❌ STT service is not running. Please start it with: docker-compose up stt"
    exit 1
}

echo "✅ STT service is running"

# Test supported languages
echo -e "\n📋 Supported languages:"
curl -s http://localhost:8001/languages | jq '.supported_languages'

# Create a test audio file (sine wave for demo)
echo -e "\n🎵 Creating test audio file..."
ffmpeg -f lavfi -i "sine=frequency=440:duration=3" -ar 16000 -ac 1 test_audio.wav 2>/dev/null || {
    echo "❌ ffmpeg not found. Please install ffmpeg to run this demo."
    exit 1
}

# Test transcription with Sinhala
echo -e "\n🔊 Testing Sinhala transcription..."
curl -X POST http://localhost:8001/transcribe \
  -F "file=@test_audio.wav" \
  -F "language=si" \
  -s | jq '.'

# Test transcription with English
echo -e "\n🔊 Testing English transcription..."
curl -X POST http://localhost:8001/transcribe \
  -F "file=@test_audio.wav" \
  -F "language=en" \
  -s | jq '.'

# Test batch transcription
echo -e "\n📦 Testing batch transcription..."
curl -X POST http://localhost:8001/transcribe-batch \
  -F "files=@test_audio.wav" \
  -F "files=@test_audio.wav" \
  -F "language=si" \
  -s | jq '.'

# Cleanup
echo -e "\n🧹 Cleaning up..."
rm -f test_audio.wav

echo -e "\n✅ STT demo completed!"
echo "💡 Try uploading a real Sinhala audio file to test transcription accuracy."
