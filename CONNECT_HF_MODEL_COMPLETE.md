# 🤗 Connect Your Hugging Face Model - Complete Guide

## 3 Ways to Connect Your HF Model

---

## 🎯 **Scenario 1: Model Already on Hugging Face Hub**

If your model is uploaded to HF (e.g., `your-username/jarvis-mistral-7b`):

### **Method A: Use Directly from Hub**

```python
# Edit training_gui.py, add at the top:

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from transformers import pipeline
import torch

# Your HF model ID
HF_MODEL_ID = "your-username/jarvis-mistral-7b-lora"  # ← Change this!

# Load directly from HF Hub
def initialize_brain():
    global brain
    
    try:
        print(f"📥 Loading model from HF Hub: {HF_MODEL_ID}")
        
        # Configure 4-bit quantization
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        # Load model from HF Hub
        model = AutoModelForCausalLM.from_pretrained(
            HF_MODEL_ID,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID)
        
        # Create pipeline
        brain = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device_map="auto",
            return_full_text=False
        )
        
        print("✅ Model loaded from HF Hub!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
```

### **Method B: Use with LoRA (If it's a LoRA adapter)**

```python
from peft import AutoPeftModelForCausalLM
from transformers import BitsAndBytesConfig
import torch

HF_MODEL_ID = "your-username/jarvis-mistral-7b-lora"

# Configure quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# Load base model + LoRA adapter in one call!
model = AutoPeftModelForCausalLM.from_pretrained(
    HF_MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID)

print("✅ Model with LoRA adapter loaded from HF Hub!")
```

---

## 🎯 **Scenario 2: Model Is Local (Not Uploaded Yet)**

If your model is only on your computer:

### **Step 1: Upload to Hugging Face Hub**

```bash
# Install HF CLI
pip install huggingface-hub

# Login
huggingface-cli login
# Enter your token from: https://huggingface.co/settings/tokens

# Upload your model
python3 << 'EOF'
from huggingface_hub import HfApi

api = HfApi()

# Upload your LoRA adapter
api.upload_folder(
    folder_path="jarvis-llm-brain-final fine tune 7B model",
    repo_id="YOUR-USERNAME/jarvis-mistral-7b-lora",  # ← CHANGE THIS!
    repo_type="model",
    commit_message="Upload Jarvis fine-tuned LoRA adapter"
)

print("✅ Model uploaded!")
print("View at: https://huggingface.co/YOUR-USERNAME/jarvis-mistral-7b-lora")
EOF
```

### **Step 2: Use from Hub**

Now use Method A or B from Scenario 1!

---

## 🎯 **Scenario 3: Use HF Inference Endpoint (Fastest!)**

Deploy as API for ultra-fast inference:

### **Step 1: Upload Model**

Use Scenario 2, Step 1 to upload your model

### **Step 2: Deploy Inference Endpoint**

1. Go to https://huggingface.co/YOUR-USERNAME/jarvis-mistral-7b-lora
2. Click **"Deploy"** → **"Inference Endpoints"**
3. Configure:
   - Name: `jarvis-api`
   - Region: `us-east-1` (or closest to you)
   - Hardware: 
     - **CPU**: $0.60/hour (slowest, 5-10s per response)
     - **T4 GPU**: $1.00/hour (good, 2-3s per response)
     - **A10G GPU**: $3.00/hour (fast, 1-2s per response)
   - Instance: 1 replica
4. Click **"Create Endpoint"**
5. Wait 2-5 minutes for deployment
6. Copy endpoint URL

### **Step 3: Connect to Your System**

```bash
# Set environment variable
export CLOUD_LLM_URL="https://YOUR-ENDPOINT.aws.endpoints.huggingface.cloud"

# Start Training GUI (will use HF Endpoint)
python3 training_gui.py

# Or use in code:
import os
os.environ['CLOUD_LLM_URL'] = "your-endpoint-url"
```

The system already has `cloud_llm_client.py` that handles this!

---

## 🔧 **Complete Integration Script**

I'll create a script that handles ALL scenarios:

```python
#!/usr/bin/env python3
"""
Universal HF Model Connector
Supports: HF Hub, LoRA, Inference Endpoints
"""

import os
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
import torch

class HFModelConnector:
    def __init__(self, model_id: str, model_type: str = "auto"):
        """
        Connect to HF model
        
        Args:
            model_id: HF model ID (username/model-name)
            model_type: "full", "lora", or "auto" (auto-detect)
        """
        self.model_id = model_id
        self.model_type = model_type
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
    def load(self, quantization="4bit"):
        """Load model from HF Hub"""
        
        # Configure quantization
        bnb_config = None
        if quantization == "4bit":
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        
        # Auto-detect model type
        if self.model_type == "auto":
            # Check if model has LoRA adapter
            try:
                from peft import AutoPeftModelForCausalLM
                print("🔍 Checking if model is LoRA adapter...")
                self.model = AutoPeftModelForCausalLM.from_pretrained(
                    self.model_id,
                    quantization_config=bnb_config,
                    device_map="auto"
                )
                print("✅ Loaded as LoRA adapter!")
            except:
                print("🔍 Loading as full model...")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    quantization_config=bnb_config,
                    device_map="auto"
                )
                print("✅ Loaded as full model!")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        
        # Create pipeline
        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map="auto",
            return_full_text=False
        )
        
        print("✅ Model ready!")
        return True
    
    def generate(self, prompt, max_new_tokens=256, temperature=0.7):
        """Generate response"""
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        output = self.pipeline(
            formatted_prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True
        )
        return output[0]['generated_text'].strip()


# Usage:
if __name__ == "__main__":
    # Connect to your HF model
    connector = HFModelConnector(
        model_id="YOUR-USERNAME/jarvis-mistral-7b-lora"  # ← Change this!
    )
    
    # Load model
    connector.load(quantization="4bit")
    
    # Test
    response = connector.generate("What is Python?")
    print(f"\nResponse: {response}")
```

---

## 📋 **Step-by-Step: Connect HF Model to Training System**

### **Option A: Model Already on HF Hub**

```bash
# 1. Create config file
cat > hf_model_config.py << 'EOF'
HF_MODEL_ID = "your-username/jarvis-mistral-7b-lora"  # ← Your HF model
USE_LORA = True  # True if LoRA adapter, False if full model
QUANTIZATION = "4bit"  # "4bit", "8bit", or "none"
EOF

# 2. Update training_gui.py to use HF model
# (I'll create an updated version below)

# 3. Start GUI
python3 training_gui.py

# 4. Run automation
python3 cursor_training_integration.py --queries 20
```

### **Option B: Upload Local Model First**

```bash
# 1. Install HF CLI
pip install huggingface-hub

# 2. Login
huggingface-cli login

# 3. Create model repo on HF
# Go to: https://huggingface.co/new
# Create new model: jarvis-mistral-7b-lora

# 4. Upload your adapter
huggingface-cli upload your-username/jarvis-mistral-7b-lora \
  "jarvis-llm-brain-final fine tune 7B model" \
  --repo-type model

# 5. Now use Option A above!
```

### **Option C: Use HF Inference Endpoint (Production)**

```bash
# 1. Upload model (Option B)
# 2. Deploy endpoint (see Scenario 3 above)
# 3. Set URL
export CLOUD_LLM_URL="your-endpoint-url"
python3 training_gui.py
```

---

## 🚀 **Easiest Way: I'll Create a Universal Connector**

Let me create a script that handles everything:

```bash
# Just run this with your HF model ID:
python3 scripts/connect_hf_model.py --model your-username/jarvis-mistral-7b-lora

# It will:
# 1. Auto-detect model type (full or LoRA)
# 2. Configure quantization
# 3. Update training GUI
# 4. Test connection
# 5. Ready to use!
```

---

## 📊 **Comparison of Methods**

| Method | Speed | Cost | Setup | Best For |
|--------|-------|------|-------|----------|
| **Local** | 2-4s | Free | 10-30 min first | Privacy, testing |
| **HF Hub** | 2-4s | Free | 5 min | Sharing, version control |
| **Endpoint** | 1-2s | $1-3/hr | 10 min | Production, scaling |

---

## 🎯 **What I Recommend for You**

### **Phase 1: Upload to HF Hub** (Best choice!)

**Why:**
- ✅ Easy sharing
- ✅ Version control
- ✅ Can use locally OR as endpoint
- ✅ Free tier available

**How:**

```bash
# 1. Login to HF
huggingface-cli login

# 2. Upload your adapter (takes 1 minute for 26MB)
python3 << 'EOF'
from huggingface_hub import HfApi

api = HfApi()

# Upload your LoRA adapter
repo_id = "YOUR-USERNAME/jarvis-mistral-7b-lora"  # ← CHANGE THIS!

api.upload_folder(
    folder_path="jarvis-llm-brain-final fine tune 7B model",
    repo_id=repo_id,
    repo_type="model"
)

print(f"✅ Uploaded to: https://huggingface.co/{repo_id}")
EOF

# 3. Use in training system
export HF_MODEL_ID="YOUR-USERNAME/jarvis-mistral-7b-lora"
python3 training_gui.py
```

### **Phase 2: Local Testing**

```bash
# Download and use locally (auto-caches)
python3 core/lora_model_loader.py
python3 training_gui.py
```

### **Phase 3: Deploy Endpoint** (For production)

```bash
# Deploy as API for ultra-fast inference
# See instructions in Scenario 3 above
```

---

## 🔌 **Quick Connection Methods**

### **Method 1: Environment Variable** (Easiest!)

```bash
# Set your HF model ID
export HF_MODEL_ID="your-username/jarvis-mistral-7b-lora"

# Start training GUI (will auto-detect and use it)
python3 training_gui.py
```

### **Method 2: Config File**

```bash
# Create config
echo 'HF_MODEL_ID=your-username/jarvis-mistral-7b-lora' >> .env

# Load in code
python3 training_gui.py
```

### **Method 3: Direct Code Edit**

Edit `core/lora_model_loader.py` line 58:

```python
def _get_default_adapter_path(self) -> str:
    """Get default adapter path"""
    # Option 1: Use from HF Hub
    return "your-username/jarvis-mistral-7b-lora"  # ← Your HF model
    
    # Option 2: Use local
    # return "/Users/asithalakmal/Documents/web/JarvisX v2/jarvis-llm-brain-final fine tune 7B model"
```

---

## 🛠️ **I'll Create the Connection Script Now**

Let me build you a one-command connector:

```bash
python3 scripts/connect_hf_model.py \
  --model your-username/jarvis-mistral-7b-lora \
  --type lora \
  --quantization 4bit

# Auto-configures everything and tests connection!
```

---

## 📝 **Full Example: Upload & Connect**

```bash
# ============================================
# COMPLETE WORKFLOW: Upload & Connect HF Model
# ============================================

# STEP 1: Login to Hugging Face
pip install huggingface-hub
huggingface-cli login
# Enter token from: https://huggingface.co/settings/tokens

# STEP 2: Upload Your Model
python3 << 'EOF'
from huggingface_hub import HfApi

api = HfApi()

# Upload adapter (26MB, takes ~1 minute)
api.upload_folder(
    folder_path="jarvis-llm-brain-final fine tune 7B model",
    repo_id="AsithaLKonara/jarvis-mistral-7b-lora",  # ← Your username!
    repo_type="model",
    commit_message="Upload Jarvis LoRA adapter"
)

print("✅ Uploaded!")
print("View at: https://huggingface.co/AsithaLKonara/jarvis-mistral-7b-lora")
EOF

# STEP 3: Set Model ID
export HF_MODEL_ID="AsithaLKonara/jarvis-mistral-7b-lora"

# STEP 4: Test Connection
python3 core/lora_model_loader.py

# STEP 5: Start Training GUI
python3 training_gui.py

# STEP 6: Run Automation
python3 cursor_training_integration.py --queries 20

# DONE! ✅
```

---

## 🚀 **Fastest Method: HF Inference API** (No Download!)

If you want to skip local setup entirely:

```bash
# 1. Upload to HF Hub (see above)

# 2. Get HF API token
# Go to: https://huggingface.co/settings/tokens

# 3. Use Inference API (FREE for public models!)
export HF_API_TOKEN="your-token"
export HF_MODEL_ID="your-username/jarvis-mistral-7b-lora"

# 4. Update training_gui.py to use Inference API:
```

```python
from huggingface_hub import InferenceClient

client = InferenceClient(
    model="your-username/jarvis-mistral-7b-lora",
    token=os.getenv("HF_API_TOKEN")
)

def get_response(query):
    response = client.text_generation(
        query,
        max_new_tokens=256,
        temperature=0.7
    )
    return response
```

**Benefits:**
- ⚡ No download (instant start!)
- 💾 No disk space needed
- 🔥 Runs on HF servers (fast!)
- 🆓 FREE for public models!

---

## ⚡ **My Recommendation for YOU:**

Given your situation, here's the best path:

### **Today (5 minutes):**

```bash
# 1. Install HF tools
pip install huggingface-hub

# 2. Login
huggingface-cli login

# 3. Upload your adapter (1 minute for 26MB)
huggingface-cli upload AsithaLKonara/jarvis-mistral-7b-lora \
  "jarvis-llm-brain-final fine tune 7B model" \
  --repo-type model
```

**Result**: Model on HF Hub, accessible anywhere! ✅

### **Tomorrow (10 minutes):**

```bash
# Use Inference API (no download!)
export HF_MODEL_ID="AsithaLKonara/jarvis-mistral-7b-lora"
export HF_API_TOKEN="your-token"

python3 training_gui.py
```

**Result**: Training system working with YOUR model! ✅

---

## 🎯 **What I'll Build Next**

Let me create a universal connector script that:
1. Detects if model is on HF Hub or local
2. Auto-configures the training system
3. Tests connection
4. Ready to use in 1 command!

Should I create this now?

---

## 📚 **Documentation**

- This guide: `CONNECT_HF_MODEL_COMPLETE.md`
- LoRA loader: `core/lora_model_loader.py`
- Cloud client: `cloud_llm_client.py`
- Setup guide: `SETUP_YOUR_MODEL.md`

---

## ✅ **Summary**

**Your Model**: LoRA Adapter (26MB)  
**Where It Can Be**: Local, HF Hub, or HF Endpoint  
**Best Option**: Upload to HF Hub (takes 1 minute!)  
**Then**: Use with Inference API (no local setup needed!)  

**Ready to upload?** Just need your HF username! 🤗✨

