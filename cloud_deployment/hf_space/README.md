---
title: Jarvis X V2 LLM Brain
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# 🧠 Jarvis X V2 - Expert LLM Brain

Cloud inference server for Jarvis X V2's custom-trained LLM brain.

## Model Details

- **Base Model:** mistralai/Mistral-7B-Instruct-v0.1
- **Fine-tuning:** LoRA adapter (rank 8, alpha 16) trained on **137,300 examples**
- **Training Time:** ~3.5 hours on NVIDIA A100
- **Training Loss:** 2.32 → 0.05-0.15 (90%+ reduction)
- **Quantization:** 4-bit (NF4) for efficient GPU inference
- **Specializations:** 
  - **7 Operational Modes:** Engineer, Designer, Editor, Business, System Monitor, Casual/Sinhala, Avatar
  - **169 Job Roles:** IT, Finance, Creative, Education, and 13 more industries
  - **Cross-Platform:** Android, iOS, Remote PC, Mobile automation
  - **Real PC Control:** System monitoring, process management, file operations
  - **Professional AI Patterns:** Communication, planning, security, debugging

## Usage

### Via API (for Jarvis X V2)

```python
import requests

response = requests.post(
    "https://YOUR-SPACE-URL/generate",
    json={
        "prompt": "Explain REST API design briefly",
        "max_new_tokens": 256,
        "temperature": 0.7
    }
)
print(response.json()["response"])
```

### Via Web Interface

Visit the Space URL and use the chat interface directly.

## Performance

- **Response time:** 2-5 seconds (on free GPU tier)
- **Quality:** Fine-tuned for technical accuracy
- **Availability:** 24/7 (subject to HF Space limits)

## Integration with Jarvis X V2

Set environment variable:
```bash
export CLOUD_LLM_URL="https://YOUR-SPACE-URL"
export DISABLE_HELAGPT=true
python3 main.py
```

