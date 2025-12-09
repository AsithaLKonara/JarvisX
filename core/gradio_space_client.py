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
    
    def __init__(self, space_url: str = "AsithaLKonara/jarvis-llm-brain", hf_token: str = None):
        """
        Initialize Gradio Space client
        
        Args:
            space_url: HF Space URL or name
            hf_token: HF token (required for private Spaces)
        """
        self.space_url = space_url
        self.hf_token = hf_token or os.getenv('HF_TOKEN')
        self.client = None
        self.is_available = False
        
        logger.info(f"🌐 Connecting to HF Space: {space_url}")
        if self.hf_token:
            logger.info("🔐 Using HF token for authentication")
        
        self._connect()
    
    def _connect(self):
        """Connect to Gradio Space"""
        try:
            from gradio_client import Client
            
            logger.info("📡 Establishing connection...")
            
            # Connect to your Space (with token if provided)
            self.client = Client(self.space_url, hf_token=self.hf_token)
            
            self.is_available = True
            logger.info("✅ Connected to Gradio Space!")
            logger.info(f"   Space: https://huggingface.co/spaces/{self.space_url}")
            
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
            max_new_tokens: Maximum new tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated response (string)
        """
        if not self.is_available:
            raise RuntimeError("Gradio Space not available")
        
        try:
            logger.info("📤 Sending request to HF Space...")
            
            # Call the /generate_response endpoint with correct parameter names
            result = self.client.predict(
                prompt,  # prompt (str)
                max_new_tokens,  # max_new_tokens (float)
                temperature,  # temperature (float)
                api_name="/generate_response"
            )
            
            logger.info("✅ Response received")
            
            # API returns a simple string
            return str(result) if result else ""
                
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            raise RuntimeError(f"HF Space generation failed: {e}")
    
    def get_response(self, query: str, max_length: int = 256, temperature: float = 0.7) -> str:
        """
        Compatibility wrapper for existing code (maps max_length to max_new_tokens)
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
    
    # Get token from environment
    hf_token = os.getenv('HF_TOKEN')
    
    # Connect to your Space
    client = GradioSpaceClient("AsithaLKonara/jarvis-llm-brain", hf_token=hf_token)
    
    if not client.is_ready():
        print("❌ Space not available")
        print()
        print("Possible issues:")
        print("  1. Space is sleeping (visit in browser to wake it)")
        print("  2. gradio_client not installed (pip install gradio_client)")
        print("  3. Space name incorrect")
        print("  4. HF_TOKEN not set or invalid (for private Spaces)")
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
    
    def __init__(self, space_url: str = "AsithaLKonara/jarvis-llm-brain", hf_token: str = None):
        """
        Initialize Gradio Space client
        
        Args:
            space_url: HF Space URL or name
            hf_token: HF token (required for private Spaces)
        """
        self.space_url = space_url
        self.hf_token = hf_token or os.getenv('HF_TOKEN')
        self.client = None
        self.is_available = False
        
        logger.info(f"🌐 Connecting to HF Space: {space_url}")
        if self.hf_token:
            logger.info("🔐 Using HF token for authentication")
        
        self._connect()
    
    def _connect(self):
        """Connect to Gradio Space"""
        try:
            from gradio_client import Client
            
            logger.info("📡 Establishing connection...")
            
            # Connect to your Space (with token if provided)
            self.client = Client(self.space_url, hf_token=self.hf_token)
            
            self.is_available = True
            logger.info("✅ Connected to Gradio Space!")
            logger.info(f"   Space: https://huggingface.co/spaces/{self.space_url}")
            
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
            max_new_tokens: Maximum new tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated response (string)
        """
        if not self.is_available:
            raise RuntimeError("Gradio Space not available")
        
        try:
            logger.info("📤 Sending request to HF Space...")
            
            # Call the /generate_response endpoint with correct parameter names
            result = self.client.predict(
                prompt,  # prompt (str)
                max_new_tokens,  # max_new_tokens (float)
                temperature,  # temperature (float)
                api_name="/generate_response"
            )
            
            logger.info("✅ Response received")
            
            # API returns a simple string
            return str(result) if result else ""
                
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            raise RuntimeError(f"HF Space generation failed: {e}")
    
    def get_response(self, query: str, max_length: int = 256, temperature: float = 0.7) -> str:
        """
        Compatibility wrapper for existing code (maps max_length to max_new_tokens)
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
    
    # Get token from environment
    hf_token = os.getenv('HF_TOKEN')
    
    # Connect to your Space
    client = GradioSpaceClient("AsithaLKonara/jarvis-llm-brain", hf_token=hf_token)
    
    if not client.is_ready():
        print("❌ Space not available")
        print()
        print("Possible issues:")
        print("  1. Space is sleeping (visit in browser to wake it)")
        print("  2. gradio_client not installed (pip install gradio_client)")
        print("  3. Space name incorrect")
        print("  4. HF_TOKEN not set or invalid (for private Spaces)")
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
    
    def __init__(self, space_url: str = "AsithaLKonara/jarvis-llm-brain", hf_token: str = None):
        """
        Initialize Gradio Space client
        
        Args:
            space_url: HF Space URL or name
            hf_token: HF token (required for private Spaces)
        """
        self.space_url = space_url
        self.hf_token = hf_token or os.getenv('HF_TOKEN')
        self.client = None
        self.is_available = False
        
        logger.info(f"🌐 Connecting to HF Space: {space_url}")
        if self.hf_token:
            logger.info("🔐 Using HF token for authentication")
        
        self._connect()
    
    def _connect(self):
        """Connect to Gradio Space"""
        try:
            from gradio_client import Client
            
            logger.info("📡 Establishing connection...")
            
            # Connect to your Space (with token if provided)
            self.client = Client(self.space_url, hf_token=self.hf_token)
            
            self.is_available = True
            logger.info("✅ Connected to Gradio Space!")
            logger.info(f"   Space: https://huggingface.co/spaces/{self.space_url}")
            
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
            max_new_tokens: Maximum new tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated response (string)
        """
        if not self.is_available:
            raise RuntimeError("Gradio Space not available")
        
        try:
            logger.info("📤 Sending request to HF Space...")
            
            # Call the /generate_response endpoint with correct parameter names
            result = self.client.predict(
                prompt,  # prompt (str)
                max_new_tokens,  # max_new_tokens (float)
                temperature,  # temperature (float)
                api_name="/generate_response"
            )
            
            logger.info("✅ Response received")
            
            # API returns a simple string
            return str(result) if result else ""
                
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            raise RuntimeError(f"HF Space generation failed: {e}")
    
    def get_response(self, query: str, max_length: int = 256, temperature: float = 0.7) -> str:
        """
        Compatibility wrapper for existing code (maps max_length to max_new_tokens)
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
    
    # Get token from environment
    hf_token = os.getenv('HF_TOKEN')
    
    # Connect to your Space
    client = GradioSpaceClient("AsithaLKonara/jarvis-llm-brain", hf_token=hf_token)
    
    if not client.is_ready():
        print("❌ Space not available")
        print()
        print("Possible issues:")
        print("  1. Space is sleeping (visit in browser to wake it)")
        print("  2. gradio_client not installed (pip install gradio_client)")
        print("  3. Space name incorrect")
        print("  4. HF_TOKEN not set or invalid (for private Spaces)")
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




