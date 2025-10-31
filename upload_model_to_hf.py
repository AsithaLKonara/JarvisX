#!/usr/bin/env python3
"""
Upload trained Jarvis LLM model to Hugging Face Model Hub
"""

import os
from huggingface_hub import HfApi, create_repo, upload_folder
from pathlib import Path

# Configuration
HF_USERNAME = input("Enter your Hugging Face username: ").strip()
MODEL_NAME = "jarvis-llm-brain-final"
LOCAL_MODEL_PATH = "/Users/asithalakmal/Documents/web/JarvisX v2/jarvis-llm-brain-final fine tune 7B model"

print("╔══════════════════════════════════════════════════════════════════════════╗")
print("║                                                                          ║")
print("║        🚀 Upload Jarvis LLM Brain to Hugging Face Model Hub            ║")
print("║                                                                          ║")
print("╚══════════════════════════════════════════════════════════════════════════╝")
print()
print(f"📋 Configuration:")
print(f"   Username: {HF_USERNAME}")
print(f"   Model Name: {MODEL_NAME}")
print(f"   Local Path: {LOCAL_MODEL_PATH}")
print()

# Verify files exist
print("🔍 Verifying model files...")
required_files = [
    "adapter_config.json",
    "adapter_model.safetensors",
    "tokenizer.json",
    "tokenizer.model",
    "README.md"
]

for file in required_files:
    file_path = Path(LOCAL_MODEL_PATH) / file
    if file_path.exists():
        size = file_path.stat().st_size / (1024 * 1024)  # MB
        print(f"   ✅ {file} ({size:.2f} MB)")
    else:
        print(f"   ❌ {file} - MISSING!")
        exit(1)

print()

# Get HF token
print("🔐 Authentication:")
print("   Please get your Hugging Face token:")
print("   1. Visit: https://huggingface.co/settings/tokens")
print("   2. Click 'New token' → 'Write' access")
print("   3. Copy and paste below")
print()

hf_token = input("Enter your HF token: ").strip()

if not hf_token:
    print("❌ No token provided!")
    exit(1)

print()

# Initialize API
print("🔌 Connecting to Hugging Face...")
api = HfApi(token=hf_token)

# Create repository
repo_id = f"{HF_USERNAME}/{MODEL_NAME}"
print(f"📦 Creating repository: {repo_id}")

try:
    create_repo(
        repo_id=repo_id,
        token=hf_token,
        repo_type="model",
        exist_ok=True,
        private=False  # Set to True if you want it private
    )
    print("✅ Repository created (or already exists)")
except Exception as e:
    print(f"⚠️  Repository creation: {e}")
    print("   (This is OK if repo already exists)")

print()

# Upload files
print("📤 Uploading model files...")
print("   This may take 2-5 minutes (uploading 30MB)...")
print()

try:
    upload_folder(
        folder_path=LOCAL_MODEL_PATH,
        repo_id=repo_id,
        token=hf_token,
        repo_type="model",
        commit_message="Upload Jarvis X V2 trained LoRA adapter"
    )
    
    print()
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                          ║")
    print("║                    ✅ UPLOAD SUCCESSFUL! ✅                              ║")
    print("║                                                                          ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"🎉 Your model is now available at:")
    print(f"   https://huggingface.co/{repo_id}")
    print()
    print("📋 Next Steps:")
    print("   1. Visit the model page and verify everything looks good")
    print("   2. Test the model with the code examples in README")
    print("   3. Deploy to Hugging Face Space for cloud inference")
    print()
    print("🚀 To deploy to Space:")
    print(f"   cd '/Users/asithalakmal/Documents/web/JarvisX v2/cloud_deployment'")
    print(f"   ./deploy_to_hf.sh {HF_USERNAME}")
    print()
    
except Exception as e:
    print()
    print("❌ Upload failed!")
    print(f"   Error: {e}")
    print()
    print("🔧 Troubleshooting:")
    print("   1. Check your internet connection")
    print("   2. Verify your HF token has 'write' access")
    print("   3. Make sure the model files exist")
    print("   4. Try again with: python3 upload_model_to_hf.py")
    exit(1)

