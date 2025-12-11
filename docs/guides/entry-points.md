# 🚪 JarvisX V2 - Entry Points Guide

## Overview

JarvisX V2 has multiple entry points for different use cases. This guide explains when to use each one.

---

## Entry Points

### 1. **Modern CLI (`cli/main.py`)** ⭐ **RECOMMENDED**

**Location:** `cli/main.py`  
**Command:** `jarvisx-cli` or `python -m cli.main`

**When to Use:**
- ✅ **Primary interface** for all operations
- ✅ Training management
- ✅ Cloud deployment
- ✅ System monitoring
- ✅ Business operations
- ✅ Workflow orchestration
- ✅ Model management

**Features:**
- Modern Typer-based CLI
- 31+ commands organized by category
- JSON output support
- Command history
- Analytics tracking
- Help system

**Example:**
```bash
# Install first (if not already installed)
pip install -e .

# Then use
jarvisx-cli status
jarvisx-cli training list
jarvisx-cli cloud connect --url https://...
```

**Installation:**
```bash
# From project root
pip install -e .
# This installs the jarvisx-cli command
```

---

### 2. **Simple CLI Interface (`cli_interface.py`)**

**Location:** `cli_interface.py`  
**Command:** `python cli_interface.py` or `python main.py`

**When to Use:**
- ✅ Simple interactive chat
- ✅ Quick testing
- ✅ TTS-enabled conversations
- ✅ Basic command execution

**Features:**
- Text-based interface
- TTS (Text-to-Speech) support
- Command parsing
- Hybrid brain system
- Simple and lightweight

**Example:**
```bash
python cli_interface.py
# Then type commands interactively
```

**Note:** This is the older interface. For new development, use `cli/main.py`.

---

### 3. **Main Entry Point (`main.py`)**

**Location:** `main.py`  
**Command:** `python main.py`

**What it does:**
- Wrapper that calls `cli_interface.py`
- Provides simple entry point
- Handles errors gracefully

**When to Use:**
- ✅ Quick start
- ✅ Simple testing
- ✅ Backward compatibility

**Example:**
```bash
python main.py
```

---

## Which Entry Point Should I Use?

### For Development & Operations
👉 **Use `jarvisx-cli` (Modern CLI)**
- Full feature set
- Better organization
- Production-ready

### For Simple Chat/Testing
👉 **Use `python cli_interface.py`**
- Quick and simple
- Interactive mode
- TTS support

### For Quick Start
👉 **Use `python main.py`**
- Simplest option
- Good for first-time users

---

## Installation & Setup

### Option 1: Install as Package (Recommended)

```bash
# From project root
pip install -e .

# Then use
jarvisx-cli --help
jarvisx-cli status
```

### Option 2: Direct Python Execution

```bash
# Modern CLI
python -m cli.main --help
python -m cli.main status

# Simple CLI
python cli_interface.py
python main.py
```

---

## Command Comparison

| Feature | Modern CLI | Simple CLI |
|---------|-----------|-------------|
| Commands | 31+ organized | Basic commands |
| Training | ✅ Full support | ❌ Limited |
| Cloud Ops | ✅ Full support | ❌ Limited |
| System Monitor | ✅ Full support | ✅ Basic |
| Business Mode | ✅ Full support | ✅ Basic |
| TTS Support | ✅ Via voice commands | ✅ Built-in |
| JSON Output | ✅ Yes | ❌ No |
| Command History | ✅ Yes | ❌ No |
| Analytics | ✅ Yes | ❌ No |

---

## Migration Guide

### From Simple CLI to Modern CLI

**Old way:**
```bash
python cli_interface.py
# Then type commands
```

**New way:**
```bash
jarvisx-cli status
jarvisx-cli training list
jarvisx-cli cloud connect --url https://...
```

**Benefits:**
- Better organization
- More features
- Better error handling
- JSON output support

---

## Troubleshooting

### "Command not found: jarvisx-cli"

**Solution:**
```bash
# Install the package
pip install -e .

# Or use directly
python -m cli.main --help
```

### "Module not found: cli"

**Solution:**
```bash
# Make sure you're in the project root
cd /path/to/JarvisX\ v2

# Then run
python -m cli.main --help
```

### Import Errors

**Solution:**
```bash
# Install dependencies
pip install -r requirements.txt

# Make sure you're using Python 3.11+
python --version
```

---

## Quick Reference

```bash
# Modern CLI (Recommended)
jarvisx-cli --help
jarvisx-cli status
jarvisx-cli training list
jarvisx-cli cloud connect --url https://...

# Simple CLI (Legacy)
python cli_interface.py
python main.py

# Direct module execution
python -m cli.main --help
```

---

## Next Steps

1. **Install the package:** `pip install -e .`
2. **Try the modern CLI:** `jarvisx-cli --help`
3. **Explore commands:** `jarvisx-cli training --help`
4. **Read the docs:** See `docs/USER_GUIDE.md`

---

**Last Updated:** 2025-01-XX  
**Version:** 2.0.0

