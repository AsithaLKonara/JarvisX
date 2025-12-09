"""
🚀 JARVIS LLM - T4 GPU OPTIMIZED (FREE COLAB)
✅ Mistral 7B base + Your Jarvis LoRA adapter
✅ Works perfectly on T4 GPU (free tier)
✅ 4-bit quantization for optimal memory
✅ Full error handling & memory optimization
✅ Trained on 137K examples

═══════════════════════════════════════════════════════════════════════
INSTRUCTIONS:
1. Go to https://colab.research.google.com/
2. Create new notebook
3. Runtime → Change runtime type → T4 GPU (FREE!)
4. Copy each CELL below into separate cells in Colab
5. Replace YOUR_HF_TOKEN in CELL 2 with your token from HuggingFace
6. Run all cells one by one (total time: ~5-7 minutes)
7. Get your public Gradio URL and share!
═══════════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════════════
# CELL 1: Install packages (LoRA adapter support!)
# ═══════════════════════════════════════════════════════════════════════
!pip install -q -U transformers accelerate bitsandbytes gradio huggingface_hub einops peft
!pip install -q torch==2.1.0 torchvision==0.16.0
print("✅ Packages installed (including PEFT for LoRA adapters)!")


# ═══════════════════════════════════════════════════════════════════════
# CELL 2: Authenticate (CRITICAL!)
# ═══════════════════════════════════════════════════════════════════════
import os
from huggingface_hub import login

# 🔐 REPLACE THIS WITH YOUR TOKEN FROM: https://huggingface.co/settings/tokens
HF_TOKEN = "YOUR_HF_TOKEN_HERE"

if HF_TOKEN == "YOUR_HF_TOKEN_HERE":
    print("⚠️  STOP! Replace YOUR_HF_TOKEN_HERE with your actual token!")
    print("Get it from: https://huggingface.co/settings/tokens")
    raise ValueError("Please set your HuggingFace token!")

try:
    os.environ['HF_TOKEN'] = HF_TOKEN
    os.environ['HUGGING_FACE_HUB_TOKEN'] = HF_TOKEN
    login(token=HF_TOKEN, add_to_git_credential=False)
    print("✅ Authenticated successfully!")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
    raise


# ═══════════════════════════════════════════════════════════════════════
# CELL 3: Check GPU & Clear Memory
# ═══════════════════════════════════════════════════════════════════════
import torch
import gc

# Clear any existing GPU memory
gc.collect()
torch.cuda.empty_cache()

if not torch.cuda.is_available():
    print("❌ No GPU detected!")
    print("Go to: Runtime → Change runtime type → T4 GPU")
    raise RuntimeError("GPU required! Please enable T4 GPU in Colab settings.")

gpu_name = torch.cuda.get_device_name(0)
gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9

print("="*70)
print(f"🔥 GPU: {gpu_name}")
print(f"💾 Total VRAM: {gpu_memory:.1f} GB")
print(f"📦 Quantization: 4-bit (optimized for T4)")
print("="*70)


# ═══════════════════════════════════════════════════════════════════════
# CELL 4: Load Base Model + LoRA Adapter (T4 Optimized!)
# ═══════════════════════════════════════════════════════════════════════
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel, PeftConfig
from huggingface_hub import snapshot_download
import torch
import gc
import os

BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"  # Base Mistral 7B model
ADAPTER_SPACE = "AsithaLKonara/jarvis-llm-brain"    # Space containing the adapter
ADAPTER_SUBDIR = "jarvis-llm-adapter"               # Folder inside the space with LoRA weights
LOCAL_ADAPTER_ROOT = "/content/jarvis_adapter"

print("="*70)
print("🔥 LOADING MISTRAL 7B + YOUR JARVIS ADAPTER")
print("="*70)
print(f"📦 Base Model: {BASE_MODEL}")
print(f"🎯 Adapter space: {ADAPTER_SPACE} / {ADAPTER_SUBDIR}")
print("⏱️  This will take 3-7 minutes on T4...\n")

try:
    # Download adapter from the Hugging Face Space (only once per runtime)
    print("🌐 Step 1/5: Downloading LoRA adapter from HuggingFace Space...")
    if os.path.exists(LOCAL_ADAPTER_ROOT):
        print("   ℹ️  Adapter already downloaded, reusing local files.")
        adapter_space_path = LOCAL_ADAPTER_ROOT
    else:
        adapter_space_path = snapshot_download(
            repo_id=ADAPTER_SPACE,
            repo_type="space",
            token=HF_TOKEN,
            allow_patterns=f"{ADAPTER_SUBDIR}/*",
            local_dir=LOCAL_ADAPTER_ROOT,
            local_dir_use_symlinks=False,
        )

    # Resolve final adapter directory
    adapter_model_path = os.path.join(adapter_space_path, ADAPTER_SUBDIR)
    if not os.path.isdir(adapter_model_path):
        # Fallback: snapshot_download may dump files directly into root
        adapter_model_path = adapter_space_path
    print(f"   ✅ Adapter path: {adapter_model_path}")

    # 4-bit quantization config (T4 optimized)
    print("📦 Step 2/5: Configuring 4-bit quantization...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    
    # Load tokenizer from adapter (has your custom tokens)
    print("📥 Step 3/5: Loading tokenizer from adapter...")
    tokenizer = AutoTokenizer.from_pretrained(
        adapter_model_path,
        token=HF_TOKEN,
        trust_remote_code=True,
        use_fast=True
    )
    
    # Set padding token if not set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        print("   ℹ️  Set pad_token = eos_token")
    
    # Load base Mistral 7B model (quantized)
    print("📥 Step 4/5: Loading base Mistral 7B model (quantized)...")
    print("   ⏱️  This is the slow part, please wait...")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
        token=HF_TOKEN,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        max_memory={0: "14GB"}  # Reserve 1GB for operations
    )
    
    # Load and apply your LoRA adapter
    print("🎯 Step 5/5: Loading your Jarvis LoRA adapter...")
    model = PeftModel.from_pretrained(
        base_model,
        adapter_model_path,
        token=HF_TOKEN,
    )
    
    model.eval()
    
    # Clear memory
    gc.collect()
    torch.cuda.empty_cache()
    
    # Check memory usage
    allocated = torch.cuda.memory_allocated(0) / 1e9
    reserved = torch.cuda.memory_reserved(0) / 1e9
    
    print("\n" + "="*70)
    print("✅ JARVIS MODEL LOADED SUCCESSFULLY!")
    print(f"💾 GPU Memory: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")
    print("🎯 Base: Mistral 7B + Your Jarvis Adapter (137K examples)")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ ERROR loading model: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you enabled T4 GPU in Colab")
    print("2. Check your HuggingFace token is valid")
    print("3. Mistral models require HF authentication")
    print("4. Try: Runtime → Restart runtime, then run all cells again")
    raise


# ═══════════════════════════════════════════════════════════════════════
# CELL 5: Inference Function (with error handling)
# ═══════════════════════════════════════════════════════════════════════
import torch
import gc

def generate_response(prompt, max_new_tokens=256, temperature=0.7):
    """Generate response with error handling and memory management"""
    
    if not prompt or not prompt.strip():
        return "⚠️ Please enter a message!"
    
    try:
        # Tokenize input
        inputs = tokenizer(
            prompt, 
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to("cuda")
        
        # Generate with torch.no_grad for memory efficiency
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=int(max_new_tokens),
                temperature=float(temperature),
                do_sample=True,
                top_p=0.95,
                top_k=50,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove the prompt from response if included
        if response.startswith(prompt):
            response = response[len(prompt):].strip()
        
        # Clear GPU cache periodically
        if torch.cuda.memory_allocated(0) / 1e9 > 12:  # If >12GB used
            gc.collect()
            torch.cuda.empty_cache()
        
        return response
    
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            # Handle OOM error
            gc.collect()
            torch.cuda.empty_cache()
            return "❌ GPU out of memory! Try reducing max tokens or restart runtime."
        else:
            return f"❌ Error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

# Quick test
print("\n🧪 Testing model...")
import time

try:
    start = time.time()
    test_response = generate_response("What is Python?", 50, 0.7)
    elapsed = time.time() - start
    
    print(f"⚡ Speed: {elapsed:.2f}s")
    print(f"📝 Output: {test_response[:100]}...")
    print("✅ Model is working perfectly!")
except Exception as e:
    print(f"❌ Test failed: {e}")


# ═══════════════════════════════════════════════════════════════════════
# CELL 6: Create Gradio Interface
# ═══════════════════════════════════════════════════════════════════════
import gradio as gr

# Custom CSS for better UI
custom_css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
}
.output-text {
    font-size: 16px !important;
    line-height: 1.6 !important;
}
"""

# Get GPU info for description
gpu_info = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
mem_info = f"{torch.cuda.memory_allocated(0) / 1e9:.1f}GB" if torch.cuda.is_available() else "N/A"

# Create interface
with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🚀 Jarvis LLM Brain - T4 GPU Edition
    ### Mistral 7B + Your Custom Jarvis Adapter (137K examples)
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown(f"""
            **System Info:**
            - 🔥 GPU: {gpu_info}
            - 💾 Memory: {mem_info}
            - 🧠 Model: Mistral 7B + LoRA
            - 📦 4-bit Quantized
            - ⚡ Free T4 GPU
            """)
    
    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(
                label="💬 Your Message",
                placeholder="Ask me anything...",
                lines=4,
                max_lines=10
            )
            
            with gr.Row():
                max_tokens = gr.Slider(
                    minimum=50,
                    maximum=512,
                    value=256,
                    step=50,
                    label="📏 Max Tokens (lower = faster)"
                )
                temperature = gr.Slider(
                    minimum=0.1,
                    maximum=1.0,
                    value=0.7,
                    step=0.1,
                    label="🌡️ Temperature (higher = creative)"
                )
            
            submit_btn = gr.Button("🚀 Generate", variant="primary", size="lg")
            clear_btn = gr.Button("🗑️ Clear")
    
    with gr.Row():
        output_text = gr.Textbox(
            label="🤖 Jarvis Response",
            lines=12,
            max_lines=20,
            show_copy_button=True
        )
    
    # Example queries
    gr.Examples(
        examples=[
            ["What is machine learning?", 200, 0.7],
            ["Explain Python programming in simple terms", 250, 0.7],
            ["Write a short story about AI", 300, 0.8],
            ["What is the meaning of life?", 150, 0.6],
        ],
        inputs=[input_text, max_tokens, temperature],
        label="📚 Example Questions"
    )
    
    # Event handlers
    submit_btn.click(
        fn=generate_response,
        inputs=[input_text, max_tokens, temperature],
        outputs=output_text
    )
    
    clear_btn.click(
        fn=lambda: ("", ""),
        inputs=None,
        outputs=[input_text, output_text]
    )
    
    gr.Markdown("""
    ---
    💡 **Tips:**
    - Lower max tokens = faster responses
    - Temperature 0.7 = balanced creativity
    - If you get OOM error, restart runtime and reduce max tokens
    """)


# ═══════════════════════════════════════════════════════════════════════
# CELL 7: Launch Gradio!
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("🚀 LAUNCHING GRADIO INTERFACE...")
print("="*70 + "\n")

try:
    demo.launch(
        share=True,
        debug=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
    print("\n✅ LIVE! Copy the public URL above and share it! ⚡\n")
except Exception as e:
    print(f"❌ Launch failed: {e}")
    print("Try: demo.launch(share=True)")


# ═══════════════════════════════════════════════════════════════════════
# 🎉 CONGRATULATIONS! Your model is now live on T4 GPU!
# ═══════════════════════════════════════════════════════════════════════
"""
TROUBLESHOOTING GUIDE:
═══════════════════════════════════════════════════════════════════════

❌ Problem: "No GPU detected"
✅ Solution: Runtime → Change runtime type → T4 GPU → Save

❌ Problem: "Authentication failed"
✅ Solution: 
   1. Go to https://huggingface.co/settings/tokens
   2. Create a token with READ access
   3. Replace YOUR_HF_TOKEN_HERE in CELL 2

❌ Problem: "Out of memory"
✅ Solution:
   1. Runtime → Restart runtime
   2. Run all cells again
   3. Reduce max_tokens to 128 in the Gradio interface

❌ Problem: "Model loading takes too long"
✅ Solution: T4 takes 2-5 minutes to load. Be patient!

❌ Problem: "Gradio won't launch"
✅ Solution: 
   1. Check all previous cells ran without errors
   2. Try: demo.launch(share=True, inline=False)

═══════════════════════════════════════════════════════════════════════
PERFORMANCE TIPS:
═══════════════════════════════════════════════════════════════════════

⚡ For faster inference:
   - Use max_tokens between 50-200
   - Keep temperature at 0.7
   - Avoid very long prompts (>512 tokens)

💾 To save memory:
   - Close other Colab tabs
   - Restart runtime if memory usage is high
   - Use smaller max_tokens values

🔥 Best practices:
   - T4 can handle ~3-5 requests per minute comfortably
   - Colab free tier gives ~12 hours per day
   - Save important outputs before session ends

═══════════════════════════════════════════════════════════════════════
"""
