#!/usr/bin/env python3
"""
Cloud LLM Client - Connect to Hugging Face Space or other cloud LLM APIs
"""

import os
import requests
import logging
from typing import Dict, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class CloudLLMClient:
    """
    Client for cloud-deployed Jarvis LLM brain (Hugging Face Space or custom API)
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize cloud LLM client
        
        Args:
            base_url: Base URL of the cloud LLM API
                     If None, reads from CLOUD_LLM_URL environment variable
        """
        self.base_url = base_url or os.getenv("CLOUD_LLM_URL", "").strip()
        self.available = False
        self.api_endpoint = None
        
        if not self.base_url:
            logger.info("ℹ️  No CLOUD_LLM_URL set, cloud LLM disabled")
            return
        
        # Ensure URL has scheme
        if not self.base_url.startswith(('http://', 'https://')):
            self.base_url = f"https://{self.base_url}"
        
        # Set API endpoint
        self.api_endpoint = urljoin(self.base_url, '/generate')
        
        logger.info(f"🌐 Connecting to Cloud LLM: {self.base_url}")
        
        # Test connection
        self._check_connection()
    
    def _check_connection(self):
        """Test if the cloud LLM API is reachable"""
        try:
            # Try health check endpoint first
            health_url = urljoin(self.base_url, '/health')
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    self.available = True
                    logger.info("✅ Cloud LLM connected (health check passed)")
                    return
            except:
                pass  # Health endpoint might not exist
            
            # Try basic connection test
            response = requests.get(self.base_url, timeout=5)
            if response.status_code in [200, 404]:  # 404 is OK, means server is up
                self.available = True
                logger.info("✅ Cloud LLM connected")
            else:
                logger.warning(f"⚠️  Cloud LLM returned status {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.warning("⚠️  Cloud LLM connection timed out")
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️  Cloud LLM connection failed (not reachable)")
        except Exception as e:
            logger.warning(f"⚠️  Cloud LLM check failed: {e}")
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Generate response from cloud LLM
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            top_p: Nucleus sampling parameter
            
        Returns:
            Generated response text
            
        Raises:
            RuntimeError: If cloud LLM is not available or request fails
        """
        if not self.available:
            raise RuntimeError("Cloud LLM not available")
        
        try:
            # Build request
            payload = {
                "prompt": prompt,
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
            
            # Send request
            logger.info(f"📤 Sending request to cloud LLM...")
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=30  # Cloud should be fast
            )
            
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            if 'response' in data:
                result = data['response']
                logger.info("✅ Cloud LLM response received")
                return result
            else:
                raise RuntimeError(f"Unexpected response format: {data}")
                
        except requests.exceptions.Timeout:
            raise RuntimeError("Cloud LLM request timed out")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Cloud LLM HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Cloud LLM request failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Cloud LLM generation failed: {e}")
    
    def get_response(self, prompt: str, max_length: int = 256, temperature: float = 0.7) -> str:
        """
        Wrapper method for compatibility with other LLM interfaces
        
        Args:
            prompt: Input prompt
            max_length: Maximum tokens (alias for max_new_tokens)
            temperature: Sampling temperature
            
        Returns:
            Generated response text
        """
        return self.generate(prompt, max_new_tokens=max_length, temperature=temperature)
    
    def is_available(self) -> bool:
        """Check if cloud LLM is available"""
        return self.available
    
    def get_stats(self) -> Dict[str, any]:
        """Get client statistics"""
        return {
            'available': self.available,
            'base_url': self.base_url,
            'api_endpoint': self.api_endpoint
        }


def test_cloud_llm():
    """Test cloud LLM client"""
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                          ║")
    print("║                 🧪 Testing Cloud LLM Client                             ║")
    print("║                                                                          ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Get URL from environment or prompt user
    cloud_url = os.getenv("CLOUD_LLM_URL", "").strip()
    
    if not cloud_url:
        print("ℹ️  CLOUD_LLM_URL not set in environment")
        print()
        print("Enter your Hugging Face Space URL:")
        print("   Example: https://YOUR-USERNAME-jarvis-llm-brain.hf.space")
        print()
        cloud_url = input("URL: ").strip()
    
    if not cloud_url:
        print("❌ No URL provided")
        return False
    
    print()
    print(f"🔗 Testing connection to: {cloud_url}")
    print()
    
    # Initialize client
    client = CloudLLMClient(cloud_url)
    
    if not client.available:
        print("❌ Cloud LLM not available")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Check if your Hugging Face Space is 'Running' (not 'Building')")
        print("   2. Verify the URL is correct")
        print("   3. Make sure your Space visibility allows API access")
        return False
    
    print("✅ Connection successful!")
    print()
    
    # Test generation
    print("🧪 Testing generation...")
    test_prompt = "What is Python?"
    
    try:
        response = client.generate(test_prompt, max_new_tokens=100, temperature=0.7)
        
        print()
        print("╔══════════════════════════════════════════════════════════════════════════╗")
        print("║                         ✅ TEST PASSED!                                  ║")
        print("╚══════════════════════════════════════════════════════════════════════════╝")
        print()
        print("📋 Test Query:")
        print(f"   {test_prompt}")
        print()
        print("📝 Response:")
        print(f"   {response[:200]}...")
        print()
        print("✅ Cloud LLM is working perfectly!")
        print()
        print("🔧 To use in Jarvis:")
        print(f"   export CLOUD_LLM_URL='{cloud_url}'")
        print("   export DISABLE_HELAGPT=true")
        print("   python3 main.py")
        print()
        return True
        
    except Exception as e:
        print()
        print("❌ Generation test failed!")
        print(f"   Error: {e}")
        print()
        print("🔧 Possible issues:")
        print("   1. Space is still building (wait 5-10 minutes)")
        print("   2. API endpoint not responding")
        print("   3. Space crashed (check Space logs)")
        return False


if __name__ == "__main__":
    import sys
    
    # Enable logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    success = test_cloud_llm()
    sys.exit(0 if success else 1)
