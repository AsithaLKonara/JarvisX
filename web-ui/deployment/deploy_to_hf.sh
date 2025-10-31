#!/bin/bash
# Deploy Jarvis Web UI to Hugging Face Spaces

SPACE_NAME="jarvis-web-ui"
HF_USERNAME="AsithaLKonara"
SPACE_URL="https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"

echo "🚀 Deploying Jarvis Web UI to Hugging Face Spaces"
echo ""

# Check if space exists
echo "📝 Space: $SPACE_URL"
echo ""

# Clone or update space
if [ -d "hf-space" ]; then
    echo "📂 Space directory exists, pulling latest..."
    cd hf-space
    git pull
    cd ..
else
    echo "📥 Cloning space repository..."
    git clone "https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME" hf-space
fi

# Copy files
echo ""
echo "📦 Copying files to space..."

cp Dockerfile hf-space/
cp README.md hf-space/
cp -r ../backend hf-space/
cp -r ../frontend/dist hf-space/frontend 2>/dev/null || echo "⚠️  Frontend not built yet, run: cd frontend && npm run build"

# Copy required Jarvis modules
mkdir -p hf-space/jarvis-core
cp ../../jarvis_llm_brain.py hf-space/jarvis-core/
cp -r ../../core hf-space/jarvis-core/
cp -r ../../utils hf-space/jarvis-core/
cp -r ../../speech hf-space/jarvis-core/
cp -r ../../system_monitor hf-space/jarvis-core/

echo "✅ Files copied"
echo ""

# Commit and push
echo "🔄 Pushing to Hugging Face..."
cd hf-space

git add .
git commit -m "Update Jarvis Web UI - $(date +%Y-%m-%d)"
git push

echo ""
echo "✅ Deployment complete!"
echo "🌐 Visit: $SPACE_URL"

