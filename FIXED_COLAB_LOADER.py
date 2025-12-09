"""
🔧 FIXED VERSION - Works with Your Model!

Fixes:
1. Proper token authentication for private repos
2. Handles full model (not just LoRA adapter)
3. Works with AsithaLKonara/jarvis-llm-brain
"""

# ═══════════════════════════════════════════════════════════════════════
# CELL 1: Install packages
# ═══════════════════════════════════════════════════════════════════════
!pip install -q transformers accelerate bitsandbytes peft gradio huggingface_hub
print("✅ Ready!")


# ═══════════════════════════════════════════════════════════════════════
# CELL 2: Set token properly (FIXED!)
# ═══════════════════════════════════════════════════════════════════════
import os
from huggingface_hub import login

# Set token in environment
HF_TOKEN = "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"
os.environ['HF_TOKEN'] = HF_TOKEN
os.environ['HUGGING_FACE_HUB_TOKEN'] = HF_TOKEN

# Login
login(token=HF_TOKEN)
print("✅ Logged in with token!")


# ═══════════════════════════════════════════════════════════════════════
# CELL 3: Check GPU
# ═══════════════════════════════════════════════════════════════════════
import torch
print(f"🔥 GPU: {torch.cuda.get_device_name(0)}")
print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")


# ═══════════════════════════════════════════════════════════════════════
# CELL 4: Load YOUR model (FIXED - tries both methods!)
# ═══════════════════════════════════════════════════════════════════════
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import torch

print("🔥 Loading YOUR model: AsithaLKonara/jarvis-llm-brain")
print("⏱️  This takes 2-3 minutes...")

# Check if it's a LoRA adapter or full model
from huggingface_hub import hf_hub_download, list_repo_files

your_model = "AsithaLKonara/jarvis-llm-brain"

try:
    # Check what files are in the repo
    print("\n🔍 Checking model type...")
    files = list_repo_files(your_model, token=HF_TOKEN)
    
    is_lora = "adapter_config.json" in files
    is_full_model = "config.json" in files
    
    print(f"📦 Model type detected:")
    print(f"   - LoRA adapter: {is_lora}")
    print(f"   - Full model: {is_full_model}")
    
except Exception as e:
    print(f"⚠️  Couldn't check files: {e}")
    print("   Trying as full model...")
    is_lora = False
    is_full_model = True

# Quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

print("\n📥 Loading model...")

if is_lora:
    # METHOD 1: Load as LoRA adapter
    print("📦 Loading as LoRA adapter...")
    base_model = "mistralai/Mistral-7B-Instruct-v0.2"
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
        token=HF_TOKEN,
    )
    model = PeftModel.from_pretrained(model, your_model, token=HF_TOKEN)
    
else:
    # METHOD 2: Load as full fine-tuned model
    print("📦 Loading as full fine-tuned model...")
    tokenizer = AutoTokenizer.from_pretrained(your_model, token=HF_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(
        your_model,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
        token=HF_TOKEN,
    )

model.eval()

print("\n" + "="*70)
print("✅ YOUR MODEL IS LOADED ON GPU!")
print("⚡ Ready for fast responses!")
print("="*70)


# ═══════════════════════════════════════════════════════════════════════
# CELL 5: Create inference function
# ═══════════════════════════════════════════════════════════════════════
def generate_response(prompt, max_new_tokens=256, temperature=0.7):
    """Generate response from YOUR model"""
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=int(max_new_tokens),
            temperature=float(temperature),
            do_sample=True,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if response.startswith(prompt):
        response = response[len(prompt):].strip()
    
    return response

# Speed test
print("\n🧪 Testing...")
import time
start = time.time()
test = generate_response("What is Python?", 50, 0.7)
elapsed = time.time() - start

print(f"✅ Response time: {elapsed:.2f} seconds")
print(f"📝 Sample: {test[:100]}...")


# ═══════════════════════════════════════════════════════════════════════
# CELL 6: Create Gradio interface
# ═══════════════════════════════════════════════════════════════════════
import gradio as gr

demo = gr.Interface(
    fn=generate_response,
    inputs=[
        gr.Textbox(label="💬 Your Message", placeholder="Ask anything...", lines=3),
        gr.Slider(1, 512, value=256, label="📏 Max Tokens"),
        gr.Slider(0.1, 1.0, value=0.7, label="🌡️ Temperature"),
    ],
    outputs=gr.Textbox(label="🤖 Jarvis Response", lines=10),
    title="🚀 Jarvis LLM Brain - GPU Accelerated",
    description=f"""⚡ Your fine-tuned model on {torch.cuda.get_device_name(0)}  
💰 Colab Pro - 4-bit quantization  
⏱️ Fast responses (2-5 seconds!)""",
    examples=[
        ["What is machine learning?", 150, 0.7],
        ["Explain Python", 200, 0.7],
    ],
)

print("✅ Interface ready!")


# ═══════════════════════════════════════════════════════════════════════
# CELL 7: Launch with PUBLIC URL
# ═══════════════════════════════════════════════════════════════════════
print("\n🚀 Launching...")
demo.launch(share=True, debug=False)

print("\n✅ YOUR MODEL IS LIVE!")
print("🌐 Share the URL above with anyone!")
print("⚡ Enjoy fast responses!")

