#!/usr/bin/env python3
"""
Jarvis X V2 - Cloud LLM Inference Server
Hugging Face Space with Gradio API
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import gradio as gr

# Load model once at startup
print("🔄 Loading Jarvis LLM Brain...")

# Use 4-bit quantization for free GPU tier
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# Load base model
base_model_name = "mistralai/Mistral-7B-Instruct-v0.1"
print(f"📦 Loading base model: {base_model_name}")
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)

# Load LoRA adapter (if exists in this Space)
adapter_path = "./jarvis-llm-adapter"
if os.path.exists(adapter_path):
    print(f"🔌 Loading LoRA adapter from {adapter_path}")
    model = PeftModel.from_pretrained(base_model, adapter_path)
    print("✅ LoRA adapter loaded!")
else:
    print("⚠️  No LoRA adapter found, using base model")
    model = base_model

model.eval()
print("✅ Model ready for inference!")


def generate_response(prompt: str, max_new_tokens: int = 256, temperature: float = 0.7):
    """Generate response from the model"""
    try:
        # Build Mistral Instruct prompt
        full_prompt = f"<s>[INST] You are Jarvis, an expert AI assistant specialized in software engineering. Provide detailed, accurate responses.\n\n{prompt} [/INST]"
        
        # Tokenize
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=2048)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode
        response = tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )
        
        return response.strip()
        
    except Exception as e:
        return f"Error: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Jarvis X V2 LLM Brain") as demo:
    gr.Markdown("# 🧠 Jarvis X V2 - Expert LLM Brain")
    gr.Markdown("Mistral-7B-Instruct with custom LoRA fine-tuning (137,300 examples across 7 domains + 169 job roles)")
    
    with gr.Tab("Chat Interface"):
        chatbot = gr.Chatbot(label="Jarvis", height=400)
        msg = gr.Textbox(label="Your message", placeholder="Ask me anything...")
        clear = gr.Button("Clear")
        
        def respond(message, chat_history):
            bot_message = generate_response(message)
            chat_history.append((message, bot_message))
            return "", chat_history
        
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        clear.click(lambda: None, None, chatbot, queue=False)
    
    with gr.Tab("API"):
        gr.Markdown("## API Endpoint")
        gr.Markdown("POST to `/generate` with JSON: `{\"prompt\": \"your query\", \"max_new_tokens\": 256, \"temperature\": 0.7}`")
        
        api_prompt = gr.Textbox(label="Prompt", placeholder="Enter your prompt")
        api_max_tokens = gr.Slider(minimum=50, maximum=512, value=256, step=10, label="Max New Tokens")
        api_temperature = gr.Slider(minimum=0.1, maximum=1.0, value=0.7, step=0.1, label="Temperature")
        api_output = gr.Textbox(label="Response", lines=10)
        api_button = gr.Button("Generate")
        
        api_button.click(
            generate_response,
            inputs=[api_prompt, api_max_tokens, api_temperature],
            outputs=api_output
        )

# Create API endpoint
@demo.queue_api
def api_generate(prompt: str, max_new_tokens: int = 256, temperature: float = 0.7):
    """API endpoint for external clients"""
    response = generate_response(prompt, max_new_tokens, temperature)
    return {"response": response, "status": "success"}

# Launch
if __name__ == "__main__":
    demo.queue()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

