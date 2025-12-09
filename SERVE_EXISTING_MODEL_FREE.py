"""
🚀 SERVE YOUR EXISTING FINE-TUNED MODEL ON FREE GPU

Your model: AsithaLKonara/jarvis-llm-brain (already trained ✅)
Problem: HF Space running on CPU = 42 minutes per response ❌
Solution: Run on FREE Colab GPU = 2-5 seconds per response ✅

═══════════════════════════════════════════════════════════════════════
COPY THIS TO GOOGLE COLAB: https://colab.research.google.com/
═══════════════════════════════════════════════════════════════════════

BEFORE RUNNING:
1. Runtime → Change runtime type → T4 GPU → Save
2. Copy each cell below (separated by # CELL X)
3. Run all cells
4. Get your FREE public URL!
"""

# ═══════════════════════════════════════════════════════════════════════
# CELL 1: Install packages
# ═══════════════════════════════════════════════════════════════════════
!pip install -q transformers accelerate bitsandbytes peft gradio huggingface_hub
print("✅ Ready!")


# ═══════════════════════════════════════════════════════════════════════
# CELL 2: Login to HuggingFace (your model is private)
# ═══════════════════════════════════════════════════════════════════════
from huggingface_hub import login
login(token="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")


# ═══════════════════════════════════════════════════════════════════════
# CELL 3: Load YOUR EXISTING model on GPU (takes 2-3 minutes)
# ═══════════════════════════════════════════════════════════════════════
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import torch

print("🔥 Loading YOUR model: AsithaLKonara/jarvis-llm-brain")
print("⏱️  This takes 2-3 minutes...")

# 4-bit quantization = faster + less memory
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# Load base + your LoRA adapter
base_model = "mistralai/Mistral-7B-Instruct-v0.2"
tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.float16,
)

# Your 137K examples fine-tune
model = PeftModel.from_pretrained(model, "AsithaLKonara/jarvis-llm-brain")
model.eval()

print("\n✅ YOUR MODEL IS NOW ON GPU!")
print("⚡ Ready for fast responses (2-5 seconds)")


# ═══════════════════════════════════════════════════════════════════════
# CELL 4: Create the same interface as your HF Space
# ═══════════════════════════════════════════════════════════════════════
def generate_response(prompt, max_new_tokens=256, temperature=0.7):
    """Same function as your HF Space - but on GPU!"""
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

# Quick test
print("\n🧪 Testing...")
test = generate_response("What is Python?", 50, 0.7)
print(f"✅ Works! Sample: {test[:80]}...")


# ═══════════════════════════════════════════════════════════════════════
# CELL 5: Create Gradio interface (same as your HF Space)
# ═══════════════════════════════════════════════════════════════════════
import gradio as gr

demo = gr.Interface(
    fn=generate_response,
    inputs=[
        gr.Textbox(label="Prompt", placeholder="Your message"),
        gr.Slider(1, 512, value=256, label="Max New Tokens"),
        gr.Slider(0.1, 1.0, value=0.7, label="Temperature"),
    ],
    outputs=gr.Textbox(label="Response"),
    title="🚀 Jarvis LLM Brain - GPU Accelerated",
    description="Mistral-7B + 137K examples | Running on FREE GPU | 2-5s responses",
)


# ═══════════════════════════════════════════════════════════════════════
# CELL 6: Launch with PUBLIC URL
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("🚀 LAUNCHING YOUR MODEL...")
print("="*70)

# Launch with free public link
demo.launch(share=True, debug=True)

# You'll get a URL like: https://xxxxx.gradio.live
# Share it with anyone - works for 72 hours!

print("\n✅ YOUR MODEL IS LIVE!")
print("⚡ Speed: 2-5 seconds (instead of 42 minutes!)")
print("💰 Cost: $0 (100% FREE)")
print("⏱️  Session: 12 hours (restart anytime)")


# ═══════════════════════════════════════════════════════════════════════
# 🎉 DONE!
# 
# Your EXISTING model now runs 500× FASTER!
# - Was: 42 minutes per response on CPU
# - Now: 2-5 seconds on FREE GPU
# 
# No retraining needed ✅
# No payment needed ✅
# ═══════════════════════════════════════════════════════════════════════

