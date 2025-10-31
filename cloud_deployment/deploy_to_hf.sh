#!/bin/bash
# Quick deploy script for Hugging Face Space

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║        🚀 Deploy Jarvis LLM to Hugging Face Space               ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check if HF username is provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your Hugging Face username"
    echo ""
    echo "Usage: ./deploy_to_hf.sh YOUR-HF-USERNAME"
    echo ""
    echo "Example: ./deploy_to_hf.sh asithalakmal"
    exit 1
fi

HF_USERNAME="$1"
SPACE_NAME="jarvis-llm-brain"
DEPLOY_DIR="$HOME/Desktop/${SPACE_NAME}"

echo "📋 Configuration:"
echo "   HF Username: $HF_USERNAME"
echo "   Space Name: $SPACE_NAME"
echo "   Deploy Directory: $DEPLOY_DIR"
echo ""

# Step 1: Clone Space (if not exists)
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "📥 Step 1: Cloning Space from Hugging Face..."
    cd ~/Desktop
    git clone "https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"
    cd "$SPACE_NAME"
else
    echo "✅ Step 1: Space directory exists, updating..."
    cd "$DEPLOY_DIR"
    git pull
fi

echo ""
echo "📦 Step 2: Copying files to Space..."

# Copy Space files
cp "/Users/asithalakmal/Documents/web/JarvisX v2/cloud_deployment/hf_space/app.py" .
cp "/Users/asithalakmal/Documents/web/JarvisX v2/cloud_deployment/hf_space/requirements.txt" .
cp "/Users/asithalakmal/Documents/web/JarvisX v2/cloud_deployment/hf_space/README.md" .

echo "✅ Copied app files"

# Copy LoRA adapter (trained model)
echo "📦 Copying LoRA adapter (this may take a moment)..."
mkdir -p jarvis-llm-adapter

# Check if trained model exists
TRAINED_MODEL="/Users/asithalakmal/Documents/web/JarvisX v2/jarvis-llm-brain-final fine tune 7B model"
if [ -d "$TRAINED_MODEL" ]; then
    echo "   Found trained model!"
    cp -r "$TRAINED_MODEL/"* jarvis-llm-adapter/
    echo "✅ Copied trained LoRA adapter (137K examples)"
else
    echo "⚠️  Trained model not found, checking old location..."
    cp -r "/Users/asithalakmal/Documents/web/JarvisX v2/models/jarvis-llm-brain-final/"* jarvis-llm-adapter/
    echo "✅ Copied LoRA adapter"
fi
echo ""

echo "📊 Files to be deployed:"
ls -lh | grep -v "^d" | awk '{print "   " $9 " (" $5 ")"}'
echo ""

# Step 3: Commit and push
echo "🚀 Step 3: Committing and pushing to Hugging Face..."
git add .
git commit -m "Deploy Jarvis LLM Brain with LoRA adapter" || echo "No changes to commit"
echo ""
echo "Pushing to Hugging Face..."
echo "(You'll need your HF Access Token - get it from https://huggingface.co/settings/tokens)"
echo ""
git push

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║        ✅ DEPLOYMENT COMPLETE!                                   ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Your Space: https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"
echo ""
echo "⏳ Wait 5-10 minutes for the build to complete."
echo ""
echo "📡 Once 'Running', your API URL is:"
echo "   https://${HF_USERNAME}-${SPACE_NAME}.hf.space"
echo ""
echo "🔧 Configure Jarvis with:"
echo "   export CLOUD_LLM_URL=\"https://${HF_USERNAME}-${SPACE_NAME}.hf.space\""
echo "   export DISABLE_HELAGPT=true"
echo "   python3 main.py"
echo ""

