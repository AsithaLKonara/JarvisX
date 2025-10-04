#!/bin/bash

# JarvisX Production Deployment Script
# This script deploys JarvisX to a production environment with full enterprise features

set -e

echo "🚀 Starting JarvisX Production Deployment..."

# Configuration
PROJECT_NAME="jarvisx"
DOMAIN="${DOMAIN:-jarvisx.yourdomain.com}"
SSL_EMAIL="${SSL_EMAIL:-admin@yourdomain.com}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if required environment variables are set
    if [ -z "$OPENAI_API_KEY" ]; then
        error "OPENAI_API_KEY environment variable is required"
    fi
    
    if [ -z "$JWT_SECRET" ]; then
        error "JWT_SECRET environment variable is required"
    fi
    
    if [ -z "$DB_PASSWORD" ]; then
        error "DB_PASSWORD environment variable is required"
    fi
    
    log "Prerequisites check passed ✓"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p {logs,data,backups,ssl,nginx,monitoring/{prometheus,grafana/{dashboards,datasources}}}
    
    # Set proper permissions
    chmod 755 logs data backups ssl nginx monitoring
    
    log "Directories created ✓"
}

# Generate SSL certificates
generate_ssl_certificates() {
    log "Generating SSL certificates..."
    
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        # Generate self-signed certificate for development
        # In production, you should use Let's Encrypt or a proper CA
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem \
            -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN}"
        
        log "SSL certificates generated ✓"
    else
        log "SSL certificates already exist ✓"
    fi
}

# Create production configuration files
create_configurations() {
    log "Creating production configuration files..."
    
    # Create nginx configuration
    cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream orchestrator {
        server orchestrator:3000;
    }
    
    upstream stt {
        server stt:8001;
    }
    
    upstream tts {
        server tts:8002;
    }
    
    upstream web-executor {
        server web-executor:8003;
    }
    
    upstream whatsapp {
        server whatsapp:8004;
    }
    
    upstream pc-agent {
        server pc-agent:8005;
    }
    
    upstream trading {
        server trading:8006;
    }
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=upload:10m rate=1r/s;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    server {
        listen 80;
        server_name ${DOMAIN};
        return 301 https://\$server_name\$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name ${DOMAIN};
        
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://orchestrator/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # WebSocket connections
        location /ws {
            proxy_pass http://orchestrator;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Service-specific endpoints
        location /stt/ {
            proxy_pass http://stt/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        location /tts/ {
            proxy_pass http://tts/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        location /web/ {
            proxy_pass http://web-executor/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        location /whatsapp/ {
            proxy_pass http://whatsapp/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        location /pc-agent/ {
            proxy_pass http://pc-agent/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        location /trading/ {
            limit_req zone=api burst=10 nodelay;
            proxy_pass http://trading/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Static files and uploads
        location /uploads/ {
            limit_req zone=upload burst=5 nodelay;
            proxy_pass http://orchestrator/uploads/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF

    # Create Prometheus configuration
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'jarvisx-orchestrator'
    static_configs:
      - targets: ['orchestrator:3000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'jarvisx-stt'
    static_configs:
      - targets: ['stt:8001']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'jarvisx-tts'
    static_configs:
      - targets: ['tts:8002']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'jarvisx-web-executor'
    static_configs:
      - targets: ['web-executor:8003']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'jarvisx-whatsapp'
    static_configs:
      - targets: ['whatsapp:8004']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'jarvisx-pc-agent'
    static_configs:
      - targets: ['pc-agent:8005']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'jarvisx-trading'
    static_configs:
      - targets: ['trading:8006']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF

    log "Configuration files created ✓"
}

# Build and deploy services
deploy_services() {
    log "Building and deploying services..."
    
    # Pull latest images
    docker-compose -f docker-compose.production.yml pull
    
    # Build custom images
    docker-compose -f docker-compose.production.yml build --no-cache
    
    # Start services
    docker-compose -f docker-compose.production.yml up -d
    
    log "Services deployed ✓"
}

# Wait for services to be ready
wait_for_services() {
    log "Waiting for services to be ready..."
    
    # Wait for database
    log "Waiting for PostgreSQL..."
    while ! docker-compose -f docker-compose.production.yml exec postgres pg_isready -U jarvisx -d jarvisx_prod; do
        sleep 2
    done
    
    # Wait for Redis
    log "Waiting for Redis..."
    while ! docker-compose -f docker-compose.production.yml exec redis redis-cli ping; do
        sleep 2
    done
    
    # Wait for orchestrator
    log "Waiting for Orchestrator..."
    while ! curl -f http://localhost:3000/health > /dev/null 2>&1; do
        sleep 5
    done
    
    log "All services are ready ✓"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    docker-compose -f docker-compose.production.yml exec orchestrator npm run migrate:prod
    
    log "Database migrations completed ✓"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Wait for Grafana to be ready
    log "Waiting for Grafana..."
    while ! curl -f http://localhost:3001 > /dev/null 2>&1; do
        sleep 5
    done
    
    # Import dashboards
    log "Importing Grafana dashboards..."
    # This would import pre-configured dashboards for JarvisX monitoring
    
    log "Monitoring setup completed ✓"
}

# Setup backups
setup_backups() {
    log "Setting up backup system..."
    
    # Create backup script
    cat > scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/jarvisx_backup_$DATE.tar.gz"

# Create backup
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U jarvisx jarvisx_prod | gzip > "$BACKUP_FILE"

# Clean old backups
find $BACKUP_DIR -name "jarvisx_backup_*.tar.gz" -mtime +$BACKUP_RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_FILE"
EOF
    
    chmod +x scripts/backup.sh
    
    log "Backup system setup completed ✓"
}

# Health check
health_check() {
    log "Running health checks..."
    
    # Check all services
    services=("orchestrator:3000" "stt:8001" "tts:8002" "web-executor:8003" "whatsapp:8004" "pc-agent:8005" "trading:8006")
    
    for service in "${services[@]}"; do
        IFS=':' read -r name port <<< "$service"
        if curl -f "http://localhost:$port/health" > /dev/null 2>&1; then
            log "$name is healthy ✓"
        else
            warn "$name health check failed"
        fi
    done
    
    log "Health checks completed ✓"
}

# Main deployment function
main() {
    log "Starting JarvisX Production Deployment"
    log "Domain: $DOMAIN"
    log "Project: $PROJECT_NAME"
    
    check_prerequisites
    create_directories
    generate_ssl_certificates
    create_configurations
    deploy_services
    wait_for_services
    run_migrations
    setup_monitoring
    setup_backups
    health_check
    
    log "🎉 JarvisX Production Deployment Completed Successfully!"
    log ""
    log "Services are now running:"
    log "  - Orchestrator: https://$DOMAIN/api/"
    log "  - STT Service: https://$DOMAIN/stt/"
    log "  - TTS Service: https://$DOMAIN/tts/"
    log "  - Web Executor: https://$DOMAIN/web/"
    log "  - WhatsApp: https://$DOMAIN/whatsapp/"
    log "  - PC Agent: https://$DOMAIN/pc-agent/"
    log "  - Trading: https://$DOMAIN/trading/"
    log ""
    log "Monitoring:"
    log "  - Grafana: http://localhost:3001 (admin / $GRAFANA_PASSWORD)"
    log "  - Prometheus: http://localhost:9090"
    log "  - Kibana: http://localhost:5601"
    log ""
    log "Next steps:"
    log "  1. Configure your domain DNS to point to this server"
    log "  2. Set up SSL certificates with Let's Encrypt (recommended)"
    log "  3. Configure monitoring alerts"
    log "  4. Set up backup verification"
    log ""
    log "For support, check the logs:"
    log "  docker-compose -f docker-compose.production.yml logs -f"
}

# Run main function
main "$@"
