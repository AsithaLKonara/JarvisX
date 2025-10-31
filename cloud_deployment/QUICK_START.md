# ⚡ Quick Start - Cloud LLM Deployment

Get your Jarvis LLM running on free cloud GPU in 10 minutes.

---

## 🎯 What You'll Get

- **Fast responses:** 2-5 seconds (vs 35+ minutes local)
- **Free tier:** No cost for basic usage
- **24/7 availability:** Always online
- **Your trained model:** Uses your LoRA adapter

---

## 📋 Steps (10 minutes)

### 1️⃣ Create Hugging Face Account (2 min)
- Go to: https://huggingface.co/join
- Sign up (free)

### 2️⃣ Create Access Token (1 min)
- Visit: https://huggingface.co/settings/tokens
- Click "New token"
- Name: `jarvis-deployment`
- Type: **Write**
- Click "Generate"
- **Copy the token** (you'll need it soon)

### 3️⃣ Create New Space (2 min)
- Go to: https://huggingface.co/spaces
- Click **"Create new Space"**
- Fill in:
  - Name: `jarvis-llm-brain`
  - License: MIT
  - SDK: **Gradio**
  - Hardware: CPU basic (free)
  - Visibility: Private
- Click **"Create Space"**

### 4️⃣ Deploy (5 min)

Open Terminal and run:

```bash
cd "/Users/asithalakmal/Documents/web/JarvisX v2/cloud_deployment"

# Replace YOUR-USERNAME with your HF username
./deploy_to_hf.sh YOUR-USERNAME
```

**When prompted for password:** Paste your Access Token (not your password!)

### 5️⃣ Wait for Build (5-10 min)

- Go to: `https://huggingface.co/spaces/YOUR-USERNAME/jarvis-llm-brain`
- Watch the "Building" indicator turn to "Running"
- First build takes 5-10 minutes

### 6️⃣ Configure Jarvis

Once "Running", set your Space URL:

```bash
cd "/Users/asithalakmal/Documents/web/JarvisX v2"

# Replace YOUR-USERNAME
export CLOUD_LLM_URL="https://YOUR-USERNAME-jarvis-llm-brain.hf.space"
export DISABLE_HELAGPT=true

# Test it!
python3 main.py
```

---

## ✅ Success!

You should now get **2-5 second responses** instead of 35+ minutes!

---

## 🔧 Troubleshooting

**"git clone" fails:**
- Make sure you've created the Space first at https://huggingface.co/spaces

**"Permission denied" when pushing:**
- Use your **Access Token** as password, not your HF password

**Build fails:**
- Check Space logs for errors
- May need to upgrade hardware to T4 GPU ($0.60/hour)

**Slow responses:**
- Free CPU tier can be slow
- Upgrade to T4 small GPU in Space settings for faster inference

---

## 📞 Need Help?

Check the full guide: `DEPLOYMENT_GUIDE.md`

