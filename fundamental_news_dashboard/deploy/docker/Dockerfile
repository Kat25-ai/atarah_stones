# Multi-stage Dockerfile for Fundamental News Trading Dashboard
FROM python:3.9-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command
CMD ["streamlit", "run", "lightweight_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]

# Production stage
FROM base as production

# Set production environment
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Copy optimized configuration
COPY deploy/docker/streamlit_config.toml /app/.streamlit/config.toml

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir pytest black flake8 mypy

# Set development environment
ENV STREAMLIT_SERVER_HEADLESS=false
ENV STREAMLIT_SERVER_ENABLE_CORS=true

# Default command for development
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]