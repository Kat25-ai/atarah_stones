# 🚀 Comprehensive Deployment Guide
## Fundamental News Trading Dashboard

This guide covers all deployment options for the Fundamental News Trading Dashboard, from local development to enterprise cloud deployments.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployments](#cloud-deployments)
5. [Performance Optimization](#performance-optimization)
6. [Monitoring & Scaling](#monitoring--scaling)
7. [Security Considerations](#security-considerations)

## 🚀 Quick Start

### Option 1: Lightweight CPU-Only Version
```bash
# Navigate to dashboard directory
cd fundamental_news_dashboard

# Run the lightweight version (optimized for CPU-only machines)
python lightweight_app.py
```

### Option 2: Full-Featured Version
```bash
# Install dependencies
pip install -r requirements.txt

# Run the full dashboard
python run_dashboard.py
```

### Option 3: Docker (Recommended)
```bash
# Build and run with Docker
docker build -t trading-dashboard .
docker run -p 8501:8501 trading-dashboard
```

## 💻 Local Development

### Prerequisites
- Python 3.8+
- 2GB RAM minimum (4GB recommended)
- Internet connection for real-time data

### Setup Steps
1. **Clone/Download the dashboard files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```
4. **Run the dashboard:**
   ```bash
   streamlit run app.py
   ```

### Development Features
- Hot reload for code changes
- Debug mode with detailed error messages
- Local database for testing
- Mock data for offline development

## 🐳 Docker Deployment

### Single Container
```bash
# Build the image
docker build -t trading-dashboard -f deploy/docker/Dockerfile .

# Run the container
docker run -d \
  --name trading-dashboard \
  -p 8501:8501 \
  -e STREAMLIT_SERVER_HEADLESS=true \
  trading-dashboard
```

### Multi-Container with Docker Compose
```bash
# Start all services
docker-compose -f deploy/docker/docker-compose.yml up -d

# Services included:
# - Main dashboard (port 8501)
# - Lightweight dashboard (port 8502)
# - Redis cache (port 6379)
# - PostgreSQL database (port 5432)
# - Nginx reverse proxy (port 80/443)
# - Prometheus monitoring (port 9090)
# - Grafana dashboards (port 3000)
```

### Production Docker Setup
```bash
# Build production image
docker build -t trading-dashboard:prod \
  --target production \
  -f deploy/docker/Dockerfile .

# Run with production settings
docker run -d \
  --name trading-dashboard-prod \
  -p 80:8501 \
  --restart unless-stopped \
  --memory="1g" \
  --cpus="1.0" \
  -e STREAMLIT_SERVER_HEADLESS=true \
  -e STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
  trading-dashboard:prod
```

## ☁️ Cloud Deployments

### AWS Deployment

#### EC2 Instance
```bash
# Deploy to EC2
python deploy/aws_deploy.py \
  --deployment-type ec2 \
  --instance-type t3.micro \
  --region us-east-1
```

#### ECS Fargate
```bash
# Deploy to ECS
python deploy/aws_deploy.py \
  --deployment-type ecs \
  --region us-east-1
```

#### Lambda Function
```bash
# Deploy as Lambda
python deploy/aws_deploy.py \
  --deployment-type lambda \
  --region us-east-1
```

### Azure Deployment

#### App Service
```bash
# Deploy to Azure App Service
python deploy/azure_deploy.py \
  --deployment-type appservice \
  --subscription-id YOUR_SUBSCRIPTION_ID \
  --resource-group trading-dashboard-rg \
  --app-name trading-dashboard-app
```

#### Container Instances
```bash
# Deploy to Azure Container Instances
python deploy/azure_deploy.py \
  --deployment-type container \
  --subscription-id YOUR_SUBSCRIPTION_ID \
  --resource-group trading-dashboard-rg \
  --app-name trading-dashboard-container
```

#### Azure Functions
```bash
# Deploy to Azure Functions
python deploy/azure_deploy.py \
  --deployment-type function \
  --subscription-id YOUR_SUBSCRIPTION_ID \
  --resource-group trading-dashboard-rg \
  --app-name trading-dashboard-func
```

### Google Cloud Platform

#### Cloud Run
```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/trading-dashboard
gcloud run deploy trading-dashboard \
  --image gcr.io/PROJECT_ID/trading-dashboard \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### App Engine
```bash
# Deploy to App Engine
gcloud app deploy app.yaml
```

## ⚡ Performance Optimization

### CPU-Only Optimization
The lightweight version is specifically optimized for CPU-only environments:

- **Keyword-based sentiment analysis** instead of deep learning models
- **Efficient caching** with 5-minute cache duration
- **Reduced memory footprint** with limited data retention
- **Optimized refresh intervals** to reduce CPU load

### Memory Optimization
```python
# Configuration for low-memory environments
LIGHTWEIGHT_CONFIG = {
    'MAX_NEWS_ITEMS': 10,      # Reduced from 20
    'MAX_EVENTS': 5,           # Reduced from 10
    'CACHE_DURATION': 300,     # 5 minutes
    'REFRESH_INTERVAL': 60,    # 1 minute
}
```

### Database Optimization
- Use SQLite for single-user deployments
- PostgreSQL for multi-user environments
- Redis for session caching
- Implement connection pooling for high-traffic scenarios

## 📊 Monitoring & Scaling

### Health Checks
```bash
# Application health check
curl http://localhost:8501/_stcore/health

# Custom health endpoint
curl http://localhost:8501/api/health
```

### Monitoring Setup

#### Prometheus Metrics
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'trading-dashboard'
    static_configs:
      - targets: ['trading-dashboard:8501']
```

#### Grafana Dashboards
- Application performance metrics
- User activity tracking
- System resource utilization
- Error rate monitoring

### Auto-Scaling

#### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-dashboard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: trading-dashboard
  template:
    metadata:
      labels:
        app: trading-dashboard
    spec:
      containers:
      - name: dashboard
        image: trading-dashboard:latest
        ports:
        - containerPort: 8501
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: trading-dashboard-service
spec:
  selector:
    app: trading-dashboard
  ports:
  - port: 80
    targetPort: 8501
  type: LoadBalancer
```

## 🔒 Security Considerations

### Environment Variables
```bash
# Required environment variables
export OPENAI_API_KEY="your-openai-key"
export NEWS_API_KEY="your-news-api-key"
export DATABASE_URL="postgresql://user:pass@host:port/db"
export SECRET_KEY="your-secret-key"
```

### SSL/TLS Configuration
```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://trading-dashboard:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Authentication
- Implement OAuth2 for production deployments
- Use API keys for external service access
- Enable HTTPS for all production environments
- Implement rate limiting to prevent abuse

## 🎯 Deployment Recommendations

### Development Environment
- **Local Python**: Quick development and testing
- **Docker**: Consistent environment across team
- **Lightweight version**: For resource-constrained machines

### Staging Environment
- **Docker Compose**: Full stack testing
- **Cloud containers**: Production-like environment
- **Monitoring enabled**: Performance testing

### Production Environment
- **Kubernetes**: High availability and scaling
- **Cloud managed services**: Reduced operational overhead
- **Full monitoring**: Comprehensive observability
- **SSL/TLS**: Security compliance

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8501
lsof -i :8501
# Kill the process
kill -9 PID
```

#### Memory Issues
```bash
# Monitor memory usage
docker stats trading-dashboard
# Increase memory limit
docker run --memory="2g" trading-dashboard
```

#### API Rate Limits
- Implement exponential backoff
- Use multiple API keys for rotation
- Cache responses to reduce API calls

### Performance Issues
- Enable caching for frequently accessed data
- Optimize database queries
- Use CDN for static assets
- Implement lazy loading for large datasets

## 📞 Support

For deployment issues or questions:
1. Check the logs: `docker logs trading-dashboard`
2. Review the troubleshooting section
3. Check system requirements
4. Verify API key configuration

## 🔄 Updates and Maintenance

### Regular Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild Docker image
docker build -t trading-dashboard:latest .

# Rolling update (zero downtime)
docker-compose up -d --no-deps trading-dashboard
```

### Backup Strategy
- Database backups: Daily automated backups
- Configuration backups: Version controlled
- Log retention: 30 days for troubleshooting

---

**Happy Trading! 📈**

*This deployment guide ensures your Fundamental News Trading Dashboard runs efficiently across all environments, from development laptops to enterprise cloud infrastructure.*