# 🚀 Hugging Face Space Deployment Guide

Deploy your Jarvis LLM Brain to free cloud GPU for fast inference (2-5 second responses).

---

## Prerequisites

- Hugging Face account (free): https://huggingface.co/join
- Git installed on your Mac

---

## Step 1: Create Hugging Face Space (5 min)

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in:
   - **Space name:** `jarvis-llm-brain` (or any name you like)
   - **License:** MIT
   - **SDK:** Gradio
   - **Hardware:** CPU basic (FREE) - will upgrade if needed
   - **Visibility:** Private (recommended) or Public
4. Click **"Create Space"**

---

## Step 2: Clone Your New Space (2 min)

```bash
cd ~/Desktop
git clone https://huggingface.co/spaces/YOUR-USERNAME/jarvis-llm-brain
cd jarvis-llm-brain
```

Replace `YOUR-USERNAME` with your HF username.

---

## Step 3: Copy Files to Space (2 min)

```bash
# Copy Space files
cp "/Users/asithalakmal/Documents/web/JarvisX v2/cloud_deployment/hf_space/app.py" .
cp "/Users/asithalakmal/Documents/web/JarvisX v2/cloud_deployment/hf_space/requirements.txt" .
cp "/Users/asithalakmal/Documents/web/JarvisX v2/cloud_deployment/hf_space/README.md" .

# Copy your trained LoRA adapter
mkdir -p jarvis-llm-adapter
cp -r "/Users/asithalakmal/Documents/web/JarvisX v2/models/jarvis-llm-brain-final/"* jarvis-llm-adapter/
```

---

## Step 4: Push to Hugging Face (3 min)

```bash
git add .
git commit -m "Initial deployment of Jarvis LLM Brain"
git push
```

**Note:** You'll be asked for credentials:
- Username: Your HF username
- Password: Your HF **Access Token** (not your password!)
  - Get token at: https://huggingface.co/settings/tokens
  - Click "New token" → "Write" access → Copy

---

## Step 5: Wait for Build (5-10 min)

1. Go to your Space page: `https://huggingface.co/spaces/YOUR-USERNAME/jarvis-llm-brain`
2. Watch the "Building" status in the top right
3. Wait for it to turn green "Running"

**First build takes 5-10 minutes** (downloading Mistral-7B base model).

---

## Step 6: Get Your API URL

Once "Running", your Space URL is:
```
https://YOUR-USERNAME-jarvis-llm-brain.hf.space
```

Example: `https://asithalakmal-jarvis-llm-brain.hf.space`

---

## Step 7: Test Your Deployment

### Test 1: Web Interface
Visit your Space URL and type a message in the chat.

### Test 2: API Call
```bash
curl -X POST "https://YOUR-SPACE-URL/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain REST API briefly", "max_new_tokens": 100, "temperature": 0.7}'
```

---

## Step 8: Configure Jarvis to Use Cloud LLM

```bash
cd "/Users/asithalakmal/Documents/web/JarvisX v2"

# Set your Space URL
export CLOUD_LLM_URL="https://YOUR-USERNAME-jarvis-llm-brain.hf.space"
export DISABLE_HELAGPT=true

# Test it
python3 main.py
```

---

## 🎯 Expected Results

- **Response time:** 2-5 seconds (vs 35+ minutes locally!)
- **Quality:** Uses your trained LoRA adapter
- **Cost:** FREE (on HF free GPU tier)
- **Availability:** 24/7

---

## 🆙 Optional: Upgrade to Better GPU

If the free CPU tier is slow:

1. Go to your Space Settings
2. Click "Change hardware"
3. Select **"CPU Upgrade"** (still free) or **"T4 small"** ($0.60/hour, but much faster)
4. Free tier should be fine for testing; upgrade if you need production speed

---

## ⚡ Quick Commands

```bash
# Update your deployment
cd ~/Desktop/jarvis-llm-brain
# Make changes to app.py
git add .
git commit -m "Update model"
git push

# Configure Jarvis
export CLOUD_LLM_URL="https://YOUR-USERNAME-jarvis-llm-brain.hf.space"
export DISABLE_HELAGPT=true
python3 main.py
```

---

## 🔧 Troubleshooting

**Build fails with "out of memory":**
- The free tier might struggle. Upgrade to T4 small GPU ($0.60/hour).

**"Model not found" error:**
- Check that `jarvis-llm-adapter/` folder has all files from `models/jarvis-llm-brain-final/`

**Slow responses (>10 seconds):**
- Upgrade hardware to T4 small GPU in Space settings

**Can't push to git:**
- Make sure you're using your HF Access Token, not your password
- Get token at: https://huggingface.co/settings/tokens

---

## 📚 Files Structure

Your Space should look like:
```
jarvis-llm-brain/
├── app.py                          # Gradio server
├── requirements.txt                # Python dependencies
├── README.md                       # Space description
└── jarvis-llm-adapter/            # Your trained LoRA
    ├── adapter_config.json
    ├── adapter_model.safetensors
    ├── tokenizer.json
    └── ...
```

---

## ✅ Success Checklist

- [ ] Created HF Space
- [ ] Cloned Space locally
- [ ] Copied all files (app.py, requirements.txt, README.md, adapter)
- [ ] Pushed to HF
- [ ] Build completed successfully (Status: "Running")
- [ ] Tested web interface
- [ ] Set `CLOUD_LLM_URL` in Jarvis
- [ ] Fast responses (2-5s) working!

---

**Need help?** Check your Space's "Logs" tab for error messages.

