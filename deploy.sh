#!/bin/bash

# EdonuOps ERP Enterprise Deployment Script
# This script deploys the complete EdonuOps ERP system with enterprise features

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
DOMAIN=${2:-localhost}
SSL_EMAIL=${3:-admin@edonuops.com}

echo -e "${BLUE}🚀 EdonuOps ERP Enterprise Deployment${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}Domain: ${DOMAIN}${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if running as root (for some operations)
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. Some operations may require elevated privileges."
    fi
    
    print_status "Prerequisites check completed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p backup
    mkdir -p nginx/ssl
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p scripts
    
    print_status "Directories created successfully"
}

# Generate SSL certificates
generate_ssl_certificates() {
    print_status "Generating SSL certificates..."
    
    if [ "$DOMAIN" != "localhost" ]; then
        # Use Let's Encrypt for production domains
        if command -v certbot &> /dev/null; then
            print_status "Using Let's Encrypt for SSL certificates..."
            certbot certonly --standalone -d $DOMAIN --email $SSL_EMAIL --agree-tos --non-interactive
            cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
            cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/key.pem
        else
            print_warning "Certbot not found. Generating self-signed certificates..."
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout nginx/ssl/key.pem \
                -out nginx/ssl/cert.pem \
                -subj "/C=US/ST=State/L=City/O=EdonuOps/CN=$DOMAIN"
        fi
    else
        # Generate self-signed certificate for localhost
        print_status "Generating self-signed certificate for localhost..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=EdonuOps/CN=localhost"
    fi
    
    print_status "SSL certificates generated successfully"
}

# Create environment file
create_environment_file() {
    print_status "Creating environment configuration..."
    
    cat > .env << EOF
# EdonuOps ERP Environment Configuration
ENVIRONMENT=$ENVIRONMENT
DOMAIN=$DOMAIN

# Database Configuration
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)

# Security Keys
SECRET_KEY=$(openssl rand -base64 64)
JWT_SECRET_KEY=$(openssl rand -base64 64)

# External Services (Add your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
STRIPE_PUBLIC_KEY=your_stripe_public_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=noreply@edonuops.com

# Monitoring
GRAFANA_PASSWORD=admin

# Optional: External Integrations
SALESFORCE_CLIENT_ID=your_salesforce_client_id
SALESFORCE_CLIENT_SECRET=your_salesforce_client_secret
QUICKBOOKS_CLIENT_ID=your_quickbooks_client_id
QUICKBOOKS_CLIENT_SECRET=your_quickbooks_client_secret
EOF
    
    print_status "Environment file created successfully"
    print_warning "Please update the .env file with your actual API keys before deployment"
}

# Create monitoring configuration
create_monitoring_config() {
    print_status "Creating monitoring configuration..."
    
    # Prometheus configuration
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'edonuops-backend'
    static_configs:
      - targets: ['backend:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:8080']
    metrics_path: '/nginx_status'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
EOF
    
    # Grafana datasource configuration
    mkdir -p monitoring/grafana/datasources
    cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
    
    print_status "Monitoring configuration created successfully"
}

# Create backup script
create_backup_script() {
    print_status "Creating backup script..."
    
    cat > scripts/backup.sh << 'EOF'
#!/bin/bash

# EdonuOps ERP Backup Script
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="edonuops_erp"
DB_USER="edonuops"
DB_HOST="postgres"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
echo "Creating database backup..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: db_backup_$DATE.sql.gz"
EOF
    
    chmod +x scripts/backup.sh
    print_status "Backup script created successfully"
}

# Build and deploy
deploy_application() {
    print_status "Building and deploying application..."
    
    # Build images
    docker-compose build
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_service_health
    
    print_status "Application deployed successfully"
}

# Check service health
check_service_health() {
    print_status "Checking service health..."
    
    # Check backend health
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        print_status "Backend is healthy"
    else
        print_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_status "Frontend is healthy"
    else
        print_error "Frontend health check failed"
        return 1
    fi
    
    # Check database
    if docker-compose exec -T postgres pg_isready -U edonuops > /dev/null 2>&1; then
        print_status "Database is healthy"
    else
        print_error "Database health check failed"
        return 1
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_status "Redis is healthy"
    else
        print_error "Redis health check failed"
        return 1
    fi
    
    print_status "All services are healthy"
}

# Initialize database
initialize_database() {
    print_status "Initializing database..."
    
    # Wait for database to be ready
    sleep 10
    
    # Run database migrations
    docker-compose exec -T backend flask db upgrade
    
    # Initialize with sample data (optional)
    read -p "Do you want to initialize with sample data? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose exec -T backend python scripts/seed_data.py
        print_status "Sample data initialized"
    fi
    
    print_status "Database initialization completed"
}

# Show deployment information
show_deployment_info() {
    echo -e "${BLUE}"
    echo "🎉 EdonuOps ERP Deployment Complete!"
    echo "=================================="
    echo ""
    echo "Access URLs:"
    echo "  Frontend:     https://$DOMAIN"
    echo "  API:          https://$DOMAIN/api"
    echo "  Health Check: https://$DOMAIN/health"
    echo ""
    echo "Monitoring:"
    echo "  Grafana:      http://localhost:3001 (admin/admin)"
    echo "  Prometheus:   http://localhost:9090"
    echo ""
    echo "Database:"
    echo "  Host:         localhost"
    echo "  Port:         5432"
    echo "  Database:     edonuops_erp"
    echo "  Username:     edonuops"
    echo ""
    echo "Management Commands:"
    echo "  View logs:    docker-compose logs -f"
    echo "  Stop:         docker-compose down"
    echo "  Restart:      docker-compose restart"
    echo "  Backup:       docker-compose run backup"
    echo ""
    echo "Next Steps:"
    echo "  1. Update the .env file with your actual API keys"
    echo "  2. Configure your domain DNS to point to this server"
    echo "  3. Set up automated backups"
    echo "  4. Configure monitoring alerts"
    echo ""
    echo -e "${NC}"
}

# Main deployment process
main() {
    echo -e "${BLUE}Starting EdonuOps ERP deployment...${NC}"
    
    check_prerequisites
    create_directories
    create_environment_file
    generate_ssl_certificates
    create_monitoring_config
    create_backup_script
    deploy_application
    initialize_database
    show_deployment_info
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
}

# Handle script arguments
case "$1" in
    "production"|"staging"|"development")
        main
        ;;
    "stop")
        print_status "Stopping EdonuOps ERP..."
        docker-compose down
        print_status "Application stopped"
        ;;
    "restart")
        print_status "Restarting EdonuOps ERP..."
        docker-compose restart
        print_status "Application restarted"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "backup")
        print_status "Creating backup..."
        docker-compose run backup
        print_status "Backup completed"
        ;;
    "update")
        print_status "Updating EdonuOps ERP..."
        git pull
        docker-compose build
        docker-compose up -d
        print_status "Application updated"
        ;;
    *)
        echo "Usage: $0 {production|staging|development|stop|restart|logs|backup|update} [domain] [email]"
        echo ""
        echo "Examples:"
        echo "  $0 production mycompany.com admin@mycompany.com"
        echo "  $0 development localhost"
        echo "  $0 stop"
        echo "  $0 logs"
        exit 1
        ;;
esac
