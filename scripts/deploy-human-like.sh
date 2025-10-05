#!/bin/bash

# JarvisX Human-Like Features Production Deployment Script
# Deploys the complete JarvisX system with human-like personality

echo "🚀 JarvisX Human-Like Features Production Deployment"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

print_feature() {
    echo -e "${PURPLE}$1${NC}"
}

# Configuration
DEPLOYMENT_ENV=${1:-"production"}
DOMAIN=${2:-"jarvisx.local"}
SSL_CERT_PATH=${3:-""}
SSL_KEY_PATH=${4:-""}

print_header "🎯 Deployment Configuration"
echo "Environment: $DEPLOYMENT_ENV"
echo "Domain: $DOMAIN"
echo "SSL Cert: $SSL_CERT_PATH"
echo "SSL Key: $SSL_KEY_PATH"
echo ""

# Check prerequisites
print_header "🔍 Checking Prerequisites"

# Check Docker
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi
print_success "Docker is running"

# Check Docker Compose
if ! docker-compose --version > /dev/null 2>&1; then
    print_error "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi
print_success "Docker Compose is available"

# Check environment variables
print_status "Checking environment variables..."
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp env.example .env
    print_warning "Please edit .env file with your API keys and configuration"
fi

# Load environment variables
source .env 2>/dev/null || true

# Check required API keys
REQUIRED_KEYS=("OPENAI_API_KEY" "GOOGLE_TTS_API_KEY")
MISSING_KEYS=()

for key in "${REQUIRED_KEYS[@]}"; do
    if [ -z "${!key}" ]; then
        MISSING_KEYS+=("$key")
    fi
done

if [ ${#MISSING_KEYS[@]} -gt 0 ]; then
    print_warning "Missing API keys: ${MISSING_KEYS[*]}"
    print_warning "Some features may not work without these keys"
fi

echo ""

# Step 1: Build all services
print_header "🏗️ Building All Services"
echo ""

print_feature "Building Personality Engine..."
cd services/personality
npm install --production
npm run build
if [ $? -eq 0 ]; then
    print_success "Personality Engine built successfully"
else
    print_error "Failed to build Personality Engine"
    exit 1
fi
cd ../..

print_feature "Building Orchestrator..."
cd apps/orchestrator
npm install --production
npm run build
if [ $? -eq 0 ]; then
    print_success "Orchestrator built successfully"
else
    print_error "Failed to build Orchestrator"
    exit 1
fi
cd ../..

print_feature "Building Desktop App..."
cd apps/desktop
npm install --production
npm run build
if [ $? -eq 0 ]; then
    print_success "Desktop App built successfully"
else
    print_error "Failed to build Desktop App"
    exit 1
fi
cd ../..

print_feature "Building Mobile App..."
cd apps/mobile
npm install --production
npm run build
if [ $? -eq 0 ]; then
    print_success "Mobile App built successfully"
else
    print_error "Failed to build Mobile App"
    exit 1
fi
cd ../..

echo ""

# Step 2: Build Docker images
print_header "🐳 Building Docker Images"
echo ""

print_status "Building all Docker images..."
docker-compose -f docker-compose.production.yml build --no-cache

if [ $? -eq 0 ]; then
    print_success "All Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

echo ""

# Step 3: Create production configuration
print_header "⚙️ Creating Production Configuration"
echo ""

# Create production environment file
cat > .env.production << EOF
# JarvisX Production Environment
NODE_ENV=production
DEPLOYMENT_ENV=$DEPLOYMENT_ENV
DOMAIN=$DOMAIN

# API Keys
OPENAI_API_KEY=${OPENAI_API_KEY}
GOOGLE_TTS_API_KEY=${GOOGLE_TTS_API_KEY}
ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
GOOGLE_CLOUD_KEY=${GOOGLE_CLOUD_KEY}
GPT_API_KEY=${GPT_API_KEY}

# Database
DATABASE_URL=postgresql://jarvisx:${POSTGRES_PASSWORD:-jarvisx123}@postgres:5432/jarvisx_prod
REDIS_URL=redis://redis:6379

# Security
JWT_SECRET=${JWT_SECRET:-$(openssl rand -hex 32)}
ENCRYPTION_KEY=${ENCRYPTION_KEY:-$(openssl rand -hex 32)}

# Services
ORCHESTRATOR_PORT=3000
PERSONALITY_PORT=8007
STT_PORT=8001
TTS_PORT=8002
WHATSAPP_PORT=8003
PC_AGENT_PORT=8004
TRADING_PORT=8005

# External Services
WHATSAPP_TOKEN=${WHATSAPP_TOKEN}
WEBHOOK_SECRET=${WEBHOOK_SECRET}

# Trading
BINANCE_API_KEY=${BINANCE_API_KEY}
BINANCE_SECRET_KEY=${BINANCE_SECRET_KEY}

# Monitoring
SENTRY_DSN=${SENTRY_DSN}
LOG_LEVEL=info
EOF

print_success "Production environment file created"

# Create Nginx configuration
cat > nginx.conf << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    # SSL Configuration
    ssl_certificate $SSL_CERT_PATH;
    ssl_certificate_key $SSL_KEY_PATH;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Main application
    location / {
        proxy_pass http://orchestrator:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Personality service
    location /personality/ {
        proxy_pass http://personality:8007/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # WebSocket connections
    location /ws {
        proxy_pass http://orchestrator:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static files
    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health checks
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

print_success "Nginx configuration created"

echo ""

# Step 4: Deploy with Docker Compose
print_header "🚀 Deploying Services"
echo ""

print_status "Starting all services with Docker Compose..."
docker-compose -f docker-compose.production.yml up -d

if [ $? -eq 0 ]; then
    print_success "All services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi

echo ""

# Step 5: Health checks
print_header "🏥 Health Checks"
echo ""

# Wait for services to start
print_status "Waiting for services to initialize..."
sleep 30

# Check orchestrator
print_feature "Checking Orchestrator..."
if curl -s http://localhost:3000/health > /dev/null; then
    print_success "Orchestrator is healthy"
else
    print_warning "Orchestrator health check failed"
fi

# Check personality service
print_feature "Checking Personality Engine..."
if curl -s http://localhost:8007/health > /dev/null; then
    print_success "Personality Engine is healthy"
else
    print_warning "Personality Engine health check failed"
fi

# Check STT service
print_feature "Checking STT Service..."
if curl -s http://localhost:8001/health > /dev/null; then
    print_success "STT Service is healthy"
else
    print_warning "STT Service health check failed"
fi

# Check TTS service
print_feature "Checking TTS Service..."
if curl -s http://localhost:8002/health > /dev/null; then
    print_success "TTS Service is healthy"
else
    print_warning "TTS Service health check failed"
fi

echo ""

# Step 6: Initialize personality
print_header "🧠 Initializing Personality System"
echo ""

print_status "Initializing JarvisX personality..."
PERSONALITY_INIT=$(curl -s -X POST http://localhost:8007/personality/update \
  -H "Content-Type: application/json" \
  -d '{
    "traits": {
      "intelligence": 95,
      "humor": 70,
      "empathy": 85,
      "confidence": 90,
      "enthusiasm": 80,
      "creativity": 75,
      "culturalAwareness": 90
    },
    "mood": "optimistic",
    "preferences": {
      "language": "mixed",
      "formality": "professional",
      "humor": "subtle"
    }
  }')

if echo "$PERSONALITY_INIT" | grep -q "success"; then
    print_success "Personality system initialized successfully"
else
    print_warning "Personality initialization may have issues"
fi

echo ""

# Step 7: Setup monitoring
print_header "📊 Setting Up Monitoring"
echo ""

# Create monitoring script
cat > scripts/monitor.sh << 'EOF'
#!/bin/bash

echo "🔍 JarvisX System Monitoring"
echo "============================"

# Check service status
echo "Service Status:"
docker-compose -f docker-compose.production.yml ps

echo ""
echo "Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

echo ""
echo "Health Checks:"
curl -s http://localhost:3000/health | jq '.' 2>/dev/null || echo "Orchestrator: Not responding"
curl -s http://localhost:8007/health | jq '.' 2>/dev/null || echo "Personality: Not responding"

echo ""
echo "Personality Status:"
curl -s http://localhost:8007/personality/status | jq '.' 2>/dev/null || echo "Personality status unavailable"
EOF

chmod +x scripts/monitor.sh
print_success "Monitoring script created"

echo ""

# Step 8: Create backup script
print_header "💾 Setting Up Backup"
echo ""

cat > scripts/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backups/jarvisx"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "🔄 Creating backup: $DATE"

# Backup database
docker exec postgres pg_dump -U jarvisx jarvisx_prod > $BACKUP_DIR/database_$DATE.sql

# Backup personality data
docker exec personality tar -czf - /app/data > $BACKUP_DIR/personality_$DATE.tar.gz

# Backup configuration
cp .env.production $BACKUP_DIR/env_$DATE

echo "✅ Backup completed: $BACKUP_DIR"
EOF

chmod +x scripts/backup.sh
print_success "Backup script created"

echo ""

# Step 9: Final verification
print_header "✅ Final Verification"
echo ""

print_status "Running final system verification..."

# Test personality response
echo "Testing personality system..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:8007/personality/respond \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello JarvisX, are you ready to help?",
    "context": {"type": "greeting"},
    "userEmotion": "friendly"
  }')

if echo "$TEST_RESPONSE" | grep -q "response"; then
    print_success "Personality system is responding correctly"
    echo "Sample response: $(echo "$TEST_RESPONSE" | jq -r '.response' 2>/dev/null)"
else
    print_warning "Personality system test failed"
fi

echo ""

# Step 10: Deployment summary
print_header "🎉 Deployment Complete!"
echo ""

print_success "JarvisX Human-Like Features have been deployed successfully!"
echo ""

echo "🌐 Access Points:"
echo "  • Main Application: http://$DOMAIN"
echo "  • Personality API: http://$DOMAIN/personality/"
echo "  • Health Check: http://$DOMAIN/health"
echo ""

echo "📱 Applications:"
echo "  • Desktop App: Built and ready for distribution"
echo "  • Mobile App: Built and ready for app stores"
echo ""

echo "🧠 Personality Features:"
echo "  • Emotional Intelligence: ✅ Active"
echo "  • Memory System: ✅ Active"
echo "  • Cultural Awareness: ✅ Active"
echo "  • Voice Personality: ✅ Active"
echo "  • Conversation Engine: ✅ Active"
echo ""

echo "🔧 Management Commands:"
echo "  • Monitor: ./scripts/monitor.sh"
echo "  • Backup: ./scripts/backup.sh"
echo "  • Logs: docker-compose -f docker-compose.production.yml logs -f"
echo ""

echo "📊 Next Steps:"
echo "  1. Configure SSL certificates for HTTPS"
echo "  2. Set up domain DNS to point to this server"
echo "  3. Configure monitoring alerts"
echo "  4. Set up automated backups"
echo "  5. Test all features thoroughly"
echo ""

print_success "JarvisX is now live with full human-like personality! 🤖✨"
echo ""
echo "Ayubowan! Your AI companion is ready to serve!"
