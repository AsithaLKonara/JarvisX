#!/usr/bin/env python3
"""
Test Connection to Your HF Space
Quick test to verify your Space is accessible
"""

import os
import sys

print("\n" + "="*70)
print("🧪 TESTING YOUR HF SPACE CONNECTION")
print("="*70 + "\n")

# Check for HF token
hf_token = os.getenv('HF_TOKEN')

if not hf_token:
    print("⚠️  HF_TOKEN not set!")
    print()
    print("Your Space is PRIVATE and requires authentication.")
    print()
    print("To set your token:")
    print("  1. Get token from: https://huggingface.co/settings/tokens")
    print("  2. Export: export HF_TOKEN='hf_your_token_here'")
    print("  3. Run again: python3 test_hf_space_connection.py")
    print()
    print("Or run with token:")
    print("  HF_TOKEN='your-token' python3 test_hf_space_connection.py")
    print()
    sys.exit(1)

print("✅ HF_TOKEN found")
print(f"   Token: hf_***{hf_token[-8:]}")
print()

# Test connection
print("📡 Connecting to Space: AsithaLKonara/jarvis-llm-brain")
print("   (This may take 30-60 seconds if Space is sleeping)")
print()

try:
    from core.gradio_space_client import GradioSpaceClient
    
    # Connect with token
    client = GradioSpaceClient(
        space_name="AsithaLKonara/jarvis-llm-brain",
        hf_token=hf_token
    )
    
    if not client.is_ready():
        print("❌ Connection failed")
        print()
        print("Possible issues:")
        print("  1. Space is sleeping - visit in browser to wake it")
        print("  2. Token doesn't have access to this Space")
        print("  3. Space name changed")
        print()
        sys.exit(1)
    
    print("✅ Connected successfully!")
    print()
    
    # Test inference
    print("🧪 Testing inference...")
    print()
    
    test_query = "What is Python programming?"
    print(f"Query: {test_query}")
    print("Generating response...")
    print()
    
    response = client.generate(
        prompt=test_query,
        max_new_tokens=150,
        temperature=0.7
    )
    
    print("="*70)
    print("✅ SUCCESS! YOUR HF SPACE IS WORKING!")
    print("="*70)
    print()
    print(f"Response from YOUR fine-tuned model:")
    print(f"{response}")
    print()
    print("="*70)
    print()
    print("🎉 Your HF Space is ready to use with the training system!")
    print()
    print("Next steps:")
    print("  1. export HF_TOKEN='your-token'")
    print("  2. python3 training_gui.py")
    print("  3. python3 cursor_training_integration.py --queries 20")
    print()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print()
    print("Install required package:")
    print("  pip install gradio_client")
    print()
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Troubleshooting:")
    print("  1. Wake Space: https://huggingface.co/spaces/AsithaLKonara/jarvis-llm-brain")
    print("  2. Check token has access to private Space")
    print("  3. Wait 30-60 seconds for Space to wake up")
    print()
    sys.exit(1)

