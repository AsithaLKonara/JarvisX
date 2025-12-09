#!/usr/bin/env python3
"""
Hugging Face Space Configuration
Your deployed model: Jarvis X V2 - Expert LLM Brain
"""

# Your HF Space URL (from your screenshot)
HF_SPACE_URL = "https://asithalkonara-jarvis-llm-brain.hf.space"

# API endpoint
API_ENDPOINT = f"{HF_SPACE_URL}/generate"

# Model configuration
MODEL_CONFIG = {
    'space_name': 'AsithaLKonara/jarvis-llm-brain',
    'model_type': 'Mistral-7B-Instruct with LoRA',
    'training_examples': 137300,
    'domains': 7,
    'job_roles': 169
}

# Default parameters
DEFAULT_PARAMS = {
    'max_new_tokens': 256,
    'temperature': 0.7
}

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   ✅ CONFIGURATION LOADED                                               ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

Your HF Space: {space}
API Endpoint: {api}

Model: {model}
Training: {examples} examples, {domains} domains, {roles} job roles

Ready to use! 🚀
""".format(
    space=HF_SPACE_URL,
    api=API_ENDPOINT,
    model=MODEL_CONFIG['model_type'],
    examples=MODEL_CONFIG['training_examples'],
    domains=MODEL_CONFIG['domains'],
    roles=MODEL_CONFIG['job_roles']
))

