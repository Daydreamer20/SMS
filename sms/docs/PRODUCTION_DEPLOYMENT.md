# Production Deployment Guide

This guide covers the complete production deployment process for the School Management System.

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 50GB SSD
- **CPU**: 2+ cores
- **Network**: Static IP address, Domain name configured

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- SSL Certificate (for HTTPS)

## Pre-Deployment Checklist

### 1. Security Configuration
- [ ] Generate secure JWT secret key (32+ characters)
- [ ] Create strong database passwords
- [ ] Configure Redis password
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Set up backup encryption keys

### 2. Infrastructure Setup
- [ ] Domain name configured with DNS
- [ ] SSL certificate obtained (Let's Encrypt or commercial)
- [ ] Email SMTP service configured
- [ ] Monitoring service setup (Sentry)
- [ ] Backup storage configured

### 3. Environment Configuration
- [ ] Copy `.env.production` and update all values
- [ ] Verify database connection settings
- [ ] Test email configuration
- [ ] Configure CORS origins
- [ ] Set up trusted hosts

## Deployment Steps

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/sms.git
cd sms

# Copy and configure environment file
cp .env.production .env.production.local
# Edit .env.production.local with your actual values
```

### Step 2: Generate Secure Keys

```bash
# Generate JWT secret key
openssl rand -base64 32

# Generate Redis password
openssl rand -base64 24

# Generate database password
openssl rand -base64 16
```

### Step 3: SSL Certificate Setup

```bash
# Create SSL directory
mkdir -p docker/nginx/ssl

# Copy your SSL certificates
cp your-cert.pem docker/nginx/ssl/cert.pem
cp your-key.pem docker/nginx/ssl/key.pem

# Set proper permissions
chmod 600 docker/nginx/ssl/key.pem
chmod 644 docker/nginx/ssl/cert.pem
```

### Step 4: Database Initialization

```bash
# Start database service first
docker-compose -f docker-compose.prod.yml up -d db redis

# Wait for database to be ready
docker-compose -f docker-compose.prod.yml exec db pg_isready -U sms_prod_user

# Run database migrations
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

### Step 5: Build and Deploy

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build --no-cache

# Deploy all services
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

### Step 6: Health Checks

```bash
# Run health checks
./scripts/health-check.sh

# Check individual services
curl http://localhost:8000/health
curl http://localhost:80/health
curl http://localhost/api/monitoring/health/detailed
```

## Post-Deployment Configuration

### 1. Create Admin User

```bash
# Access backend container
docker-compose -f docker-compose.prod.yml exec backend bash

# Create superuser (implement this endpoint)
python -c "
from app.core.database import get_db
from app.services.user_service import create_admin_user
import asyncio

async def create_admin():
    async for db in get_db():
        await create_admin_user(
            db=db,
            username='admin',
            email='admin@yourschool.com',
            password='secure_admin_password'
        )
        break

asyncio.run(create_admin())
"
```

### 2. Configure Backup Schedule

```bash
# Add to crontab for automated backups
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * /path/to/sms/scripts/backup.sh
```

### 3. Set Up Monitoring

```bash
# Configure log rotation
sudo nano /etc/logrotate.d/sms

# Add monitoring alerts
# Configure Sentry error tracking
# Set up uptime monitoring
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. System Updates

```bash
# Keep system updated
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
sudo yum update -y                      # CentOS/RHEL
```

### 3. Docker Security

```bash
# Run containers as non-root user
# Enable Docker content trust
export DOCKER_CONTENT_TRUST=1

# Scan images for vulnerabilities
docker scan sms_backend_prod
docker scan sms_frontend_prod
```

## Monitoring and Maintenance

### 1. Log Management

```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f nginx

# Log locations
# Application logs: ./logs/
# Nginx logs: ./logs/nginx/
# Database logs: Docker container logs
```

### 2. Performance Monitoring

```bash
# Monitor resource usage
docker stats

# Database performance
docker-compose -f docker-compose.prod.yml exec db psql -U sms_prod_user -d sms_production -c "
SELECT * FROM pg_stat_activity WHERE state = 'active';
"

# Redis monitoring
docker-compose -f docker-compose.prod.yml exec redis redis-cli info
```

### 3. Backup Verification

```bash
# Test backup restoration
./scripts/restore.sh backup_file.sql

# Verify backup integrity
./scripts/verify-backup.sh
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database status
   docker-compose -f docker-compose.prod.yml exec db pg_isready
   
   # Check logs
   docker-compose -f docker-compose.prod.yml logs db
   ```

2. **Redis Connection Failed**
   ```bash
   # Test Redis connection
   docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
   ```

3. **SSL Certificate Issues**
   ```bash
   # Verify certificate
   openssl x509 -in docker/nginx/ssl/cert.pem -text -noout
   
   # Test SSL configuration
   openssl s_client -connect your-domain.com:443
   ```

4. **High Memory Usage**
   ```bash
   # Check container resource usage
   docker stats
   
   # Optimize database settings
   # Adjust worker processes
   # Enable Redis memory optimization
   ```

### Emergency Procedures

1. **Service Restart**
   ```bash
   # Restart specific service
   docker-compose -f docker-compose.prod.yml restart backend
   
   # Full system restart
   docker-compose -f docker-compose.prod.yml down
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Database Recovery**
   ```bash
   # Restore from backup
   ./scripts/restore.sh latest_backup.sql
   
   # Check database integrity
   docker-compose -f docker-compose.prod.yml exec db pg_dump --schema-only
   ```

3. **Rollback Deployment**
   ```bash
   # Rollback to previous version
   git checkout previous-stable-tag
   docker-compose -f docker-compose.prod.yml up -d --force-recreate
   ```

## Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes for frequently queried columns
CREATE INDEX CONCURRENTLY idx_students_class_id ON students(class_id);
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_attendance_date ON attendance(date);

-- Analyze tables
ANALYZE;

-- Update statistics
UPDATE pg_stat_user_tables SET n_tup_ins = 0, n_tup_upd = 0, n_tup_del = 0;
```

### 2. Redis Optimization

```bash
# Configure Redis for production
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

### 3. Nginx Optimization

```nginx
# Add to nginx configuration
worker_processes auto;
worker_connections 2048;
keepalive_timeout 65;
client_max_body_size 50M;
```

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer Setup**
   - Configure multiple backend instances
   - Use Redis for session storage
   - Implement database read replicas

2. **Container Orchestration**
   - Consider Kubernetes for large deployments
   - Use Docker Swarm for simpler scaling
   - Implement auto-scaling policies

### Vertical Scaling

1. **Resource Allocation**
   - Increase container memory limits
   - Add more CPU cores
   - Use faster storage (NVMe SSD)

2. **Database Scaling**
   - Increase shared_buffers
   - Optimize connection pooling
   - Consider database clustering

## Compliance and Security

### Data Protection

1. **Encryption**
   - Database encryption at rest
   - SSL/TLS for data in transit
   - Backup encryption

2. **Access Control**
   - Role-based permissions
   - API rate limiting
   - Audit logging

3. **Privacy Compliance**
   - GDPR compliance measures
   - Data retention policies
   - User consent management

## Support and Maintenance

### Regular Maintenance Tasks

- [ ] Weekly security updates
- [ ] Monthly backup verification
- [ ] Quarterly performance review
- [ ] Annual security audit

### Emergency Contacts

- System Administrator: [contact-info]
- Database Administrator: [contact-info]
- Security Team: [contact-info]
- Hosting Provider: [contact-info]

---

For additional support, please refer to the project documentation or contact the development team.