# 🎓 Training GUI - Quick Start Guide

## Overview

The **Training GUI** is a simple web-based interface for:
- Interacting with your optimized Mistral 7B model
- Rating responses (1-5 stars)
- Building high-quality training datasets
- Exporting datasets for retraining

**Perfect for collecting user feedback and continuous model improvement!**

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install Flask Flask-CORS
# Or install all:
pip install -r requirements.txt
```

### 2. Start the Training GUI

```bash
python3 training_gui.py
```

The interface will start at: **http://localhost:5001**

### 3. Open in Browser

```bash
open http://localhost:5001
# Or manually open in your browser
```

---

## 🎯 Features

### **Left Side: Chat Interface**

1. **Send Queries**
   - Type your message
   - Select task type (Technical, Engineering, Design, Business, General)
   - Click "Send" or press Enter

2. **Rate Responses**
   - Click stars (1-5) below each response
   - 4-5 stars = Training examples
   - Feedback is automatically saved

3. **View Statistics**
   - Total conversations
   - Rated responses
   - Average rating
   - Training-ready examples (4-5 stars)

### **Right Side: Training Log**

- **Real-time logging** of all interactions
- **Color-coded entries**:
  - 🟢 Green border = Rated
  - 🟠 Orange border = Not rated yet
- **Quick actions**:
  - **Export**: Download training dataset (JSON)
  - **Refresh**: Update statistics
  - **Clear**: Clear all history

---

## 📊 How It Works

### Workflow

```
1. User sends query
   ↓
2. Model generates response
   ↓
3. User rates response (1-5 stars)
   ↓
4. Feedback is logged automatically
   ↓
5. Export dataset when ready (100+ examples recommended)
   ↓
6. Use exported data to retrain model
```

### Data Format

Exported dataset is in **Alpaca format**:

```json
[
  {
    "instruction": "What is machine learning?",
    "input": "",
    "output": "Machine learning is a subset of AI...",
    "metadata": {
      "rating": 5,
      "task_type": "technical",
      "timestamp": "2025-11-06T10:30:00"
    }
  }
]
```

---

## 🔧 API Endpoints

The training GUI exposes these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main interface |
| `/api/chat` | POST | Send message, get response |
| `/api/rate` | POST | Rate a response |
| `/api/history` | GET | Get conversation history |
| `/api/stats` | GET | Get statistics |
| `/api/export` | GET | Export training dataset |
| `/api/clear` | POST | Clear history |

### Example: Send Chat Request

```python
import requests

response = requests.post('http://localhost:5001/api/chat', json={
    'message': 'What is Python?',
    'task_type': 'technical'
})

data = response.json()
print(f"Response: {data['response']}")
print(f"Inference time: {data['inference_time']}s")
```

### Example: Rate Response

```python
requests.post('http://localhost:5001/api/rate', json={
    'conversation_id': 0,
    'rating': 5,
    'feedback': 'Great explanation!'
})
```

---

## 📈 Best Practices

### 1. Collecting Quality Data

- **Diverse queries**: Ask different types of questions
- **Honest ratings**: Rate responses objectively
- **Multiple domains**: Technical, business, design, etc.
- **Edge cases**: Include tricky or uncommon questions

### 2. Rating Guidelines

| Stars | Meaning | Use For |
|-------|---------|---------|
| ⭐ 1 | Completely wrong | Bad responses, don't use for training |
| ⭐⭐ 2 | Mostly wrong | Poor quality |
| ⭐⭐⭐ 3 | Partially correct | Neutral, won't be used for training |
| ⭐⭐⭐⭐ 4 | Good quality | **Will be used for training** ✅ |
| ⭐⭐⭐⭐⭐ 5 | Excellent | **Will be used for training** ✅ |

**Only 4-5 star responses are exported for training!**

### 3. Dataset Size Recommendations

- **Minimum**: 100 examples (4-5 stars)
- **Good**: 500-1000 examples
- **Excellent**: 2000+ examples
- **Balanced**: Mix of all task types

---

## 🔄 Integration with Self-Training

The Training GUI automatically integrates with the self-training system:

```python
# Feedback is automatically recorded in:
data/feedback/feedback.jsonl

# Can be used with:
python3 scripts/auto_train_from_feedback.py
```

---

## 🎨 Customization

### Change Port

Edit `training_gui.py`:

```python
app.run(host='0.0.0.0', port=5001, debug=False)
# Change to your preferred port
```

### Add Custom Task Types

Edit `training.html`:

```html
<select class="task-type-select" id="task-type">
    <option value="general">General</option>
    <option value="custom">Your Custom Type</option>
</select>
```

### Modify Model Parameters

Edit `training_gui.py`:

```python
response = brain.get_response(
    user_input=user_input,
    max_length=256,  # Adjust max response length
    temperature=0.7,  # Adjust creativity (0.0-1.0)
    task_type=task_type
)
```

---

## 🧪 Testing Workflow

### Day 1-7: Data Collection
```
Goal: Collect 100+ rated examples
- Use GUI for all queries
- Rate every response honestly
- Mix of task types
```

### Week 2: Export & Review
```
1. Click "Export" button
2. Review exported JSON
3. Check data quality
4. Remove any bad examples if needed
```

### Week 3: Retrain Model
```
1. Use exported dataset
2. Run: python3 scripts/auto_train_from_feedback.py
3. Or use Google Colab for faster training
```

### Week 4+: Deploy & Monitor
```
1. Deploy updated model
2. Continue collecting feedback
3. Retrain monthly for continuous improvement
```

---

## 📊 Statistics Dashboard

The stats bar shows real-time metrics:

- **Total Conversations**: All queries sent
- **Rated Responses**: Responses with star ratings
- **Average Rating**: Mean of all ratings
- **Training Examples**: 4-5 star responses (ready for training)

---

## 🐛 Troubleshooting

### Issue: "Model not loaded"
**Solution**: 
1. Ensure model is in correct path
2. Check `OPTIMIZED_LLM_GUIDE.md` for setup
3. Verify dependencies are installed

### Issue: Slow responses
**Solution**:
1. First response is slower (torch.compile warmup)
2. Subsequent responses should be 2-3s
3. Close other applications to free memory

### Issue: Export button not working
**Solution**:
1. Rate at least one response
2. Check browser console for errors
3. Ensure Flask server is running

### Issue: Port already in use
**Solution**:
```bash
# Find process using port 5001
lsof -i :5001

# Kill process
kill -9 <PID>

# Or change port in training_gui.py
```

---

## 💡 Tips

1. **Keep it running**: Leave GUI open during work to collect organic queries
2. **Batch rating**: Rate multiple responses at once
3. **Regular exports**: Export data weekly to avoid losing progress
4. **Backup datasets**: Save exported JSON files in safe location
5. **Diverse queries**: Ask questions you'd actually ask Jarvis

---

## 🔗 Integration Examples

### With Hybrid Brain

```python
# In core/hybrid_brain.py
from training_gui import initialize_brain

# Use GUI's brain instance
gui_brain = initialize_brain()
```

### With Existing CLI

```python
# Start GUI alongside CLI
import subprocess

# Start GUI in background
subprocess.Popen(['python3', 'training_gui.py'])

# Continue with CLI
```

### Automated Collection

```python
# Script to automatically send test queries
import requests

queries = [
    "What is Python?",
    "Explain machine learning",
    "How to optimize SQL?"
]

for query in queries:
    response = requests.post('http://localhost:5001/api/chat', json={
        'message': query,
        'task_type': 'technical'
    })
    
    # Rate automatically (for testing)
    data = response.json()
    requests.post('http://localhost:5001/api/rate', json={
        'conversation_id': data['conversation_id'],
        'rating': 4
    })
```

---

## 📚 Files

- `training_gui.py` - Flask backend server
- `training_gui_templates/training.html` - Web interface
- `logs/training_gui.log` - Server logs
- `data/feedback/feedback.jsonl` - Collected feedback

---

## 🎯 Next Steps

1. **Start GUI**: `python3 training_gui.py`
2. **Collect Data**: Use for 1-2 weeks
3. **Export Dataset**: Click "Export" button
4. **Retrain Model**: Use exported data
5. **Deploy**: Replace old model with new one
6. **Repeat**: Continuous improvement!

---

## 🌟 Benefits

✅ **Easy to use** - Simple web interface  
✅ **Real-time feedback** - See results immediately  
✅ **Automatic logging** - All interactions saved  
✅ **Export ready** - One-click dataset export  
✅ **Integrated** - Works with self-training system  
✅ **Beautiful UI** - Modern, gradient design  
✅ **Production ready** - Stable Flask backend  

---

**Created**: November 6, 2025  
**Version**: 1.0  
**Status**: ✅ Ready to Use

**Start collecting training data now!** 🚀

