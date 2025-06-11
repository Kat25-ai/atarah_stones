#!/usr/bin/env python3
"""
Comprehensive Azure Deployment Script
Handles all deployment types with proper error handling and validation
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from azure_deploy import AzureDeployer, AzureMonitoring
from azure_config import (
    validate_deployment_config, 
    get_deployment_config, 
    print_deployment_summary,
    create_deployment_files
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_deployment_environment():
    """Setup deployment environment and files"""
    
    logger.info("Setting up deployment environment...")
    
    # Create deployment files
    deployment_files = create_deployment_files()
    
    # Write files to disk
    deploy_dir = Path(__file__).parent
    for filename, content in deployment_files.items():
        file_path = deploy_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
        logger.info(f"Created deployment file: {filename}")
    
    logger.info("Deployment environment setup complete")

def deploy_application(args):
    """Deploy the application to Azure"""
    
    # Validate configuration
    logger.info("Validating deployment configuration...")
    validation = validate_deployment_config(args.deployment_type)
    
    if not validation['valid']:
        logger.error("Configuration validation failed:")
        for error in validation['errors']:
            logger.error(f"  - {error}")
        return False
    
    if validation['warnings']:
        logger.warning("Configuration warnings:")
        for warning in validation['warnings']:
            logger.warning(f"  - {warning}")
    
    # Get deployment configuration
    try:
        config = get_deployment_config(args.deployment_type)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return False
    
    # Initialize deployer
    try:
        deployer = AzureDeployer(
            subscription_id=config['subscription_id'],
            resource_group=config['resource_group'],
            location=config['location']
        )
        logger.info("Azure deployer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Azure deployer: {e}")
        return False
    
    # Deploy based on type
    logger.info(f"Starting {args.deployment_type} deployment...")
    
    try:
        if args.deployment_type == 'appservice':
            result = deployer.deploy_app_service(
                app_name=args.app_name,
                sku=args.sku or config.get('sku_options', {}).get('basic', 'B1')
            )
        elif args.deployment_type == 'container':
            result = deployer.deploy_container_instance(args.app_name)
        elif args.deployment_type == 'function':
            result = deployer.deploy_function_app(args.app_name)
        else:
            logger.error(f"Unsupported deployment type: {args.deployment_type}")
            return False
        
        # Print deployment summary
        print_deployment_summary(result)
        
        if result['status'] == 'deployed':
            # Setup monitoring if requested
            if args.enable_monitoring:
                logger.info("Setting up monitoring...")
                monitoring = AzureMonitoring(
                    config['subscription_id'], 
                    config['resource_group']
                )
                
                insights_result = monitoring.setup_application_insights(args.app_name)
                alerts_result = monitoring.setup_alerts(args.app_name)
                
                logger.info("Monitoring setup complete:")
                logger.info(f"  Application Insights: {insights_result['status']}")
                logger.info(f"  Alerts: {alerts_result['status']}")
            
            logger.info("Deployment completed successfully!")
            return True
        else:
            logger.error("Deployment failed!")
            return False
            
    except Exception as e:
        logger.error(f"Deployment failed with exception: {e}")
        return False

def main():
    """Main deployment function"""
    
    parser = argparse.ArgumentParser(
        description='Deploy Fundamental News Trading Dashboard to Azure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy as App Service (recommended)
  python deploy.py --deployment-type appservice --app-name my-trading-dashboard

  # Deploy as Container Instance
  python deploy.py --deployment-type container --app-name my-dashboard-container

  # Deploy as Function App
  python deploy.py --deployment-type function --app-name my-dashboard-function

  # Deploy with monitoring enabled
  python deploy.py --deployment-type appservice --app-name my-dashboard --enable-monitoring

Environment Variables Required:
  AZURE_SUBSCRIPTION_ID - Your Azure subscription ID
  AZURE_RESOURCE_GROUP - Target resource group name
  AZURE_LOCATION - Azure region (default: East US)

Optional Environment Variables:
  AZURE_CLIENT_ID - Service principal client ID
  AZURE_CLIENT_SECRET - Service principal secret
  AZURE_TENANT_ID - Azure tenant ID
        """
    )
    
    parser.add_argument(
        '--deployment-type',
        choices=['appservice', 'container', 'function'],
        required=True,
        help='Type of Azure deployment'
    )
    
    parser.add_argument(
        '--app-name',
        required=True,
        help='Name for the deployed application'
    )
    
    parser.add_argument(
        '--sku',
        choices=['F1', 'B1', 'S1', 'P1v2'],
        help='App Service SKU (only for appservice deployment)'
    )
    
    parser.add_argument(
        '--enable-monitoring',
        action='store_true',
        help='Enable Application Insights monitoring'
    )
    
    parser.add_argument(
        '--setup-only',
        action='store_true',
        help='Only setup deployment files, do not deploy'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Setup deployment environment
    setup_deployment_environment()
    
    # If setup-only, exit here
    if args.setup_only:
        logger.info("Setup complete. Deployment files created.")
        return 0
    
    # Check required environment variables
    required_vars = ['AZURE_SUBSCRIPTION_ID', 'AZURE_RESOURCE_GROUP']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error("Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        logger.error("\nPlease set these environment variables and try again.")
        logger.error("See --help for more information.")
        return 1
    
    # Deploy application
    success = deploy_application(args)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())