#!/usr/bin/env python3
"""
LoRA Model Loader - Load Mistral 7B + Your Fine-tuned LoRA Adapter
"""

import os
import logging
import torch
from typing import Optional, Dict, Any
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class LoRAModelLoader:
    """
    Load Mistral 7B base model + your LoRA adapter
    With 4-bit quantization for fast inference on 8GB RAM
    """
    
    def __init__(
        self,
        base_model: str = "mistralai/Mistral-7B-Instruct-v0.2",
        adapter_path: str = None,
        quantization: str = "4bit",
        device_map: str = "auto"
    ):
        """
        Initialize LoRA model loader
        
        Args:
            base_model: Base model from HuggingFace (Mistral 7B)
            adapter_path: Path to your LoRA adapter
            quantization: Quantization type ("4bit", "8bit", "none")
            device_map: Device mapping
        """
        self.base_model = base_model
        self.adapter_path = adapter_path or self._get_default_adapter_path()
        self.quantization = quantization
        self.device_map = device_map
        
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.is_loaded = False
        
        logger.info("🚀 Initializing LoRA Model Loader...")
        logger.info(f"   Base model: {self.base_model}")
        logger.info(f"   LoRA adapter: {self.adapter_path}")
        logger.info(f"   Quantization: {self.quantization}")
        
        if os.path.exists(self.adapter_path):
            self._load_model_with_adapter()
        else:
            logger.error(f"❌ Adapter not found: {self.adapter_path}")
    
    def _get_default_adapter_path(self) -> str:
        """Get default adapter path"""
        return "/Users/asithalakmal/Documents/web/JarvisX v2/jarvis-llm-brain-final fine tune 7B model"
    
    def _load_model_with_adapter(self):
        """Load base model + LoRA adapter with optimizations"""
        try:
            start_time = time.time()
            
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            from peft import PeftModel
            
            logger.info("📦 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.adapter_path,
                use_fast=True,
                trust_remote_code=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Configure quantization
            model_kwargs = {
                "device_map": self.device_map,
                "trust_remote_code": True,
                "low_cpu_mem_usage": True
            }
            
            if self.quantization == "4bit":
                logger.info("⚡ Loading BASE model with 4-bit quantization...")
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                model_kwargs["quantization_config"] = bnb_config
            
            # Load base model
            logger.info(f"🧠 Loading base model: {self.base_model}")
            logger.info("   ⏳ This will download ~14GB on first run (may take 10-30 min)")
            logger.info("   ⏳ Subsequent runs will use cached model (faster)")
            
            base_model = AutoModelForCausalLM.from_pretrained(
                self.base_model,
                **model_kwargs
            )
            
            logger.info("✅ Base model loaded")
            
            # Load and merge LoRA adapter
            logger.info(f"🔧 Loading LoRA adapter from: {self.adapter_path}")
            
            self.model = PeftModel.from_pretrained(
                base_model,
                self.adapter_path,
                device_map=self.device_map
            )
            
            logger.info("✅ LoRA adapter applied")
            
            # Optional: Merge adapter for faster inference
            # logger.info("🔄 Merging adapter into base model...")
            # self.model = self.model.merge_and_unload()
            
            # Create pipeline
            from transformers import pipeline
            
            logger.info("🔧 Creating inference pipeline...")
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map=self.device_map,
                return_full_text=False
            )
            
            load_time = time.time() - start_time
            self.is_loaded = True
            
            logger.info(f"✅ Model ready in {load_time:.1f}s")
            logger.info(f"   Memory: ~3.5GB (with 4-bit quantization)")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            logger.error("\nPossible issues:")
            logger.error("  1. Missing dependencies: pip install transformers peft bitsandbytes")
            logger.error("  2. Base model not cached: Will download on first run")
            logger.error("  3. Insufficient memory: Use 4-bit quantization")
            raise
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """Generate response"""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # Format for Mistral Instruct
            formatted_prompt = f"<s>[INST] You are Jarvis, an expert AI assistant. Provide detailed, accurate responses.\n\n{prompt} [/INST]"
            
            output = self.pipeline(
                formatted_prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
            
            response = output[0]['generated_text'].strip()
            return response
            
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            raise
    
    def get_response(self, query: str, max_length: int = 256, temperature: float = 0.7) -> str:
        """Compatibility wrapper"""
        return self.generate(query, max_new_tokens=max_length, temperature=temperature)
    
    def is_available(self) -> bool:
        """Check if model is ready"""
        return self.is_loaded


def test_lora_loader():
    """Test LoRA loader"""
    print("\n" + "="*70)
    print("🧪 Testing LoRA Model Loader")
    print("="*70 + "\n")
    
    try:
        loader = LoRAModelLoader(quantization="4bit")
        
        if not loader.is_available():
            print("❌ Model not loaded")
            return False
        
        print("\n🧪 Testing inference...")
        
        test_query = "What is Python?"
        print(f"Query: {test_query}")
        
        response = loader.generate(test_query, max_new_tokens=100)
        
        print(f"\n✅ Response:\n{response}\n")
        print("="*70)
        print("✅ LoRA model working!")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        print("Make sure you have:")
        print("  1. pip install transformers peft bitsandbytes torch")
        print("  2. Internet connection (for first download)")
        print("  3. ~8GB free disk space (for base model cache)")
        return False


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    success = test_lora_loader()
    sys.exit(0 if success else 1)

