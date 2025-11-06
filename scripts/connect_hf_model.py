#!/usr/bin/env python3
"""
Universal HF Model Connector
One command to connect ANY Hugging Face model to the training system
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def upload_to_hf(local_path: str, repo_id: str, token: str = None):
    """Upload local model to HF Hub"""
    
    print("\n" + "="*70)
    print("📤 UPLOADING TO HUGGING FACE HUB")
    print("="*70 + "\n")
    
    try:
        from huggingface_hub import HfApi
        
        api = HfApi(token=token)
        
        print(f"Local path: {local_path}")
        print(f"Repo ID: {repo_id}")
        print()
        
        # Check if path exists
        if not os.path.exists(local_path):
            print(f"❌ Path not found: {local_path}")
            return False
        
        # Upload
        print("⏳ Uploading... (this will take 1-5 minutes for 26MB)")
        
        api.upload_folder(
            folder_path=local_path,
            repo_id=repo_id,
            repo_type="model",
            commit_message="Upload Jarvis fine-tuned model"
        )
        
        print()
        print("✅ Upload complete!")
        print(f"   View at: https://huggingface.co/{repo_id}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print()
        print("Make sure:")
        print("  1. You're logged in: huggingface-cli login")
        print("  2. Repo exists or will be created automatically")
        print("  3. You have write access")
        return False


def test_hf_connection(model_id: str, use_lora: bool = True, quantization: str = "4bit"):
    """Test connection to HF model"""
    
    print("\n" + "="*70)
    print("🧪 TESTING HF MODEL CONNECTION")
    print("="*70 + "\n")
    
    print(f"Model ID: {model_id}")
    print(f"Type: {'LoRA Adapter' if use_lora else 'Full Model'}")
    print(f"Quantization: {quantization}")
    print()
    
    try:
        from transformers import AutoTokenizer, BitsAndBytesConfig, AutoModelForCausalLM, pipeline
        import torch
        
        # Configure quantization
        bnb_config = None
        if quantization == "4bit":
            print("⚡ Configuring 4-bit quantization...")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        
        # Load model
        if use_lora:
            print("📥 Loading LoRA adapter from HF Hub...")
            print("   (First run: downloads base model ~14GB, 10-30 min)")
            print("   (Subsequent: uses cache, fast!)")
            print()
            
            try:
                from peft import AutoPeftModelForCausalLM
                
                model = AutoPeftModelForCausalLM.from_pretrained(
                    model_id,
                    quantization_config=bnb_config,
                    device_map="auto"
                )
                print("✅ LoRA adapter loaded!")
            except Exception as e:
                print(f"⚠️  LoRA load failed, trying as full model: {e}")
                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    quantization_config=bnb_config,
                    device_map="auto"
                )
                print("✅ Full model loaded!")
        else:
            print("📥 Loading full model from HF Hub...")
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                device_map="auto"
            )
            print("✅ Model loaded!")
        
        # Load tokenizer
        print("📦 Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Create pipeline
        print("🔧 Creating pipeline...")
        gen_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device_map="auto",
            return_full_text=False
        )
        
        print("✅ Pipeline ready!")
        print()
        
        # Test inference
        print("🧪 Testing inference...")
        test_query = "What is Python?"
        
        formatted_prompt = f"<s>[INST] You are Jarvis. Answer this question: {test_query} [/INST]"
        
        print(f"Query: {test_query}")
        print("Generating response...")
        
        output = gen_pipeline(
            formatted_prompt,
            max_new_tokens=100,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
        
        response = output[0]['generated_text'].strip()
        
        print()
        print("="*70)
        print("✅ CONNECTION SUCCESSFUL!")
        print("="*70)
        print()
        print(f"Response: {response}")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("="*70)
        print("❌ CONNECTION FAILED")
        print("="*70)
        print()
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check model ID is correct")
        print("  2. Install: pip install transformers peft bitsandbytes torch")
        print("  3. Check internet connection")
        print("  4. Verify model exists on HF Hub")
        print()
        return False


def configure_training_system(model_id: str, use_lora: bool = True):
    """Configure training system to use HF model"""
    
    print("\n" + "="*70)
    print("🔧 CONFIGURING TRAINING SYSTEM")
    print("="*70 + "\n")
    
    # Update .env
    env_content = f"""# Hugging Face Model Configuration
HF_MODEL_ID={model_id}
USE_LORA_ADAPTER={'true' if use_lora else 'false'}
QUANTIZATION=4bit

# Optional: For private models
# HF_TOKEN=your_token_here
"""
    
    with open(".env.hf_model", "w") as f:
        f.write(env_content)
    
    print("✅ Configuration saved to .env.hf_model")
    print()
    print("Configuration:")
    print(env_content)
    
    print("To use this configuration:")
    print("  source .env.hf_model")
    print("  python3 training_gui.py")
    print()
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Connect Hugging Face Model to Training System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test connection to HF model
  python3 scripts/connect_hf_model.py --model your-username/jarvis-lora --test

  # Upload local model to HF Hub
  python3 scripts/connect_hf_model.py --upload --repo your-username/jarvis-lora

  # Full setup: upload + test + configure
  python3 scripts/connect_hf_model.py --model your-username/jarvis-lora --upload --test --configure
        """
    )
    
    parser.add_argument('--model', type=str, help='HF model ID (username/model-name)')
    parser.add_argument('--type', choices=['lora', 'full', 'auto'], default='auto',
                       help='Model type (auto-detects by default)')
    parser.add_argument('--quantization', choices=['4bit', '8bit', 'none'], default='4bit',
                       help='Quantization type')
    parser.add_argument('--upload', action='store_true',
                       help='Upload local model to HF Hub')
    parser.add_argument('--repo', type=str,
                       help='HF repo ID for upload (username/repo-name)')
    parser.add_argument('--test', action='store_true',
                       help='Test connection to HF model')
    parser.add_argument('--configure', action='store_true',
                       help='Configure training system')
    parser.add_argument('--local-path', type=str,
                       default="jarvis-llm-brain-final fine tune 7B model",
                       help='Local model path for upload')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🤗 HUGGING FACE MODEL CONNECTOR")
    print("="*70)
    
    # Upload if requested
    if args.upload:
        if not args.repo:
            print("\n❌ Error: --repo required for upload")
            print("Example: --repo your-username/jarvis-lora")
            return 1
        
        success = upload_to_hf(args.local_path, args.repo)
        if not success:
            return 1
        
        # Use uploaded model ID
        if not args.model:
            args.model = args.repo
    
    # Test connection if requested
    if args.test:
        if not args.model:
            print("\n❌ Error: --model required for testing")
            print("Example: --model your-username/jarvis-lora")
            return 1
        
        use_lora = (args.type == 'lora') or (args.type == 'auto')
        success = test_hf_connection(args.model, use_lora, args.quantization)
        if not success:
            return 1
    
    # Configure if requested
    if args.configure:
        if not args.model:
            print("\n❌ Error: --model required for configuration")
            return 1
        
        use_lora = (args.type == 'lora') or (args.type == 'auto')
        configure_training_system(args.model, use_lora)
    
    # If no action specified, show help
    if not (args.upload or args.test or args.configure):
        parser.print_help()
        return 0
    
    print("\n" + "="*70)
    print("✅ ALL DONE!")
    print("="*70)
    print()
    print("Your HF model is connected!")
    print()
    print("Next steps:")
    print("  1. python3 training_gui.py")
    print("  2. python3 cursor_training_integration.py --queries 20")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

