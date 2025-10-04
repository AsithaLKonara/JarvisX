# JarvisX - Sinhala-enabled Cross-platform AI Assistant

JarvisX is a comprehensive AI assistant that understands Sinhala and English, executes tasks across desktop, web, and mobile platforms, and provides secure, permissioned automation capabilities.

## 🚀 Features

### Core Capabilities
- **Sinhala Speech-to-Text**: Powered by OpenAI Whisper for accurate Sinhala transcription
- **Sinhala Text-to-Speech**: Google Cloud TTS with Festival fallback for natural Sinhala speech
- **GPT-5 Integration**: Advanced task planning and natural language understanding
- **Cross-platform Execution**: Desktop, web, and mobile task execution
- **Real-time Communication**: WebSocket-based real-time updates and approvals

### Security & Permissions
- **Granular Permissions**: Fine-grained access control for all operations
- **Audit Logging**: Comprehensive logging of all system events
- **Dry-run Mode**: Test operations before execution
- **User Approval Flow**: Mandatory approval for sensitive operations

### Executors
- **System Executor**: Open applications, run whitelisted commands, file operations
- **Web Executor**: Playwright-based web automation for e-commerce and other sites
- **WhatsApp Executor**: Parse orders from WhatsApp messages and send confirmations
- **TTS Executor**: Text-to-speech synthesis in Sinhala and English

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Desktop App   │    │  Mobile App     │    │   Web Client    │
│   (Tauri)       │    │  (React Native) │    │   (Optional)    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     Orchestrator API      │
                    │   (Node.js + TypeScript)  │
                    └─────────────┬─────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
┌───────┴───────┐    ┌────────────┴────────────┐    ┌──────┴──────┐
│  STT Service  │    │      TTS Service        │    │   LLM       │
│ (Python +     │    │   (Node.js + Google     │    │ Service     │
│  Whisper)     │    │    Cloud TTS)           │    │ (GPT-5)     │
└───────────────┘    └─────────────────────────┘    └─────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────┴───────┐    ┌────────┴────────┐    ┌──────┴──────┐
│System Executor│    │ Web Executor    │    │WhatsApp     │
│(Whitelisted   │    │(Playwright)     │    │Executor     │
│ Commands)     │    │                 │    │             │
└───────────────┘    └─────────────────┘    └─────────────┘
```

## 📁 Project Structure

```
jarvisx/
├── apps/
│   ├── desktop/          # Tauri + React desktop application
│   ├── orchestrator/     # Core orchestrator API service
│   └── mobile/           # React Native mobile companion
├── services/
│   ├── stt/              # Speech-to-Text service (Python + Whisper)
│   ├── tts/              # Text-to-Speech service (Node.js)
│   ├── web-executor/     # Web automation service (Playwright)
│   ├── system-executor/  # System command executor
│   └── whatsapp/         # WhatsApp Business API integration
├── shared/
│   ├── schemas/          # JSON schemas for validation
│   └── prompts/          # LLM prompt templates
├── tests/                # Integration and E2E tests
├── scripts/              # Demo and utility scripts
└── .github/workflows/    # CI/CD pipeline configuration
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- OpenAI API key
- Google Cloud TTS credentials (optional)
- WhatsApp Business API token (optional)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd jarvisx
npm install
```

### 2. Environment Configuration

```bash
cp env.example .env
# Edit .env with your API keys and configuration
```

### 3. Start Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start individual services for development
npm run dev
```

### 4. Verify Installation

```bash
# Check service health
curl http://localhost:3000/health  # Orchestrator
curl http://localhost:8001/health  # STT Service
curl http://localhost:8002/health  # TTS Service
curl http://localhost:8003/health  # WhatsApp Service
```

## 🎯 Usage Examples

### 1. Voice Command Processing

```bash
# Send audio file for Sinhala transcription
curl -X POST http://localhost:8001/transcribe \
  -F "file=@audio.wav" \
  -F "language=si"
```

### 2. Task Planning and Execution

```bash
# Create a new task
curl -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Open Cursor IDE",
    "user_id": "user123"
  }'

# Approve and execute task
curl -X PATCH http://localhost:3000/tasks/{task_id}/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by": "user123", "dry_run": false}'
```

### 3. WhatsApp Order Processing

```bash
# Parse WhatsApp message for order
curl -X POST http://localhost:8003/parse-order \
  -H "Content-Type: application/json" \
  -d '{
    "message": "මට ලැප්ටොප් 2ක් ගන්න ඕන. මගේ නම කමල්."
  }'
```

### 4. Web Automation

```bash
# Create order in e-commerce admin
curl -X POST http://localhost:8004/create-order \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "admin_url": "https://admin.example.com",
      "admin_email": "admin@example.com",
      "admin_password": "password"
    },
    "order": {
      "customer": {"name": "John Doe"},
      "items": [{"sku": "LAPTOP-001", "title": "Laptop", "qty": 1}]
    },
    "dry_run": true
  }'
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GPT_API_KEY` | OpenAI API key for GPT-5 | Yes |
| `GOOGLE_CLOUD_KEY` | Google Cloud TTS credentials | No |
| `WHATSAPP_TOKEN` | WhatsApp Business API token | No |
| `JWT_SECRET` | JWT signing secret | Yes |
| `DATABASE_URL` | SQLite database path | No |

### Permission Scopes

- `read_files`: Read files from specified paths
- `run_command`: Execute whitelisted system commands
- `network`: Make network requests to specified domains
- `use_credentials`: Access stored credentials
- `admin_access`: Administrative system access
- `create_tasks`: Create new tasks
- `approve_tasks`: Approve pending tasks
- `execute_tasks`: Execute approved tasks

## 🧪 Testing

### Unit Tests

```bash
# Run all unit tests
npm test

# Run specific service tests
cd apps/orchestrator && npm test
cd services/stt && python -m pytest test_stt.py -v
```

### Integration Tests

```bash
# Start services
docker-compose up -d

# Run integration tests
npm run test:integration

# Check test results
cat TEST_RESULTS.xml
```

### E2E Testing

```bash
# Run end-to-end tests
npm run test:e2e
```

## 📊 Monitoring

### Health Checks

All services expose health check endpoints:

- Orchestrator: `GET /health`
- STT Service: `GET /health`
- TTS Service: `GET /health`
- WhatsApp Service: `GET /health`

### Audit Logging

All system events are logged to the database and can be viewed via:

```bash
curl http://localhost:3000/admin/audit-logs
```

### Metrics

Basic metrics are available at:

```bash
curl http://localhost:3000/admin/stats
```

## 🔒 Security

### Authentication

- JWT-based authentication
- Role-based access control
- Session management

### Permissions

- Granular permission system
- Resource-specific access control
- Permission expiration

### Audit Trail

- All actions logged with timestamps
- User attribution
- Immutable audit logs

## 🚀 Deployment

### Docker Deployment

```bash
# Build and deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

### Production Considerations

- Use environment-specific configurations
- Enable SSL/TLS certificates
- Configure proper secrets management
- Set up monitoring and alerting
- Regular database backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Setup

```bash
# Install dependencies
npm install

# Start development environment
npm run dev

# Run linting
npm run lint

# Run tests
npm test
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Documentation: [Wiki](https://github.com/your-org/jarvisx/wiki)
- Issues: [GitHub Issues](https://github.com/your-org/jarvisx/issues)
- Discussions: [GitHub Discussions](https://github.com/your-org/jarvisx/discussions)

## 🗺️ Roadmap

### Version 1.0 (MVP)
- [x] Core orchestrator with GPT-5 integration
- [x] STT/TTS services with Sinhala support
- [x] System, web, and WhatsApp executors
- [x] Permission system and audit logging
- [x] Basic desktop and mobile interfaces

### Version 1.1
- [ ] Plugin marketplace
- [ ] Advanced monitoring dashboard
- [ ] Local LLM fallback options
- [ ] Enhanced mobile features

### Version 2.0
- [ ] Multi-language support (Tamil, Hindi)
- [ ] Advanced RPA capabilities
- [ ] Enterprise features
- [ ] Cloud deployment options

---

**JarvisX** - Your intelligent Sinhala-speaking AI assistant! 🤖✨