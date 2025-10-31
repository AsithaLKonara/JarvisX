#!/bin/bash
# Master deployment script for Jarvis X V2 trained model
# Runs all deployment steps in sequence

set -e

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║         🚀 JARVIS X V2 - COMPLETE MODEL DEPLOYMENT                      ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if HF username is provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your Hugging Face username"
    echo ""
    echo "Usage: ./deploy_all.sh YOUR-HF-USERNAME"
    echo ""
    echo "Example: ./deploy_all.sh asithalakmal"
    echo ""
    echo "This script will:"
    echo "  1. Upload your trained model to HF Model Hub"
    echo "  2. Deploy to HF Space for cloud inference"
    echo "  3. Test the deployment"
    echo "  4. Configure local Jarvis"
    echo ""
    exit 1
fi

HF_USERNAME="$1"
BASE_DIR="/Users/asithalakmal/Documents/web/JarvisX v2"

echo "📋 Configuration:"
echo "   HF Username: $HF_USERNAME"
echo "   Base Directory: $BASE_DIR"
echo ""
echo "This will take approximately 15-20 minutes."
echo ""
read -p "Ready to proceed? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "=" | tr " " "=" | head -c 74
echo ""

# Step 1: Upload model to HF Model Hub
echo ""
echo "📦 STEP 1/5: Uploading model to Hugging Face Model Hub"
echo ""
echo "=" | tr " " "=" | head -c 74
echo ""

cd "$BASE_DIR"

echo "🔄 Running: python3 upload_model_to_hf.py"
echo ""
echo "⚠️  You will need to enter your HF Access Token"
echo "   Get it from: https://huggingface.co/settings/tokens"
echo ""

# Note: This is interactive, user needs to provide token
python3 upload_model_to_hf.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Model upload failed!"
    echo "   Check error message above"
    exit 1
fi

echo ""
echo "✅ Model uploaded successfully!"
echo ""
sleep 2

# Step 2: Create HF Space (manual step)
echo ""
echo "=" | tr " " "=" | head -c 74
echo ""
echo "📦 STEP 2/5: Create Hugging Face Space"
echo ""
echo "=" | tr " " "=" | head -c 74
echo ""

echo "Please create your Space manually:"
echo ""
echo "1. Go to: https://huggingface.co/spaces"
echo "2. Click 'Create new Space'"
echo "3. Fill in:"
echo "   - Name: jarvis-llm-brain"
echo "   - SDK: Gradio"
echo "   - Hardware: CPU basic (FREE)"
echo "   - Visibility: Private"
echo "4. Click 'Create Space'"
echo ""
read -p "Have you created the Space? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "❌ Please create the Space first, then run this script again"
    echo ""
    echo "Or run manually:"
    echo "   cd cloud_deployment"
    echo "   ./deploy_to_hf.sh $HF_USERNAME"
    exit 1
fi

# Step 3: Deploy to Space
echo ""
echo "=" | tr " " "=" | head -c 74
echo ""
echo "📦 STEP 3/5: Deploying to Hugging Face Space"
echo ""
echo "=" | tr " " "=" | head -c 74
echo ""

cd "$BASE_DIR/cloud_deployment"
./deploy_to_hf.sh "$HF_USERNAME"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Space deployment failed!"
    echo "   Check error message above"
    exit 1
fi

echo ""
echo "✅ Deployed to Space successfully!"
echo ""
sleep 2

# Step 4: Wait for build
echo ""
echo "=" | tr " " "=" | head -c 74
echo ""
echo "⏳ STEP 4/5: Waiting for Space build"
echo ""
echo "=" | tr " " "=" | head -c 74
echo ""

SPACE_URL="https://${HF_USERNAME}-jarvis-llm-brain.hf.space"

echo "Your Space is building..."
echo ""
echo "🌐 Space URL: https://huggingface.co/spaces/${HF_USERNAME}/jarvis-llm-brain"
echo "🔗 API URL: $SPACE_URL"
echo ""
echo "This usually takes 5-10 minutes for first build."
echo ""
echo "Options:"
echo "  1. Wait here (we'll check every minute)"
echo "  2. Skip and check manually later"
echo ""
read -p "Wait for build to complete? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "⏳ Checking build status every 60 seconds..."
    echo "   (You can press Ctrl+C to skip)"
    echo ""
    
    MAX_ATTEMPTS=15  # 15 minutes max
    ATTEMPT=0
    
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        ATTEMPT=$((ATTEMPT + 1))
        echo "   Attempt $ATTEMPT/$MAX_ATTEMPTS..."
        
        # Try to connect to Space
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$SPACE_URL" 2>/dev/null || echo "000")
        
        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "404" ]; then
            echo ""
            echo "✅ Space is responding! (HTTP $HTTP_CODE)"
            break
        fi
        
        if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
            sleep 60
        fi
    done
    
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo ""
        echo "⚠️  Build is taking longer than expected"
        echo "   Check Space status manually:"
        echo "   https://huggingface.co/spaces/${HF_USERNAME}/jarvis-llm-brain"
        echo ""
        echo "   You can continue with deployment and test later."
        echo ""
    fi
fi

# Step 5: Test deployment
echo ""
echo "=" | tr " " "=" | head -c 74
echo ""
echo "🧪 STEP 5/5: Testing deployment"
echo ""
echo "=" | tr " " "=" | head -c 74
echo ""

cd "$BASE_DIR"

echo "Setting environment variables..."
export CLOUD_LLM_URL="$SPACE_URL"
export DISABLE_HELAGPT=true

echo ""
echo "Testing cloud API connection..."
echo ""

# Test cloud client
python3 cloud_llm_client.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Cloud API test passed!"
    echo ""
else
    echo ""
    echo "⚠️  Cloud API test failed"
    echo "   Space might still be building"
    echo "   Try again in a few minutes:"
    echo "   python3 cloud_llm_client.py"
    echo ""
fi

# Final summary
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║              ✅ DEPLOYMENT COMPLETE! ✅                                  ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Summary:"
echo "   ✅ Model uploaded to HF Model Hub"
echo "   ✅ Deployed to HF Space"
echo "   ✅ Environment configured"
echo ""
echo "🔗 Your URLs:"
echo "   Model: https://huggingface.co/${HF_USERNAME}/jarvis-llm-brain-final"
echo "   Space: https://huggingface.co/spaces/${HF_USERNAME}/jarvis-llm-brain"
echo "   API: $SPACE_URL"
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Run comprehensive tests (50 test cases):"
echo "   python3 test_trained_model.py"
echo ""
echo "2. Start Jarvis with your trained model:"
echo "   export CLOUD_LLM_URL='$SPACE_URL'"
echo "   export DISABLE_HELAGPT=true"
echo "   python3 main.py"
echo ""
echo "3. Make environment variables permanent:"
echo "   echo 'export CLOUD_LLM_URL=\"$SPACE_URL\"' >> ~/.zshrc"
echo "   echo 'export DISABLE_HELAGPT=true' >> ~/.zshrc"
echo "   source ~/.zshrc"
echo ""
echo "📚 Documentation:"
echo "   • TRAINED_MODEL_DEPLOYMENT_GUIDE.md - Complete guide"
echo "   • QUICK_START_TRAINED_MODEL.txt - Quick reference"
echo "   • INTEGRATION_COMPLETE_SUMMARY.md - What you built"
echo ""
echo "🎉 Your Jarvis AI is now powered by your custom-trained model!"
echo ""

