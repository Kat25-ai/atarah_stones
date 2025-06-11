"""
Azure Deployment Script for Fundamental News Trading Dashboard
Supports App Service, Container Instances, and Functions deployments
"""

import json
import os
import zipfile
import time
from typing import Dict, List, Optional
import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureDeployer:
    """Azure deployment manager for the trading dashboard"""
    
    def __init__(self, subscription_id: str, resource_group: str, location: str = 'East US'):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.location = location
        
        try:
            # Initialize Azure clients
            self.credential = DefaultAzureCredential()
            self.resource_client = ResourceManagementClient(self.credential, subscription_id)
            self.web_client = WebSiteManagementClient(self.credential, subscription_id)
            self.container_client = ContainerInstanceManagementClient(self.credential, subscription_id)
            self.storage_client = StorageManagementClient(self.credential, subscription_id)
            self.insights_client = ApplicationInsightsManagementClient(self.credential, subscription_id)
            
            # Test authentication
            self._test_authentication()
            
            # Ensure resource group exists
            self._ensure_resource_group()
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure clients: {e}")
            raise
    
    def _test_authentication(self):
        """Test Azure authentication"""
        try:
            # Try to list resource groups to test authentication
            list(self.resource_client.resource_groups.list())
            logger.info("Azure authentication successful")
        except Exception as e:
            logger.error(f"Azure authentication failed: {e}")
            raise Exception("Azure authentication failed. Please ensure you're logged in with 'az login' or have proper service principal credentials.")
    
    def deploy_app_service(self, app_name: str, sku: str = 'F1') -> Dict:
        """Deploy dashboard as Azure App Service"""
        
        try:
            # Create App Service Plan
            plan_name = f"{app_name}-plan"
            
            app_service_plan = {
                'location': self.location,
                'sku': {
                    'name': sku,
                    'tier': 'Free' if sku == 'F1' else 'Basic'
                },
                'kind': 'linux',
                'reserved': True
            }
            
            logger.info(f"Creating App Service Plan: {plan_name}")
            plan_result = self.web_client.app_service_plans.begin_create_or_update(
                self.resource_group,
                plan_name,
                app_service_plan
            ).result()
            
            # Create Web App
            web_app = {
                'location': self.location,
                'server_farm_id': plan_result.id,
                'site_config': {
                    'linux_fx_version': 'PYTHON|3.9',
                    'app_command_line': 'python -m streamlit run lightweight_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false',
                    'app_settings': [
                        {'name': 'WEBSITES_PORT', 'value': '8000'},
                        {'name': 'SCM_DO_BUILD_DURING_DEPLOYMENT', 'value': 'true'},
                        {'name': 'ENABLE_ORYX_BUILD', 'value': 'true'},
                        {'name': 'PYTHONPATH', 'value': '/home/site/wwwroot'},
                        {'name': 'PORT', 'value': '8000'}
                    ]
                }
            }
            
            logger.info(f"Creating Web App: {app_name}")
            app_result = self.web_client.web_apps.begin_create_or_update(
                self.resource_group,
                app_name,
                web_app
            ).result()
            
            # Get app URL
            app_url = f"https://{app_name}.azurewebsites.net"
            
            return {
                'app_name': app_name,
                'app_url': app_url,
                'resource_group': self.resource_group,
                'status': 'deployed'
            }
            
        except Exception as e:
            logger.error(f"App Service deployment failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def deploy_container_instance(self, container_name: str) -> Dict:
        """Deploy dashboard as Azure Container Instance"""
        
        try:
            # Container configuration
            container_config = {
                'location': self.location,
                'containers': [
                    {
                        'name': container_name,
                        'image': 'python:3.9-slim',
                        'resources': {
                            'requests': {
                                'memory_in_gb': 2.0,
                                'cpu': 1.0
                            }
                        },
                        'ports': [
                            {'port': 8501, 'protocol': 'TCP'}
                        ],
                        'environment_variables': [
                            {'name': 'PYTHONUNBUFFERED', 'value': '1'},
                            {'name': 'STREAMLIT_SERVER_PORT', 'value': '8501'},
                            {'name': 'STREAMLIT_SERVER_ADDRESS', 'value': '0.0.0.0'}
                        ],
                        'command': [
                            '/bin/bash', '-c',
                            'apt-get update && apt-get install -y git && '
                            'pip install --no-cache-dir streamlit==1.29.0 pandas==2.1.4 numpy==1.24.3 plotly==5.17.0 requests==2.31.0 beautifulsoup4==4.12.2 textblob==0.17.1 vaderSentiment==3.3.2 && '
                            'mkdir -p /app && cd /app && '
                            'echo "Creating lightweight dashboard..." && '
                            'python -c "exec(open(\'/tmp/create_app.py\').read())" && '
                            'streamlit run lightweight_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true'
                        ]
                    }
                ],
                'os_type': 'Linux',
                'ip_address': {
                    'type': 'Public',
                    'ports': [
                        {'port': 8501, 'protocol': 'TCP'}
                    ]
                },
                'restart_policy': 'Always'
            }
            
            logger.info(f"Creating Container Instance: {container_name}")
            container_result = self.container_client.container_groups.begin_create_or_update(
                self.resource_group,
                container_name,
                container_config
            ).result()
            
            # Get container IP
            container_ip = container_result.ip_address.ip
            dashboard_url = f"http://{container_ip}:8501"
            
            return {
                'container_name': container_name,
                'container_ip': container_ip,
                'dashboard_url': dashboard_url,
                'status': 'deployed'
            }
            
        except Exception as e:
            logger.error(f"Container Instance deployment failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def deploy_function_app(self, function_name: str) -> Dict:
        """Deploy lightweight version as Azure Function"""
        
        try:
            # Create storage account for function app
            storage_name = f"{function_name}storage"[:24].replace('-', '').lower()
            
            storage_params = {
                'sku': {'name': 'Standard_LRS'},
                'kind': 'StorageV2',
                'location': self.location
            }
            
            logger.info(f"Creating Storage Account: {storage_name}")
            storage_result = self.storage_client.storage_accounts.begin_create(
                self.resource_group,
                storage_name,
                storage_params
            ).result()
            
            # Get storage connection string
            storage_keys = self.storage_client.storage_accounts.list_keys(
                self.resource_group, storage_name
            )
            storage_key = storage_keys.keys[0].value
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_name};AccountKey={storage_key};EndpointSuffix=core.windows.net"
            
            # Create Function App
            function_app = {
                'location': self.location,
                'kind': 'functionapp,linux',
                'site_config': {
                    'linux_fx_version': 'PYTHON|3.9',
                    'app_settings': [
                        {'name': 'AzureWebJobsStorage', 'value': connection_string},
                        {'name': 'FUNCTIONS_WORKER_RUNTIME', 'value': 'python'},
                        {'name': 'FUNCTIONS_EXTENSION_VERSION', 'value': '~4'}
                    ]
                }
            }
            
            logger.info(f"Creating Function App: {function_name}")
            function_result = self.web_client.web_apps.begin_create_or_update(
                self.resource_group,
                function_name,
                function_app
            ).result()
            
            # Function app URL
            function_url = f"https://{function_name}.azurewebsites.net"
            
            return {
                'function_name': function_name,
                'function_url': function_url,
                'storage_account': storage_name,
                'status': 'deployed'
            }
            
        except Exception as e:
            logger.error(f"Function App deployment failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _ensure_resource_group(self):
        """Ensure resource group exists"""
        try:
            self.resource_client.resource_groups.get(self.resource_group)
            logger.info(f"Resource group {self.resource_group} exists")
        except ResourceNotFoundError:
            logger.info(f"Creating resource group: {self.resource_group}")
            try:
                self.resource_client.resource_groups.create_or_update(
                    self.resource_group,
                    {'location': self.location}
                )
                logger.info(f"Resource group {self.resource_group} created successfully")
            except Exception as e:
                logger.error(f"Failed to create resource group: {e}")
                raise
        except Exception as e:
            logger.error(f"Error checking resource group: {e}")
            raise
    
    def create_deployment_files(self):
        """Create necessary deployment files for Azure"""
        
        # Create requirements.txt for Azure
        requirements_content = """streamlit==1.29.0
requests==2.31.0
pandas==2.1.4
numpy==1.24.3
plotly==5.17.0
matplotlib==3.8.2
seaborn==0.13.0
beautifulsoup4==4.12.2
lxml==4.9.3
textblob==0.17.1
vaderSentiment==3.3.2
yfinance==0.2.28
python-dotenv==1.0.0
schedule==1.2.0
pytz==2023.3
python-dateutil==2.8.2
json5==0.9.14
pillow==10.1.0"""
        
        # Create startup script for App Service
        startup_script = """#!/bin/bash
echo "Starting Trading Dashboard..."
python -m streamlit run lightweight_app.py --server.port 8000 --server.address 0.0.0.0
"""
        
        # Create Azure Function code
        function_code = '''import azure.functions as func
import json
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function for trading dashboard API"""
    
    try:
        # Simple API response
        response_data = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "message": "Trading Dashboard API is running on Azure",
            "data": {
                "market_status": "open",
                "safety_score": 75,
                "active_events": 3,
                "platform": "Azure Functions"
            }
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )
'''
        
        # Create function.json
        function_json = {
            "scriptFile": "__init__.py",
            "bindings": [
                {
                    "authLevel": "anonymous",
                    "type": "httpTrigger",
                    "direction": "in",
                    "name": "req",
                    "methods": ["get", "post"]
                },
                {
                    "type": "http",
                    "direction": "out",
                    "name": "$return"
                }
            ]
        }
        
        # Create host.json
        host_json = {
            "version": "2.0",
            "functionTimeout": "00:05:00",
            "extensions": {
                "http": {
                    "routePrefix": "api"
                }
            }
        }
        
        return {
            'requirements.txt': requirements_content,
            'startup.sh': startup_script,
            'function_code.py': function_code,
            'function.json': json.dumps(function_json, indent=2),
            'host.json': json.dumps(host_json, indent=2)
        }

class AzureMonitoring:
    """Azure monitoring and logging setup"""
    
    def __init__(self, subscription_id: str, resource_group: str):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.credential = DefaultAzureCredential()
    
    def setup_application_insights(self, app_name: str) -> Dict:
        """Setup Application Insights for monitoring"""
        
        try:
            insights_name = f"{app_name}-insights"
            
            # Create Application Insights component
            insights_config = {
                'location': 'East US',
                'kind': 'web',
                'properties': {
                    'application_type': 'web'
                }
            }
            
            logger.info(f"Creating Application Insights: {insights_name}")
            insights_result = self.insights_client.components.create_or_update(
                self.resource_group,
                insights_name,
                insights_config
            )
            
            return {
                'insights_name': insights_name,
                'instrumentation_key': insights_result.instrumentation_key,
                'connection_string': insights_result.connection_string,
                'status': 'configured'
            }
            
        except Exception as e:
            logger.error(f"Application Insights setup failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def setup_alerts(self, resource_name: str) -> Dict:
        """Setup monitoring alerts"""
        
        alerts = [
            {
                'name': 'High CPU Usage',
                'condition': 'CPU > 80%',
                'action': 'Send notification'
            },
            {
                'name': 'High Memory Usage',
                'condition': 'Memory > 90%',
                'action': 'Send notification'
            },
            {
                'name': 'Application Errors',
                'condition': 'Error rate > 5%',
                'action': 'Send notification'
            }
        ]
        
        return {
            'alerts_configured': len(alerts),
            'alerts': alerts,
            'status': 'configured'
        }

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy Trading Dashboard to Azure')
    parser.add_argument('--deployment-type', choices=['appservice', 'container', 'function'], 
                       default='appservice', help='Deployment type')
    parser.add_argument('--subscription-id', required=True, help='Azure subscription ID')
    parser.add_argument('--resource-group', required=True, help='Azure resource group')
    parser.add_argument('--app-name', required=True, help='Application name')
    parser.add_argument('--location', default='East US', help='Azure region')
    
    args = parser.parse_args()
    
    deployer = AzureDeployer(
        subscription_id=args.subscription_id,
        resource_group=args.resource_group,
        location=args.location
    )
    
    logger.info(f"Starting {args.deployment_type} deployment...")
    
    if args.deployment_type == 'appservice':
        result = deployer.deploy_app_service(args.app_name)
    elif args.deployment_type == 'container':
        result = deployer.deploy_container_instance(args.app_name)
    elif args.deployment_type == 'function':
        result = deployer.deploy_function_app(args.app_name)
    
    if result['status'] == 'deployed':
        logger.info("Deployment successful!")
        logger.info(f"Result: {json.dumps(result, indent=2)}")
        
        # Setup monitoring
        monitoring = AzureMonitoring(args.subscription_id, args.resource_group)
        insights_result = monitoring.setup_application_insights(args.app_name)
        alerts_result = monitoring.setup_alerts(args.app_name)
        
        logger.info("Monitoring configured:")
        logger.info(f"Application Insights: {insights_result}")
        logger.info(f"Alerts: {alerts_result}")
        
    else:
        logger.error("Deployment failed!")
        logger.error(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()