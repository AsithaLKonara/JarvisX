#!/usr/bin/env python3
"""
Connect Training System to Hugging Face Model
"""

import os
from pathlib import Path

def setup_huggingface_model(hf_model_id: str = None, use_token: bool = False):
    """
    Configure system to use Hugging Face model
    
    Args:
        hf_model_id: Your HF model ID (e.g., "username/jarvis-mistral-7b")
        use_token: Whether to use HF token for private models
    """
    
    print("\n" + "="*70)
    print("🤗 CONNECTING TO HUGGING FACE MODEL")
    print("="*70 + "\n")
    
    # Option 1: Local model (already downloaded)
    local_model = Path("/Users/asithalakmal/Documents/web/JarvisX v2/jarvis-llm-brain-final fine tune 7B model")
    
    if local_model.exists():
        print("✅ Local model found!")
        print(f"   Path: {local_model}")
        print(f"   Files: {list(local_model.glob('*'))[:5]}")
        print()
        print("Your system is ALREADY configured to use this model!")
        print()
        print("To use it:")
        print("  1. Install dependencies: pip install transformers torch bitsandbytes")
        print("  2. Run Training GUI: python3 training_gui.py")
        print("  3. Run automation: python3 cursor_training_integration.py --queries 20")
        print()
        return True
    
    # Option 2: Download from Hugging Face Hub
    if hf_model_id:
        print(f"📥 Downloading from Hugging Face: {hf_model_id}")
        print()
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Set up token if needed
            token = None
            if use_token:
                token = os.getenv("HF_TOKEN") or input("Enter HF token: ")
            
            print("⏳ Downloading model (this may take a while)...")
            
            # Download model
            model = AutoModelForCausalLM.from_pretrained(
                hf_model_id,
                token=token,
                cache_dir="models/hf_cache"
            )
            
            tokenizer = AutoTokenizer.from_pretrained(
                hf_model_id,
                token=token,
                cache_dir="models/hf_cache"
            )
            
            print("✅ Model downloaded successfully!")
            print(f"   Cached at: models/hf_cache")
            print()
            
            # Update config
            print("📝 Updating configuration...")
            config_update = f"""
# Add to your .env file:
HF_MODEL_ID={hf_model_id}
USE_HF_MODEL=true
"""
            print(config_update)
            
            with open(".env.hf", "w") as f:
                f.write(config_update)
            
            print("✅ Configuration saved to .env.hf")
            print()
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
            print("Make sure you have:")
            print("  1. Correct model ID")
            print("  2. Valid HF token (if private)")
            print("  3. Sufficient disk space")
            return False
    
    # No model configured
    print("⚠️  No model configured!")
    print()
    print("Options:")
    print("  1. Your local model should be at:")
    print(f"     {local_model}")
    print()
    print("  2. Or specify HF model ID:")
    print("     python3 connect_huggingface_model.py --model username/model-name")
    print()
    
    return False


def check_model_status():
    """Check current model configuration"""
    
    print("\n" + "="*70)
    print("📊 MODEL CONFIGURATION STATUS")
    print("="*70 + "\n")
    
    # Check local model
    local_model = Path("/Users/asithalakmal/Documents/web/JarvisX v2/jarvis-llm-brain-final fine tune 7B model")
    
    print("1. LOCAL MODEL:")
    if local_model.exists():
        files = list(local_model.glob("*"))
        print(f"   ✅ Found at: {local_model}")
        print(f"   📁 Files: {len(files)}")
        print()
        print("   Key files:")
        for f in ['config.json', 'model.safetensors', 'tokenizer.json', 'pytorch_model.bin']:
            if (local_model / f).exists():
                print(f"      ✅ {f}")
            else:
                print(f"      ❌ {f}")
        print()
    else:
        print("   ❌ Not found")
        print()
    
    # Check HF cache
    print("2. HUGGING FACE CACHE:")
    hf_cache = Path("models/hf_cache")
    if hf_cache.exists():
        print(f"   ✅ Found at: {hf_cache}")
        print(f"   📁 Cached models: {len(list(hf_cache.glob('*')))}")
    else:
        print("   ❌ No cached models")
    print()
    
    # Check environment
    print("3. CONFIGURATION:")
    if Path(".env").exists():
        print("   ✅ .env file found")
        with open(".env", "r") as f:
            for line in f:
                if "MODEL" in line or "HF" in line:
                    print(f"      {line.strip()}")
    else:
        print("   ❌ No .env file")
    print()
    
    # Recommendation
    print("="*70)
    print("📝 RECOMMENDATION:")
    print("="*70)
    
    if local_model.exists():
        print()
        print("✅ Your model is ready to use!")
        print()
        print("Next steps:")
        print("  1. pip install transformers torch bitsandbytes")
        print("  2. python3 training_gui.py")
        print("  3. python3 cursor_training_integration.py --queries 20")
        print()
    else:
        print()
        print("⚠️  Model not found!")
        print()
        print("Options:")
        print("  A. If you have the model elsewhere, move it to:")
        print(f"     {local_model}")
        print()
        print("  B. Or download from Hugging Face:")
        print("     python3 connect_huggingface_model.py --model YOUR_HF_MODEL_ID")
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Connect to Hugging Face Model')
    parser.add_argument('--model', type=str, help='HF model ID (username/model-name)')
    parser.add_argument('--token', action='store_true', help='Use HF token')
    parser.add_argument('--status', action='store_true', help='Check current status')
    
    args = parser.parse_args()
    
    if args.status:
        check_model_status()
    elif args.model:
        setup_huggingface_model(args.model, args.token)
    else:
        check_model_status()

