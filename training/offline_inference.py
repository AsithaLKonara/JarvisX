"""
JARVIS AI - Offline Inference Manager
Handles offline AI inference using Ollama, LM Studio, or local models.
"""

import json
import logging
import subprocess
import requests
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import time

class OfflineInferenceManager:
    """
    Manages offline AI inference for Jarvis AI.
    Supports Ollama, LM Studio, and other local model runners.
    """
    
    def __init__(self, inference_type: str = "ollama"):
        """Initialize offline inference manager."""
        self.logger = logging.getLogger(__name__)
        self.inference_type = inference_type.lower()
        self.model_name = None
        self.base_url = None
        self.is_available = False
        
        # Initialize based on type
        if self.inference_type == "ollama":
            self._init_ollama()
        elif self.inference_type == "lm_studio":
            self._init_lm_studio()
        else:
            self.logger.warning(f"Unsupported inference type: {inference_type}")
    
    def _init_ollama(self):
        """Initialize Ollama integration."""
        try:
            self.base_url = "http://localhost:11434"
            self.model_name = "llama2"  # Default model
            
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.is_available = True
                self.logger.info("Ollama is available and running")
            else:
                self.logger.warning("Ollama is not running or not accessible")
        
        except Exception as e:
            self.logger.warning(f"Ollama not available: {e}")
            self.is_available = False
    
    def _init_lm_studio(self):
        """Initialize LM Studio integration."""
        try:
            self.base_url = "http://localhost:1234"
            
            # Check if LM Studio is running
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            if response.status_code == 200:
                self.is_available = True
                self.logger.info("LM Studio is available and running")
            else:
                self.logger.warning("LM Studio is not running or not accessible")
        
        except Exception as e:
            self.logger.warning(f"LM Studio not available: {e}")
            self.is_available = False
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List available models for inference."""
        try:
            if not self.is_available:
                return []
            
            if self.inference_type == "ollama":
                response = requests.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return data.get('models', [])
            
            elif self.inference_type == "lm_studio":
                response = requests.get(f"{self.base_url}/v1/models")
                if response.status_code == 200:
                    data = response.json()
                    return data.get('data', [])
            
            return []
        
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []
    
    def load_model(self, model_name: str) -> bool:
        """Load a specific model for inference."""
        try:
            if not self.is_available:
                self.logger.error("Inference service not available")
                return False
            
            if self.inference_type == "ollama":
                # Pull model if not available
                self._pull_ollama_model(model_name)
                self.model_name = model_name
                return True
            
            elif self.inference_type == "lm_studio":
                # LM Studio handles model loading automatically
                self.model_name = model_name
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Error loading model {model_name}: {e}")
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """Generate response using offline model."""
        try:
            if not self.is_available or not self.model_name:
                return "Offline inference not available"
            
            if self.inference_type == "ollama":
                return self._generate_ollama_response(prompt, max_tokens, temperature)
            elif self.inference_type == "lm_studio":
                return self._generate_lm_studio_response(prompt, max_tokens, temperature)
            else:
                return "Unsupported inference type"
        
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Error: {e}"
    
    def _generate_ollama_response(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate response using Ollama."""
        try:
            data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response generated')
            else:
                self.logger.error(f"Ollama API error: {response.status_code}")
                return "API error occurred"
        
        except Exception as e:
            self.logger.error(f"Error with Ollama generation: {e}")
            return f"Generation error: {e}"
    
    def _generate_lm_studio_response(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate response using LM Studio."""
        try:
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                choices = result.get('choices', [])
                if choices:
                    return choices[0].get('message', {}).get('content', 'No response generated')
                return "No response generated"
            else:
                self.logger.error(f"LM Studio API error: {response.status_code}")
                return "API error occurred"
        
        except Exception as e:
            self.logger.error(f"Error with LM Studio generation: {e}")
            return f"Generation error: {e}"
    
    def _pull_ollama_model(self, model_name: str) -> bool:
        """Pull Ollama model if not available."""
        try:
            self.logger.info(f"Pulling Ollama model: {model_name}")
            
            # Check if model exists
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                existing_models = [model['name'] for model in data.get('models', [])]
                
                if model_name in existing_models:
                    self.logger.info(f"Model {model_name} already available")
                    return True
            
            # Pull model
            data = {"name": model_name, "stream": False}
            response = requests.post(
                f"{self.base_url}/api/pull",
                json=data,
                timeout=300  # 5 minutes timeout for model download
            )
            
            if response.status_code == 200:
                self.logger.info(f"Model {model_name} pulled successfully")
                return True
            else:
                self.logger.error(f"Failed to pull model {model_name}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error pulling Ollama model: {e}")
            return False
    
    def setup_ollama(self) -> Dict[str, Any]:
        """Setup instructions for Ollama."""
        return {
            'instructions': [
                "1. Install Ollama from https://ollama.ai",
                "2. Run: ollama serve",
                "3. Pull a model: ollama pull llama2",
                "4. Verify: ollama list",
                "5. Test: ollama run llama2 'Hello, how are you?'"
            ],
            'recommended_models': [
                "llama2:7b",
                "llama2:13b", 
                "codellama:7b",
                "mistral:7b",
                "neural-chat:7b"
            ],
            'system_requirements': {
                'ram': '8GB minimum, 16GB recommended',
                'storage': '4GB per 7B model, 8GB per 13B model',
                'os': 'macOS, Windows, Linux'
            }
        }
    
    def setup_lm_studio(self) -> Dict[str, Any]:
        """Setup instructions for LM Studio."""
        return {
            'instructions': [
                "1. Download LM Studio from https://lmstudio.ai",
                "2. Install and launch LM Studio",
                "3. Download a model from the model library",
                "4. Load the model in LM Studio",
                "5. Start the local server (usually port 1234)"
            ],
            'recommended_models': [
                "TheBloke/Llama-2-7B-Chat-GGML",
                "TheBloke/Mistral-7B-Instruct-v0.1-GGML",
                "TheBloke/CodeLlama-7B-Instruct-GGML"
            ],
            'system_requirements': {
                'ram': '8GB minimum, 16GB recommended',
                'storage': '4-8GB per model',
                'os': 'Windows, macOS, Linux'
            }
        }
    
    def benchmark_model(self, model_name: str, test_prompts: List[str] = None) -> Dict[str, Any]:
        """Benchmark model performance."""
        try:
            if not self.load_model(model_name):
                return {'error': 'Failed to load model'}
            
            if test_prompts is None:
                test_prompts = [
                    "Hello, how are you?",
                    "Explain quantum computing in simple terms",
                    "Write a Python function to sort a list",
                    "What are the benefits of renewable energy?",
                    "Help me plan a productive day"
                ]
            
            results = {
                'model_name': model_name,
                'test_prompts': len(test_prompts),
                'responses': [],
                'avg_response_time': 0,
                'total_time': 0,
                'success_rate': 0
            }
            
            successful_responses = 0
            total_time = 0
            
            for i, prompt in enumerate(test_prompts):
                start_time = time.time()
                response = self.generate_response(prompt, max_tokens=50)
                end_time = time.time()
                
                response_time = end_time - start_time
                total_time += response_time
                
                if response and not response.startswith("Error"):
                    successful_responses += 1
                
                results['responses'].append({
                    'prompt': prompt,
                    'response': response,
                    'response_time': round(response_time, 2)
                })
                
                self.logger.info(f"Benchmark {i+1}/{len(test_prompts)} completed")
            
            results['total_time'] = round(total_time, 2)
            results['avg_response_time'] = round(total_time / len(test_prompts), 2)
            results['success_rate'] = round(successful_responses / len(test_prompts) * 100, 1)
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error benchmarking model: {e}")
            return {'error': str(e)}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for offline inference."""
        try:
            import psutil
            
            return {
                'inference_type': self.inference_type,
                'is_available': self.is_available,
                'model_loaded': self.model_name,
                'system_ram_gb': round(psutil.virtual_memory().total / (1024**3), 1),
                'available_ram_gb': round(psutil.virtual_memory().available / (1024**3), 1),
                'cpu_count': psutil.cpu_count(),
                'recommended_models': self._get_recommended_models()
            }
        
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {'error': str(e)}
    
    def _get_recommended_models(self) -> List[str]:
        """Get recommended models based on system specs."""
        try:
            import psutil
            
            ram_gb = psutil.virtual_memory().total / (1024**3)
            
            if ram_gb >= 16:
                return ["llama2:13b", "mistral:7b", "codellama:13b"]
            elif ram_gb >= 8:
                return ["llama2:7b", "mistral:7b", "neural-chat:7b"]
            else:
                return ["tinyllama:1.1b", "phi:2.7b"]
        
        except Exception as e:
            self.logger.error(f"Error getting recommended models: {e}")
            return ["llama2:7b"]  # Safe default
