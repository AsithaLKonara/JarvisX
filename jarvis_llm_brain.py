#!/usr/bin/env python3
"""
Jarvis X V2 LLM Brain - Trained Model Integration
Supports GGUF (fastest local), Ollama, Cloud LLM API, and Python wrapper
"""

import os
import logging
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class JarvisLLMBrain:
    """
    Custom trained LLM brain for Jarvis X V2
    Priority: Cloud LLM (fast) > Ollama (local) > GGUF (local) > Python wrapper
    """
    
    def __init__(self, model_path: str = None):
        """Initialize trained LLM brain"""
        # Try trained model first, fallback to old location
        if model_path is None:
            trained_model = "/Users/asithalakmal/Documents/web/JarvisX v2/jarvis-llm-brain-final fine tune 7B model"
            if os.path.exists(trained_model):
                model_path = trained_model
            else:
                model_path = "models/jarvis-llm-brain-final"
        
        self.model_path = model_path
        self.wrapper = None
        self.ollama_available = False
        self.cloud_client = None
        self.gguf_model = None
        self.gguf_available = False
        self.ollama_model = "jarvis-brain"
        self.loaded = False
        
        # Conversation context
        self.conversation_history = []
        self.max_history = 5
        
        logger.info("🧠 Initializing Jarvis LLM Brain (Cloud-Optimized)...")
        logger.info(f"📂 Model path: {model_path}")
        
        # Try Cloud LLM first (fastest for production)
        self._check_cloud()
        
        # Try Ollama second (if macOS 14+)
        if not (self.cloud_client and self.cloud_client.available):
            self._check_ollama()
        
        # Try GGUF third (local fallback)
        if not (self.cloud_client and self.cloud_client.available) and not self.ollama_available:
            self._check_gguf()
        
        # Fallback to Python wrapper
        if not self.gguf_available and not self.ollama_available and not (self.cloud_client and self.cloud_client.available):
            self._load_wrapper()
    
    def _check_gguf(self):
        """Check for GGUF models and load with llama-cpp-python"""
        try:
            from llama_cpp import Llama
            
            # Look for GGUF models in models/gguf directory
            gguf_dir = Path("models/gguf")
            if not gguf_dir.exists():
                logger.info("ℹ️  No models/gguf directory found")
                return False
            
            # Find first .gguf file
            gguf_files = list(gguf_dir.glob("*.gguf"))
            if not gguf_files:
                logger.info("ℹ️  No GGUF models found in models/gguf/")
                return False
            
            gguf_path = gguf_files[0]
            logger.info(f"📦 Loading GGUF model: {gguf_path.name}")
            
            # Load model with llama-cpp-python
            # n_ctx: context window, n_gpu_layers: use Metal if available
            self.gguf_model = Llama(
                model_path=str(gguf_path),
                n_ctx=4096,  # Context window
                n_threads=4,  # CPU threads
                n_gpu_layers=-1,  # Use all GPU layers (Metal on Mac)
                verbose=False
            )
            
            self.gguf_available = True
            self.loaded = True
            logger.info("✅ Expert LLM ready via GGUF (fast local inference!)")
            logger.info(f"   Model: {gguf_path.name}")
            logger.info("   Using Metal acceleration if available")
            return True
            
        except ImportError:
            logger.info("ℹ️  llama-cpp-python not installed, skipping GGUF")
            return False
        except Exception as e:
            logger.warning(f"⚠️  GGUF loading failed: {e}")
            return False
    
    def _check_ollama(self):
        """Check if Ollama is available and model exists"""
        try:
            # Check if ollama command exists
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Check if jarvis-brain model exists
                if self.ollama_model in result.stdout:
                    self.ollama_available = True
                    self.loaded = True
                    logger.info("✅ Expert LLM ready via Ollama (fast!)")
                    logger.info(f"   Model: {self.ollama_model}")
                    return True
                else:
                    logger.info("⚠️  Ollama available but jarvis-brain model not found")
                    logger.info(f"   Run: ollama create {self.ollama_model}")
                    return False
            else:
                return False
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.info("⚠️  Ollama not available (checking Cloud LLM)")
            return False
        except Exception as e:
            logger.warning(f"⚠️  Ollama check failed: {e}")
            return False
            
    def _check_cloud(self):
        """Check if Cloud LLM is configured and reachable"""
        try:
            from cloud_llm_client import CloudLLMClient
            base_url = os.getenv("CLOUD_LLM_URL", "").strip()
            if not base_url:
                logger.info("ℹ️  CLOUD_LLM_URL not set; skipping Cloud LLM")
                return False
            self.cloud_client = CloudLLMClient(base_url)
            if self.cloud_client.available:
                self.loaded = True
                logger.info("✅ Expert LLM ready via Cloud LLM API")
                logger.info(f"   URL: {base_url}")
                return True
            return False
        except ImportError as e:
            logger.warning(f"⚠️  Cloud LLM client import failed: {e}")
            return False
        except Exception as e:
            logger.warning(f"⚠️  Cloud LLM check failed: {e}")
            return False
    
    def _load_wrapper(self):
        """Load LLM wrapper (Python 3.11 venv) as fallback"""
        try:
            from llm_wrapper import LLMWrapper
            self.wrapper = LLMWrapper()
            
            if self.wrapper.available:
                if os.path.exists(self.model_path):
                    self.loaded = True
                    logger.info("✅ Expert LLM brain ready (Python 3.11 venv)")
                    logger.info("   Note: Model loads on first use (40-90s on CPU)")
                else:
                    logger.warning(f"⚠️  Model path not found: {self.model_path}")
            else:
                logger.warning("⚠️  Python 3.11 venv not available")
        except ImportError as e:
            logger.warning(f"⚠️  LLM wrapper not available: {e}")
        except Exception as e:
            logger.warning(f"⚠️  LLM initialization failed: {e}")
    
    def is_available(self) -> bool:
        """Check if custom LLM is loaded and ready"""
        return self.loaded and (
            self.gguf_available or
            self.ollama_available or 
            (self.cloud_client and self.cloud_client.available) or
            (self.wrapper and self.wrapper.available)
        )
    
    def generate_response(
        self,
        query: str,
        max_length: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """Generate response using trained LLM"""
        if not self.is_available():
            raise RuntimeError("Custom LLM not available")
        
        # Try GGUF first (fastest local)
        if self.gguf_available:
            return self._generate_gguf(query, max_length, temperature)
        
        # Try Ollama second (fast, if macOS 14+)
        if self.ollama_available:
            return self._generate_ollama(query, max_length, temperature)
        
        # Try Cloud LLM third
        if self.cloud_client and self.cloud_client.available:
            prompt = (
                "You are Jarvis, an expert AI assistant specialized in software engineering. "
                "Provide detailed, accurate responses.\n\nUser: " + query + "\nAssistant:"
            )
            response = self.cloud_client.generate(prompt, max_new_tokens=max_length, temperature=temperature)
            self._update_history(query, response)
            return response.strip()
        
        # Fallback to Python wrapper (slower)
        if self.wrapper and self.wrapper.available:
            response = self.wrapper.generate(query, max_length, temperature)
            self._update_history(query, response)
            return response.strip()
        
        raise RuntimeError("No LLM backend available")
    
    def _generate_gguf(self, query: str, max_length: int, temperature: float) -> str:
        """Generate using GGUF model (fastest local)"""
        try:
            # Build prompt for Mistral Instruct format
            prompt = f"<s>[INST] You are Jarvis, an expert AI assistant specialized in software engineering. Provide detailed, accurate responses.\n\n{query} [/INST]"
            
            # Generate with llama-cpp-python
            response = self.gguf_model(
                prompt,
                max_tokens=max_length,
                temperature=temperature,
                top_p=0.9,
                echo=False,  # Don't repeat the prompt
                stop=["</s>", "[INST]"]  # Stop tokens
            )
            
            # Extract text from response
            text = response['choices'][0]['text'].strip()
            
            self._update_history(query, text)
            return text
            
        except Exception as e:
            logger.error(f"❌ GGUF generation error: {e}")
            raise RuntimeError(f"GGUF generation failed: {e}")
    
    def _generate_ollama(self, query: str, max_length: int, temperature: float) -> str:
        """Generate using Ollama (fast)"""
        try:
            # Use ollama run command
            result = subprocess.run(
                ["ollama", "run", self.ollama_model, query],
                capture_output=True,
                text=True,
                timeout=30  # Ollama should be fast
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                self._update_history(query, response)
                return response
            else:
                raise RuntimeError(f"Ollama error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Ollama generation timed out")
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {e}")
    
    def get_response(self, query: str, max_length: int = 512, temperature: float = 0.7) -> str:
        """
        Wrapper method for compatibility with hybrid_brain
        """
        return self.generate_response(query, max_length, temperature)
    
    def _update_history(self, query: str, response: str):
        """Update conversation history"""
        self.conversation_history.append({
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("🔄 Conversation history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get brain statistics"""
        return {
            'loaded': self.loaded,
            'model_path': self.model_path,
            'gguf_available': self.gguf_available,
            'ollama_available': self.ollama_available,
            'cloud_available': self.cloud_client.available if self.cloud_client else False,
            'wrapper_available': self.wrapper.available if self.wrapper else False,
            'conversation_length': len(self.conversation_history)
        }


# Singleton instance
_brain_instance = None

def get_brain() -> Optional[JarvisLLMBrain]:
    """Get or create singleton brain instance"""
    global _brain_instance
    if _brain_instance is None:
        try:
            _brain_instance = JarvisLLMBrain()
        except Exception as e:
            logger.error(f"Failed to initialize brain: {e}")
            return None
    return _brain_instance


# Test function
def test_brain():
    """Test brain initialization"""
    print("🧪 Testing Jarvis LLM Brain...")
    
    brain = JarvisLLMBrain()
    
    if not brain.is_available():
        print("❌ Brain not available")
        return False
    
    print("✅ Brain loaded successfully!")
    print(f"   GGUF (local): {brain.gguf_available}")
    print(f"   Ollama: {brain.ollama_available}")
    cloud_ok = brain.cloud_client.available if brain.cloud_client else False
    print(f"   Cloud: {cloud_ok}")
    print(f"   Wrapper: {brain.wrapper.available if brain.wrapper else False}")
    
    return True


if __name__ == "__main__":
    test_brain()
