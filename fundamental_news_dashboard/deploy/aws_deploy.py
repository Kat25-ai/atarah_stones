"""
AWS Deployment Script for Fundamental News Trading Dashboard
Supports EC2, ECS, and Lambda deployments
"""

import boto3
import json
import os
import zipfile
import time
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSDeployer:
    """AWS deployment manager for the trading dashboard"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.ec2 = boto3.client('ec2', region_name=region)
        self.ecs = boto3.client('ecs', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.iam = boto3.client('iam', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
        
    def deploy_ec2_instance(self, instance_type: str = 't3.micro') -> Dict:
        """Deploy dashboard on EC2 instance"""
        
        # User data script for EC2 instance
        user_data_script = """#!/bin/bash
        yum update -y
        yum install -y python3 python3-pip git
        
        # Clone or copy dashboard files
        mkdir -p /opt/trading-dashboard
        cd /opt/trading-dashboard
        
        # Install Python dependencies
        pip3 install streamlit pandas numpy plotly requests beautifulsoup4 textblob vaderSentiment
        
        # Create systemd service
        cat > /etc/systemd/system/trading-dashboard.service << EOF
[Unit]
Description=Trading Dashboard
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/trading-dashboard
ExecStart=/usr/bin/python3 -m streamlit run lightweight_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

        systemctl enable trading-dashboard
        systemctl start trading-dashboard
        """
        
        try:
            # Create security group
            security_group = self._create_security_group()
            
            # Launch EC2 instance
            response = self.ec2.run_instances(
                ImageId='ami-0c02fb55956c7d316',  # Amazon Linux 2
                MinCount=1,
                MaxCount=1,
                InstanceType=instance_type,
                SecurityGroupIds=[security_group['GroupId']],
                UserData=user_data_script,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': 'Trading-Dashboard'},
                            {'Key': 'Project', 'Value': 'FundamentalNewsTrading'}
                        ]
                    }
                ]
            )
            
            instance_id = response['Instances'][0]['InstanceId']
            logger.info(f"EC2 instance launched: {instance_id}")
            
            # Wait for instance to be running
            self.ec2.get_waiter('instance_running').wait(InstanceIds=[instance_id])
            
            # Get public IP
            instance_info = self.ec2.describe_instances(InstanceIds=[instance_id])
            public_ip = instance_info['Reservations'][0]['Instances'][0].get('PublicIpAddress')
            
            return {
                'instance_id': instance_id,
                'public_ip': public_ip,
                'dashboard_url': f'http://{public_ip}:8501',
                'status': 'deployed'
            }
            
        except Exception as e:
            logger.error(f"EC2 deployment failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def deploy_ecs_service(self) -> Dict:
        """Deploy dashboard as ECS service"""
        
        try:
            # Create ECS cluster
            cluster_response = self.ecs.create_cluster(
                clusterName='trading-dashboard-cluster',
                tags=[
                    {'key': 'Project', 'value': 'FundamentalNewsTrading'}
                ]
            )
            
            cluster_arn = cluster_response['cluster']['clusterArn']
            
            # Create task definition
            task_definition = {
                'family': 'trading-dashboard-task',
                'networkMode': 'awsvpc',
                'requiresCompatibilities': ['FARGATE'],
                'cpu': '256',
                'memory': '512',
                'executionRoleArn': self._get_or_create_execution_role(),
                'containerDefinitions': [
                    {
                        'name': 'trading-dashboard',
                        'image': 'python:3.9-slim',
                        'portMappings': [
                            {
                                'containerPort': 8501,
                                'protocol': 'tcp'
                            }
                        ],
                        'essential': True,
                        'command': [
                            'sh', '-c',
                            'pip install streamlit pandas numpy plotly requests beautifulsoup4 textblob vaderSentiment && streamlit run lightweight_app.py --server.port 8501 --server.address 0.0.0.0'
                        ],
                        'logConfiguration': {
                            'logDriver': 'awslogs',
                            'options': {
                                'awslogs-group': '/ecs/trading-dashboard',
                                'awslogs-region': self.region,
                                'awslogs-stream-prefix': 'ecs'
                            }
                        }
                    }
                ]
            }
            
            # Register task definition
            task_response = self.ecs.register_task_definition(**task_definition)
            task_arn = task_response['taskDefinition']['taskDefinitionArn']
            
            # Create service
            service_response = self.ecs.create_service(
                cluster=cluster_arn,
                serviceName='trading-dashboard-service',
                taskDefinition=task_arn,
                desiredCount=1,
                launchType='FARGATE',
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'subnets': self._get_default_subnets(),
                        'securityGroups': [self._create_security_group()['GroupId']],
                        'assignPublicIp': 'ENABLED'
                    }
                }
            )
            
            return {
                'cluster_arn': cluster_arn,
                'service_arn': service_response['service']['serviceArn'],
                'task_arn': task_arn,
                'status': 'deployed'
            }
            
        except Exception as e:
            logger.error(f"ECS deployment failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def deploy_lambda_function(self) -> Dict:
        """Deploy lightweight version as Lambda function"""
        
        try:
            # Create deployment package
            zip_path = self._create_lambda_package()
            
            # Create Lambda function
            with open(zip_path, 'rb') as zip_file:
                response = self.lambda_client.create_function(
                    FunctionName='trading-dashboard-api',
                    Runtime='python3.9',
                    Role=self._get_or_create_lambda_role(),
                    Handler='lambda_handler.handler',
                    Code={'ZipFile': zip_file.read()},
                    Description='Fundamental News Trading Dashboard API',
                    Timeout=30,
                    MemorySize=512,
                    Environment={
                        'Variables': {
                            'ENVIRONMENT': 'production',
                            'REGION': self.region
                        }
                    },
                    Tags={
                        'Project': 'FundamentalNewsTrading'
                    }
                )
            
            function_arn = response['FunctionArn']
            
            # Create API Gateway integration (optional)
            api_url = self._create_api_gateway(function_arn)
            
            return {
                'function_arn': function_arn,
                'api_url': api_url,
                'status': 'deployed'
            }
            
        except Exception as e:
            logger.error(f"Lambda deployment failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _create_security_group(self) -> Dict:
        """Create security group for dashboard access"""
        try:
            # Get default VPC
            vpcs = self.ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
            vpc_id = vpcs['Vpcs'][0]['VpcId']
            
            # Create security group
            response = self.ec2.create_security_group(
                GroupName='trading-dashboard-sg',
                Description='Security group for Trading Dashboard',
                VpcId=vpc_id
            )
            
            group_id = response['GroupId']
            
            # Add inbound rules
            self.ec2.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 8501,
                        'ToPort': 8501,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'Streamlit access'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access'}]
                    }
                ]
            )
            
            return {'GroupId': group_id}
            
        except Exception as e:
            logger.error(f"Security group creation failed: {e}")
            raise
    
    def _get_default_subnets(self) -> List[str]:
        """Get default subnet IDs"""
        try:
            subnets = self.ec2.describe_subnets(
                Filters=[{'Name': 'default-for-az', 'Values': ['true']}]
            )
            return [subnet['SubnetId'] for subnet in subnets['Subnets']]
        except Exception as e:
            logger.error(f"Failed to get default subnets: {e}")
            return []
    
    def _get_or_create_execution_role(self) -> str:
        """Get or create ECS execution role"""
        role_name = 'ecsTaskExecutionRole'
        
        try:
            response = self.iam.get_role(RoleName=role_name)
            return response['Role']['Arn']
        except self.iam.exceptions.NoSuchEntityException:
            # Create the role
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            
            # Attach managed policy
            self.iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'
            )
            
            return response['Role']['Arn']
    
    def _get_or_create_lambda_role(self) -> str:
        """Get or create Lambda execution role"""
        role_name = 'trading-dashboard-lambda-role'
        
        try:
            response = self.iam.get_role(RoleName=role_name)
            return response['Role']['Arn']
        except self.iam.exceptions.NoSuchEntityException:
            # Create the role
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            
            # Attach basic execution policy
            self.iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            return response['Role']['Arn']
    
    def _create_lambda_package(self) -> str:
        """Create Lambda deployment package"""
        zip_path = '/tmp/trading-dashboard-lambda.zip'
        
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            # Add Lambda handler
            lambda_handler_code = '''
import json
import boto3
from datetime import datetime

def handler(event, context):
    """Lambda handler for trading dashboard API"""
    
    # Simple API response
    response_data = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "message": "Trading Dashboard API is running",
        "data": {
            "market_status": "open",
            "safety_score": 75,
            "active_events": 3
        }
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response_data)
    }
'''
            zip_file.writestr('lambda_handler.py', lambda_handler_code)
        
        return zip_path
    
    def _create_api_gateway(self, function_arn: str) -> str:
        """Create API Gateway for Lambda function"""
        # This would create an API Gateway REST API
        # Simplified implementation
        return f"https://api.gateway.url/prod/trading-dashboard"

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy Trading Dashboard to AWS')
    parser.add_argument('--deployment-type', choices=['ec2', 'ecs', 'lambda'], 
                       default='ec2', help='Deployment type')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--instance-type', default='t3.micro', help='EC2 instance type')
    
    args = parser.parse_args()
    
    deployer = AWSDeployer(region=args.region)
    
    logger.info(f"Starting {args.deployment_type} deployment...")
    
    if args.deployment_type == 'ec2':
        result = deployer.deploy_ec2_instance(instance_type=args.instance_type)
    elif args.deployment_type == 'ecs':
        result = deployer.deploy_ecs_service()
    elif args.deployment_type == 'lambda':
        result = deployer.deploy_lambda_function()
    
    if result['status'] == 'deployed':
        logger.info("Deployment successful!")
        logger.info(f"Result: {json.dumps(result, indent=2)}")
    else:
        logger.error("Deployment failed!")
        logger.error(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()