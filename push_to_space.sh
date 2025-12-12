#!/bin/bash
# Script to push fixed app.py to Hugging Face Space

echo "🚀 Pushing fix to Hugging Face Space..."
echo ""

# Check if HF_TOKEN is set
if [ -z "$HF_TOKEN" ]; then
    echo "❌ HF_TOKEN not set!"
    echo ""
    echo "Please set your Hugging Face token:"
    echo "  export HF_TOKEN=your_token_here"
    echo ""
    echo "Get your token from: https://huggingface.co/settings/tokens"
    exit 1
fi

# Navigate to Space directory
cd "$(dirname "$0")/jarvis-llm-brain" || exit 1

# Update remote URL with token
echo "📝 Updating remote URL..."
git remote set-url origin "https://AsithaLKonara:${HF_TOKEN}@huggingface.co/spaces/AsithaLKonara/jarvis-llm-brain"

# Push
echo "📤 Pushing to Space..."
if git push origin main; then
    echo ""
    echo "✅ Push successful!"
    echo ""
    echo "⏳ Space will rebuild automatically (10-15 minutes on free tier)"
    echo "📊 Check build logs: https://huggingface.co/spaces/AsithaLKonara/jarvis-llm-brain/logs"
else
    echo ""
    echo "❌ Push failed!"
    echo "💡 Try:"
    echo "   1. Verify token is valid: https://huggingface.co/settings/tokens"
    echo "   2. Or use manual upload via web UI (see PUSH_INSTRUCTIONS.md)"
    exit 1
fi

