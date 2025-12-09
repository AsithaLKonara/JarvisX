# 🚀 JarvisX V2 - Deployment Guide

## Table of Contents

1. [Production Readiness Checklist](#production-readiness-checklist)
2. [Local Deployment](#local-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Security Considerations](#security-considerations)
7. [Performance Optimization](#performance-optimization)

---

## Production Readiness Checklist

### Pre-Deployment Checklist

- [ ] **Testing Complete**
  - [ ] All unit tests passing
  - [ ] Integration tests passing
  - [ ] End-to-end tests passing
  - [ ] Voice integration tested
  - [ ] CLI commands verified

- [ ] **Configuration**
  - [ ] Configuration files reviewed
  - [ ] API keys and secrets secured
  - [ ] Environment variables set
  - [ ] Logging configured

- [ ] **Dependencies**
  - [ ] All dependencies installed
  - [ ] Version compatibility verified
  - [ ] System requirements met

- [ ] **Documentation**
  - [ ] User guide reviewed
  - [ ] API documentation complete
  - [ ] Deployment procedures documented

- [ ] **Security**
  - [ ] Secrets management configured
  - [ ] Access controls reviewed
  - [ ] Security best practices followed

---

## Local Deployment

### 1. System Requirements

```bash
# Minimum requirements
- Python 3.11+
- 8GB RAM (16GB recommended)
- 10GB free disk space
- Internet connection (for cloud features)
```

### 2. Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/AsithaLKonara/JarvisX.git
cd JarvisX

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
jarvisx-cli version
jarvisx-cli status
```

### 3. Configuration

```bash
# Create configuration directory
mkdir -p ~/.jarvisx

# Set up configuration
jarvisx-cli config set --key api_key --value "your-api-key"
jarvisx-cli config set --key default_model --value "jarvis-llm-brain"

# Validate configuration
jarvisx-cli config validate
```

### 4. Test Deployment

```bash
# Run health check
jarvisx-cli system health --full

# Test voice integration
jarvisx-cli voice listen --timeout 5

# Test cloud connection (if applicable)
jarvisx-cli cloud connect --url <your-space-url>
```

---

## Cloud Deployment

### Hugging Face Spaces Deployment

#### 1. Prepare Model

```bash
# Train or load your model
jarvisx-cli training start --config training/config.json

# Wait for training to complete
jarvisx-cli training status --job-id <job-id>

# Evaluate model
jarvisx-cli training evaluate --job-id <job-id>
```

#### 2. Upload Model

```bash
# Upload to Hugging Face Hub
jarvisx-cli model upload \
  --model ./models/jarvis-llm-brain \
  --space jarvis-llm-brain \
  --description "JarvisX V2 AI Assistant"
```

#### 3. Deploy to Space

```bash
# Deploy to Hugging Face Space
jarvisx-cli cloud deploy \
  --space jarvis-llm-brain \
  --model ./models/jarvis-llm-brain \
  --api-key <your-hf-token>
```

#### 4. Monitor Deployment

```bash
# Check deployment status
jarvisx-cli cloud status --space jarvis-llm-brain

# Monitor metrics
jarvisx-cli cloud monitor --space jarvis-llm-brain --metrics latency,errors

# View logs
jarvisx-cli cloud logs --space jarvis-llm-brain --tail 100
```

### API Endpoint Deployment

#### 1. Set Up API Server

```python
# api_server.py
from flask import Flask, request, jsonify
from core.jarvis_llm_brain import JarvisLLMBrain

app = Flask(__name__)
brain = JarvisLLMBrain()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    response = brain.process(data['message'])
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### 2. Deploy with Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run server
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

#### 3. Test API

```bash
# Test API endpoint
jarvisx-cli cloud test --url http://localhost:5000/api/chat --prompt "Hello"
```

---

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV JARVISX_HOME=/app

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "-m", "cli.main", "status"]
```

### 2. Build Docker Image

```bash
# Build image
docker build -t jarvisx-v2:latest .

# Tag for registry
docker tag jarvisx-v2:latest your-registry/jarvisx-v2:latest
```

### 3. Run Container

```bash
# Run container
docker run -d \
  --name jarvisx \
  -p 5000:5000 \
  -v ~/.jarvisx:/app/data \
  -e API_KEY=your-api-key \
  jarvisx-v2:latest
```

### 4. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  jarvisx:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ~/.jarvisx:/app/data
      - ./models:/app/models
    environment:
      - API_KEY=${API_KEY}
      - MODEL_PATH=/app/models
    restart: unless-stopped
```

```bash
# Start with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## Monitoring & Maintenance

### 1. Health Monitoring

```bash
# Set up automated health checks
*/5 * * * * jarvisx-cli system health --json > /var/log/jarvisx-health.log

# Monitor system status
jarvisx-cli system status --json | jq '.System'
```

### 2. Log Management

```bash
# View logs
jarvisx-cli system logs --tail 100

# Clean old logs
jarvisx-cli system cleanup --logs --days 7
```

### 3. Performance Monitoring

```bash
# Check analytics
jarvisx-cli analytics summary

# Monitor performance
jarvisx-cli analytics performance

# Check errors
jarvisx-cli analytics errors
```

### 4. Regular Maintenance

```bash
# Weekly cleanup script
#!/bin/bash
jarvisx-cli system cleanup --logs --cache --temp
jarvisx-cli system optimize --auto
jarvisx-cli analytics summary
```

---

## Security Considerations

### 1. Secrets Management

```bash
# Use environment variables for secrets
export JARVISX_API_KEY="your-secret-key"
export HUGGINGFACE_TOKEN="your-hf-token"

# Or use config file with restricted permissions
chmod 600 ~/.jarvisx/config.json
```

### 2. Access Control

```bash
# Review command history
jarvisx-cli history list

# Check analytics for suspicious activity
jarvisx-cli analytics commands
```

### 3. Network Security

- Use HTTPS for API endpoints
- Implement rate limiting
- Use firewall rules
- Enable authentication for API access

### 4. Data Protection

```bash
# Encrypt sensitive data
# Use secure storage for models
# Regular backups
jarvisx-cli business export --type all --format json --output backup.json
```

---

## Performance Optimization

### 1. Model Optimization

```bash
# Use quantized models
jarvisx-cli model load --name <model> --quantize

# Optimize system
jarvisx-cli system optimize --auto
```

### 2. Caching

```bash
# Enable caching
jarvisx-cli config set --key enable_cache --value true
jarvisx-cli config set --key cache_ttl --value 3600
```

### 3. Resource Management

```bash
# Monitor resource usage
jarvisx-cli system status --json | jq '.System.Memory'
jarvisx-cli system status --json | jq '.System.CPU'

# Clean up when needed
jarvisx-cli system cleanup --cache --temp
```

### 4. Async Operations

```bash
# Use async for long-running operations
jarvisx-cli training start --config config.json --async
```

---

## Troubleshooting Deployment

### Common Issues

**1. Model Loading Fails**
```bash
# Check model path
jarvisx-cli model info --name <model-name>

# Verify model files
ls -lh models/<model-name>/
```

**2. API Connection Issues**
```bash
# Test connection
jarvisx-cli cloud test --url <api-url> --prompt "test"

# Check network
jarvisx-cli system status --json | jq '.System.Network'
```

**3. Performance Issues**
```bash
# Check system resources
jarvisx-cli system health --full

# Optimize system
jarvisx-cli system optimize --auto
```

### Getting Help

```bash
# Check logs
jarvisx-cli system logs --tail 100

# View analytics
jarvisx-cli analytics errors

# Get help
jarvisx-cli help command <command-name>
```

---

## Post-Deployment

### 1. Verification

```bash
# Verify deployment
jarvisx-cli status
jarvisx-cli system health --full
jarvisx-cli cloud status --space <your-space>
```

### 2. Documentation

- Document deployment procedure
- Note any custom configurations
- Record API endpoints and credentials
- Document monitoring setup

### 3. Monitoring Setup

- Set up health check alerts
- Configure log aggregation
- Set up performance monitoring
- Create backup procedures

---

## Best Practices

1. **Version Control**: Tag releases and document changes
2. **Backups**: Regular backups of models and data
3. **Monitoring**: Continuous monitoring of system health
4. **Documentation**: Keep deployment docs up to date
5. **Testing**: Test deployments in staging first
6. **Security**: Regular security audits and updates
7. **Performance**: Monitor and optimize regularly

---

**Deployment Complete! 🎉**

For issues or questions, refer to:
- User Guide: `docs/USER_GUIDE.md`
- CLI Documentation: `cli/README.md`
- GitHub Issues: https://github.com/AsithaLKonara/JarvisX/issues

