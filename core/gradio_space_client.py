#!/usr/bin/env python3
"""
Gradio Space Client - Connect to Your Deployed HF Space
For: AsithaLKonara/jarvis-llm-brain
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GradioSpaceClient:
    """
    Client for your deployed Gradio Space on Hugging Face
    Space: AsithaLKonara/jarvis-llm-brain
    """
    
    def __init__(self, space_name: str = "AsithaLKonara/jarvis-llm-brain", hf_token: str = None):
        """
        Initialize Gradio Space client
        
        Args:
            space_name: HF Space name
            hf_token: HF token (required for private Spaces)
        """
        self.space_name = space_name
        self.hf_token = hf_token or os.getenv('HF_TOKEN')
        self.client = None
        self.is_available = False
        
        logger.info(f"🌐 Connecting to HF Space: {space_name}")
        if self.hf_token:
            logger.info("🔐 Using HF token for authentication")
        
        self._connect()
    
    def _connect(self):
        """Connect to Gradio Space"""
        try:
            from gradio_client import Client
            
            logger.info("📡 Establishing connection...")
            
            # Connect to your Space (with token if provided)
            self.client = Client(self.space_name, hf_token=self.hf_token)
            
            self.is_available = True
            logger.info("✅ Connected to Gradio Space!")
            logger.info(f"   Space: https://huggingface.co/spaces/{self.space_name}")
            
        except ImportError:
            logger.error("❌ gradio_client not installed")
            logger.error("   Install: pip install gradio_client")
            self.is_available = False
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            logger.error("   Space might be sleeping or not accessible")
            self.is_available = False
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response from your HF Space
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated response
        """
        if not self.is_available:
            raise RuntimeError("Gradio Space not available")
        
        try:
            logger.info("📤 Sending request to HF Space...")
            
            # Call the /generate endpoint
            result = self.client.predict(
                prompt,  # Prompt
                max_new_tokens,  # Max new tokens
                temperature,  # Temperature
                api_name="/generate"
            )
            
            logger.info("✅ Response received")
            
            # Extract response (format depends on Space output)
            if isinstance(result, str):
                return result
            elif isinstance(result, dict):
                return result.get('response', str(result))
            elif isinstance(result, (list, tuple)) and len(result) > 0:
                return str(result[0])
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            raise RuntimeError(f"HF Space generation failed: {e}")
    
    def get_response(self, query: str, max_length: int = 256, temperature: float = 0.7) -> str:
        """
        Compatibility wrapper for existing code
        """
        return self.generate(query, max_new_tokens=max_length, temperature=temperature)
    
    def is_ready(self) -> bool:
        """Check if client is ready"""
        return self.is_available


def test_space_client():
    """Test Gradio Space client"""
    print("\n" + "="*70)
    print("🧪 Testing Gradio Space Client")
    print("="*70 + "\n")
    
    # Connect to your Space
    client = GradioSpaceClient("AsithaLKonara/jarvis-llm-brain")
    
    if not client.is_ready():
        print("❌ Space not available")
        print()
        print("Possible issues:")
        print("  1. Space is sleeping (visit in browser to wake it)")
        print("  2. gradio_client not installed (pip install gradio_client)")
        print("  3. Space name incorrect")
        return False
    
    print("✅ Connected to Space!")
    print()
    
    # Test inference
    print("🧪 Testing inference...")
    test_queries = [
        "What is Python?",
        "Explain machine learning",
        "How to optimize code?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}/{len(test_queries)}: {query}")
        
        try:
            response = client.generate(query, max_new_tokens=100, temperature=0.7)
            print(f"✅ Response ({len(response)} chars):")
            print(f"   {response[:150]}...")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print()
    print("="*70)
    print("✅ Testing complete!")
    print("="*70)
    print()
    
    return True


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    success = test_space_client()
    sys.exit(0 if success else 1)

