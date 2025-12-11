# 🔧 Troubleshooting Guide

Common issues and solutions for JarvisX V2.

## 📋 Table of Contents

1. [Installation Issues](#installation-issues)
2. [CLI Issues](#cli-issues)
3. [Model Loading Issues](#model-loading-issues)
4. [Cloud Connection Issues](#cloud-connection-issues)
5. [Dependency Issues](#dependency-issues)
6. [Performance Issues](#performance-issues)

---

## Installation Issues

### "Command not found: jarvisx-cli"

**Problem:** The CLI command is not available after installation.

**Solutions:**
```bash
# Install the package
pip install -e .

# Or use directly
python -m cli.main --help
```

### "Module not found: cli"

**Problem:** Python can't find the CLI module.

**Solutions:**
```bash
# Make sure you're in the project root
cd /path/to/JarvisX\ v2

# Check Python path
python -c "import sys; print(sys.path)"

# Run from project root
python -m cli.main --help
```

---

## CLI Issues

### Import Errors

**Problem:** Import errors when running CLI commands.

**Solutions:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Check Python version (requires 3.11+)
python --version

# Verify installation
pip list | grep jarvisx
```

### "psutil not available"

**Problem:** System monitoring commands fail.

**Solution:**
```bash
pip install psutil
```

### "certifi not available"

**Problem:** Cloud/HTTP requests fail.

**Solution:**
```bash
pip install certifi
# Or
pip install requests  # certifi is a dependency
```

---

## Model Loading Issues

### "Model path not found"

**Problem:** Model files not found.

**Solutions:**
```bash
# Set environment variable
export JARVIS_MODEL_PATH=/path/to/model

# Or use default location
# models/jarvis-llm-brain-final
```

### Hardcoded Path Errors

**Problem:** Errors about hardcoded paths.

**Solution:**
- This has been fixed in the latest version
- Use `JARVIS_MODEL_PATH` environment variable
- Or use relative paths from project root

---

## Cloud Connection Issues

### "Failed to connect to cloud space"

**Problem:** Can't connect to Hugging Face Space.

**Solutions:**
```bash
# Check URL format
export CLOUD_LLM_URL=https://your-space.hf.space

# Test connection
python -m cli.main cloud test --prompt "Hello"

# Check network
curl https://your-space.hf.space
```

### "Authentication failed"

**Problem:** Authentication errors with Hugging Face.

**Solutions:**
```bash
# Set token
export HF_TOKEN=your_token_here

# Or use --token flag
python -m cli.main cloud deploy --token your_token
```

---

## Dependency Issues

### Missing Dependencies

**Problem:** Various "module not found" errors.

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# For specific issues:
pip install psutil  # System monitoring
pip install certifi  # SSL certificates
pip install huggingface_hub  # Cloud operations
```

### Version Conflicts

**Problem:** Dependency version conflicts.

**Solutions:**
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Check versions
pip list
```

---

## Performance Issues

### Slow Response Times

**Problem:** CLI commands are slow.

**Solutions:**
- Use cloud LLM for faster responses
- Enable GPU acceleration if available
- Check system resources: `jarvisx-cli system status`

### High Memory Usage

**Problem:** High memory consumption.

**Solutions:**
- Use cloud LLM instead of local
- Reduce model size
- Close other applications
- Check memory: `jarvisx-cli system status`

---

## Getting Help

### Check Logs
```bash
# View logs
jarvisx-cli system logs

# Check specific log file
tail -f logs/jarvis.log
```

### Debug Mode
```bash
# Enable verbose output
jarvisx-cli --verbose status

# Check configuration
jarvisx-cli config show
```

### Common Commands
```bash
# Check system status
jarvisx-cli status

# Check system health
jarvisx-cli system health

# View configuration
jarvisx-cli config show
```

---

## Still Having Issues?

1. **Check Documentation:**
   - [User Guide](USER_GUIDE.md)
   - [Entry Points Guide](../ENTRY_POINTS_GUIDE.md)
   - [Deployment Guide](DEPLOYMENT_GUIDE.md)

2. **Check Issues:**
   - GitHub Issues: https://github.com/AsithaLKonara/JarvisX/issues

3. **Get Support:**
   - Create a new issue with:
     - Error message
     - Steps to reproduce
     - System information
     - Logs (if available)

---

**Last Updated:** 2025-01-XX

