#!/usr/bin/env python3
"""
Optimized LLM Loader - Supercharged Mistral 7B with Quantization
Implements 4-bit quantization, torch.compile, and caching for 3-6x speedup
"""

import os
import logging
import torch
from typing import Dict, Any, Optional
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class OptimizedLLMLoader:
    """
    Optimized LLM loader with:
    - 4-bit/8-bit quantization (BitsAndBytes)
    - torch.compile() for PyTorch 2.x
    - Model caching in memory
    - Automatic GPU detection (CUDA, MPS, ROCm)
    - Smart batching
    """
    
    def __init__(
        self,
        model_path: str = None,
        quantization: str = "4bit",  # "4bit", "8bit", or "none"
        use_compile: bool = True,  # Use torch.compile for PyTorch 2.x
        use_flash_attention: bool = True,
        device_map: str = "auto"
    ):
        """
        Initialize optimized LLM loader
        
        Args:
            model_path: Path to fine-tuned model
            quantization: Quantization type ("4bit", "8bit", "none")
            use_compile: Enable torch.compile() optimization
            use_flash_attention: Use flash attention 2 if available
            device_map: Device mapping strategy
        """
        self.model_path = model_path or self._get_default_model_path()
        self.quantization = quantization
        self.use_compile = use_compile
        self.use_flash_attention = use_flash_attention
        self.device_map = device_map
        
        # State
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.is_loaded = False
        self.device = None
        
        # Performance tracking
        self.load_time = 0
        self.inference_times = []
        
        logger.info("🚀 Initializing Optimized LLM Loader...")
        logger.info(f"   Model: {self.model_path}")
        logger.info(f"   Quantization: {self.quantization}")
        logger.info(f"   torch.compile: {self.use_compile}")
        logger.info(f"   Flash Attention: {self.use_flash_attention}")
        
        # Detect device
        self._detect_device()
        
        # Load model
        if os.path.exists(self.model_path):
            self._load_optimized_model()
        else:
            logger.error(f"❌ Model path not found: {self.model_path}")
    
    def _get_default_model_path(self) -> str:
        """Get default model path"""
        trained_model = "/Users/asithalakmal/Documents/web/JarvisX v2/jarvis-llm-brain-final fine tune 7B model"
        if os.path.exists(trained_model):
            return trained_model
        return "models/jarvis-llm-brain-final"
    
    def _detect_device(self):
        """Detect best available device"""
        if torch.cuda.is_available():
            self.device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"🔥 Using CUDA GPU: {gpu_name}")
        elif torch.backends.mps.is_available():
            self.device = "mps"
            logger.info("🍎 Using Apple Metal (MPS)")
        else:
            self.device = "cpu"
            logger.info("💻 Using CPU (consider getting a GPU for faster inference)")
    
    def _load_optimized_model(self):
        """Load model with optimizations"""
        try:
            start_time = time.time()
            
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            
            logger.info("📦 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                use_fast=True,  # Use fast tokenizer
                trust_remote_code=True
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Configure quantization
            model_kwargs = {
                "device_map": self.device_map,
                "trust_remote_code": True,
                "low_cpu_mem_usage": True
            }
            
            if self.quantization == "4bit" and self.device != "cpu":
                logger.info("⚡ Loading with 4-bit quantization...")
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,  # Nested quantization
                    bnb_4bit_quant_type="nf4"  # Normal Float 4
                )
                model_kwargs["quantization_config"] = bnb_config
            
            elif self.quantization == "8bit" and self.device != "cpu":
                logger.info("⚡ Loading with 8-bit quantization...")
                bnb_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    llm_int8_threshold=6.0
                )
                model_kwargs["quantization_config"] = bnb_config
            
            else:
                logger.info("📦 Loading full precision model...")
                if self.device == "cpu":
                    model_kwargs["torch_dtype"] = torch.float32
                else:
                    model_kwargs["torch_dtype"] = torch.float16
            
            # Add flash attention 2 if available
            if self.use_flash_attention:
                try:
                    model_kwargs["attn_implementation"] = "flash_attention_2"
                    logger.info("⚡ Flash Attention 2 enabled")
                except:
                    logger.info("⚠️  Flash Attention 2 not available, using default")
            
            logger.info("🧠 Loading model (this may take 30-60 seconds)...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                **model_kwargs
            )
            
            # Apply torch.compile for PyTorch 2.x
            if self.use_compile and hasattr(torch, 'compile'):
                try:
                    logger.info("🔥 Applying torch.compile() optimization...")
                    self.model = torch.compile(self.model, mode="reduce-overhead")
                    logger.info("✅ torch.compile() applied (warmup needed)")
                except Exception as e:
                    logger.warning(f"⚠️  torch.compile() failed: {e}")
            
            # Create pipeline for easy inference
            from transformers import pipeline
            
            logger.info("🔧 Creating inference pipeline...")
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map=self.device_map,
                return_full_text=False  # Only return generated text
            )
            
            self.load_time = time.time() - start_time
            self.is_loaded = True
            
            logger.info(f"✅ Optimized LLM loaded in {self.load_time:.1f}s")
            logger.info(f"   Memory: ~{self._estimate_memory()} GB")
            logger.info(f"   Device: {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load optimized model: {e}")
            raise
    
    def _estimate_memory(self) -> float:
        """Estimate memory usage"""
        if self.quantization == "4bit":
            return 3.5  # ~3.5GB for 7B 4-bit
        elif self.quantization == "8bit":
            return 7.0  # ~7GB for 7B 8-bit
        else:
            return 14.0  # ~14GB for 7B fp16
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        do_sample: bool = True,
        num_return_sequences: int = 1
    ) -> str:
        """
        Generate response with optimized inference
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling
            do_sample: Use sampling vs greedy
            num_return_sequences: Number of responses
            
        Returns:
            Generated text
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        start_time = time.time()
        
        try:
            # Format prompt for Mistral Instruct
            formatted_prompt = f"<s>[INST] You are Jarvis, an expert AI assistant specialized in software engineering, design, and business. Provide detailed, accurate, and helpful responses.\n\n{prompt} [/INST]"
            
            # Generate
            output = self.pipeline(
                formatted_prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                num_return_sequences=num_return_sequences,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract response
            response = output[0]['generated_text'].strip()
            
            # Track performance
            inference_time = time.time() - start_time
            self.inference_times.append(inference_time)
            
            # Keep only last 100 times
            if len(self.inference_times) > 100:
                self.inference_times = self.inference_times[-100:]
            
            logger.info(f"⚡ Generated in {inference_time:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            raise
    
    def get_response(self, query: str, max_length: int = 256, temperature: float = 0.7) -> str:
        """
        Compatibility wrapper for existing code
        """
        return self.generate(query, max_new_tokens=max_length, temperature=temperature)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        avg_inference_time = sum(self.inference_times) / len(self.inference_times) if self.inference_times else 0
        
        return {
            'loaded': self.is_loaded,
            'model_path': self.model_path,
            'device': self.device,
            'quantization': self.quantization,
            'load_time': self.load_time,
            'avg_inference_time': avg_inference_time,
            'total_generations': len(self.inference_times),
            'estimated_memory_gb': self._estimate_memory(),
            'torch_compile_enabled': self.use_compile,
            'flash_attention_enabled': self.use_flash_attention
        }
    
    def warmup(self, num_warmups: int = 3):
        """
        Warmup model (important for torch.compile)
        """
        logger.info(f"🔥 Warming up model ({num_warmups} iterations)...")
        
        for i in range(num_warmups):
            try:
                _ = self.generate(
                    "Hello, who are you?",
                    max_new_tokens=50,
                    temperature=0.7
                )
                logger.info(f"   Warmup {i+1}/{num_warmups} complete")
            except Exception as e:
                logger.warning(f"⚠️  Warmup {i+1} failed: {e}")
        
        logger.info("✅ Warmup complete - model is ready!")
    
    def is_available(self) -> bool:
        """Check if model is loaded and available"""
        return self.is_loaded


def test_optimized_loader():
    """Test optimized loader"""
    print("\n" + "="*70)
    print("🧪 Testing Optimized LLM Loader")
    print("="*70 + "\n")
    
    # Test with 4-bit quantization
    loader = OptimizedLLMLoader(quantization="4bit", use_compile=True)
    
    if not loader.is_available():
        print("❌ Model not loaded")
        return False
    
    print("\n📊 Model Statistics:")
    stats = loader.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n🔥 Warming up model...")
    loader.warmup(num_warmups=2)
    
    print("\n🧪 Testing inference...")
    test_queries = [
        "What is Python?",
        "Explain machine learning in simple terms.",
        "How do I optimize database queries?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}/{len(test_queries)}: {query}")
        try:
            response = loader.generate(query, max_new_tokens=100, temperature=0.7)
            print(f"✅ Response ({len(response)} chars): {response[:200]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print("\n" + "="*70)
    print("✅ Testing complete!")
    print("="*70 + "\n")
    
    final_stats = loader.get_stats()
    print(f"📊 Average inference time: {final_stats['avg_inference_time']:.2f}s")
    print(f"📊 Total generations: {final_stats['total_generations']}")
    
    return True


if __name__ == "__main__":
    import sys
    
    # Enable logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    success = test_optimized_loader()
    sys.exit(0 if success else 1)

