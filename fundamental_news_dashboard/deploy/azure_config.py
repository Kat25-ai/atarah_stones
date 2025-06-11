"""
Azure Deployment Configuration
Contains deployment settings and validation functions
"""

import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Azure deployment configurations
AZURE_CONFIGS = {
    'app_service': {
        'sku_options': {
            'free': 'F1',
            'basic': 'B1',
            'standard': 'S1',
            'premium': 'P1v2'
        },
        'python_version': 'PYTHON|3.9',
        'port': 8000,
        'startup_command': 'python -m streamlit run lightweight_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false'
    },
    'container_instance': {
        'image': 'python:3.9-slim',
        'memory_gb': 2.0,
        'cpu_cores': 1.0,
        'port': 8501
    },
    'function_app': {
        'runtime': 'python',
        'version': '~4',
        'python_version': 'PYTHON|3.9'
    }
}

# Required environment variables for deployment
REQUIRED_ENV_VARS = [
    'AZURE_SUBSCRIPTION_ID',
    'AZURE_RESOURCE_GROUP',
    'AZURE_LOCATION'
]

# Optional environment variables
OPTIONAL_ENV_VARS = [
    'AZURE_CLIENT_ID',
    'AZURE_CLIENT_SECRET',
    'AZURE_TENANT_ID'
]

def validate_deployment_config(deployment_type: str) -> Dict:
    """Validate deployment configuration"""
    
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check deployment type
    if deployment_type not in AZURE_CONFIGS:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Invalid deployment type: {deployment_type}")
    
    # Check required environment variables
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Check optional environment variables
    missing_optional = []
    for var in OPTIONAL_ENV_VARS:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        validation_result['warnings'].append(f"Missing optional environment variables: {', '.join(missing_optional)}")
        validation_result['warnings'].append("Using DefaultAzureCredential for authentication")
    
    return validation_result

def get_deployment_config(deployment_type: str) -> Dict:
    """Get deployment configuration for specified type"""
    
    if deployment_type not in AZURE_CONFIGS:
        raise ValueError(f"Invalid deployment type: {deployment_type}")
    
    base_config = {
        'subscription_id': os.getenv('AZURE_SUBSCRIPTION_ID'),
        'resource_group': os.getenv('AZURE_RESOURCE_GROUP'),
        'location': os.getenv('AZURE_LOCATION', 'East US')
    }
    
    # Merge with deployment-specific config
    deployment_config = AZURE_CONFIGS[deployment_type].copy()
    deployment_config.update(base_config)
    
    return deployment_config

def create_deployment_files() -> Dict[str, str]:
    """Create all necessary deployment files"""
    
    files = {}
    
    # Startup script for App Service
    files['startup.sh'] = """#!/bin/bash
echo "Starting Fundamental News Trading Dashboard..."
echo "Python version: $(python --version)"
echo "Streamlit version: $(python -m streamlit version)"

# Install any missing dependencies
pip install --no-cache-dir -r requirements.txt

# Start the application
python -m streamlit run lightweight_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false
"""
    
    # Azure Function requirements
    files['function_requirements.txt'] = """azure-functions==1.18.0
azure-functions-worker==1.0.0
requests==2.31.0
pandas==2.1.4
numpy==1.24.3
python-dateutil==2.8.2
"""
    
    # Docker health check script
    files['healthcheck.py'] = """#!/usr/bin/env python3
import requests
import sys
import time

def check_health():
    try:
        response = requests.get('http://localhost:8501/healthz', timeout=10)
        if response.status_code == 200:
            print("Health check passed")
            return True
    except Exception as e:
        print(f"Health check failed: {e}")
    return False

if __name__ == "__main__":
    max_retries = 5
    for i in range(max_retries):
        if check_health():
            sys.exit(0)
        time.sleep(5)
    sys.exit(1)
"""
    
    # Environment template
    files['.env.template'] = """# Azure Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group
AZURE_LOCATION=East US

# Optional: Service Principal Authentication
# AZURE_CLIENT_ID=your-client-id
# AZURE_CLIENT_SECRET=your-client-secret
# AZURE_TENANT_ID=your-tenant-id

# Application Settings
APP_NAME=trading-dashboard
DEPLOYMENT_TYPE=appservice
"""
    
    return files

def print_deployment_summary(result: Dict):
    """Print deployment summary"""
    
    print("\n" + "="*60)
    print("AZURE DEPLOYMENT SUMMARY")
    print("="*60)
    
    if result['status'] == 'deployed':
        print("✅ Deployment Status: SUCCESS")
        print(f"📱 Application Name: {result.get('app_name', 'N/A')}")
        print(f"🌐 Application URL: {result.get('app_url', result.get('dashboard_url', 'N/A'))}")
        print(f"📍 Resource Group: {result.get('resource_group', 'N/A')}")
        
        if 'container_ip' in result:
            print(f"🖥️  Container IP: {result['container_ip']}")
        
        if 'storage_account' in result:
            print(f"💾 Storage Account: {result['storage_account']}")
            
    else:
        print("❌ Deployment Status: FAILED")
        print(f"💥 Error: {result.get('error', 'Unknown error')}")
    
    print("="*60)

def get_monitoring_config() -> Dict:
    """Get monitoring configuration"""
    
    return {
        'application_insights': {
            'enabled': True,
            'retention_days': 90,
            'sampling_percentage': 100
        },
        'alerts': [
            {
                'name': 'High CPU Usage',
                'metric': 'CpuPercentage',
                'threshold': 80,
                'operator': 'GreaterThan',
                'time_window': 'PT5M'
            },
            {
                'name': 'High Memory Usage',
                'metric': 'MemoryPercentage',
                'threshold': 90,
                'operator': 'GreaterThan',
                'time_window': 'PT5M'
            },
            {
                'name': 'Application Errors',
                'metric': 'Http5xx',
                'threshold': 5,
                'operator': 'GreaterThan',
                'time_window': 'PT5M'
            }
        ],
        'log_analytics': {
            'enabled': True,
            'retention_days': 30
        }
    }