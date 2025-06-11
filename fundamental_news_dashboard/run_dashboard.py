#!/usr/bin/env python3
"""
Startup script for the Fundamental News Trading Dashboard
"""

import os
import sys
import subprocess
import logging
import platform
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_system_info():
    """Print system information"""
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Architecture: {platform.architecture()[0]}")
    logger.info(f"Working directory: {Path.cwd()}")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error(f"Python 3.8 or higher is required. Current version: {sys.version}")
        logger.error("Please upgrade Python and try again.")
        return False
    logger.info(f"Python version check passed: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_requirements():
    """Check if required packages are installed"""
    try:
        import streamlit
        import pandas
        import numpy
        import plotly
        import requests
        import bs4  # beautifulsoup4 imports as bs4
        logger.info("All required packages are available")
        return True
    except ImportError as e:
        logger.error(f"Missing required package: {e}")
        logger.info("Will attempt to install missing packages...")
        return False

def install_requirements():
    """Install required packages"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        logger.error("requirements.txt not found")
        logger.info("Please ensure requirements.txt exists in the same directory as this script")
        return False
    
    try:
        logger.info("Installing required packages...")
        logger.info("This may take a few minutes...")
        
        # Use --upgrade to ensure latest versions
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(requirements_file)
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            logger.info("Requirements installed successfully")
            return True
        else:
            logger.error(f"Failed to install requirements:")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Package installation timed out (5 minutes)")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install requirements: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during installation: {e}")
        return False

def check_port_available(port):
    """Check if port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def validate_dashboard_files():
    """Validate that dashboard files are properly configured"""
    app_dir = Path(__file__).parent
    issues = []
    
    # Check for app files
    full_app = app_dir / "app.py"
    lightweight_app = app_dir / "lightweight_app.py"
    
    if not full_app.exists() and not lightweight_app.exists():
        issues.append("No dashboard app files found (app.py or lightweight_app.py)")
    
    # Check requirements.txt
    requirements_file = app_dir / "requirements.txt"
    if not requirements_file.exists():
        issues.append("requirements.txt not found")
    
    # Check .env.example
    env_example = app_dir / ".env.example"
    if not env_example.exists():
        issues.append(".env.example not found (optional but recommended)")
    
    # Check config files
    config_file = app_dir / "config.py"
    if not config_file.exists():
        issues.append("config.py not found (may affect some features)")
    
    if issues:
        logger.warning("Dashboard validation issues found:")
        for issue in issues:
            logger.warning(f"  - {issue}")
        return False
    
    logger.info("Dashboard files validation passed")
    return True

def setup_environment():
    """Setup environment variables"""
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        logger.warning(".env file not found. Please copy .env.example to .env and configure your API keys")
        return False
    
    # Load environment variables from .env file
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logger.info("Environment variables loaded from .env file")
        except ImportError:
            logger.warning("python-dotenv not installed. Environment variables not loaded.")
        except Exception as e:
            logger.error(f"Failed to load environment variables: {e}")
    
    return True

def select_app_file():
    """Select which app file to run"""
    app_dir = Path(__file__).parent
    full_app = app_dir / "app.py"
    lightweight_app = app_dir / "lightweight_app.py"
    
    # Check which apps are available
    available_apps = []
    if full_app.exists():
        available_apps.append(("Full Dashboard", str(full_app)))
    if lightweight_app.exists():
        available_apps.append(("Lightweight Dashboard", str(lightweight_app)))
    
    if not available_apps:
        logger.error("No dashboard app files found (app.py or lightweight_app.py)")
        return None
    
    if len(available_apps) == 1:
        app_name, app_path = available_apps[0]
        logger.info(f"Running {app_name}: {Path(app_path).name}")
        return app_path
    
    # Multiple apps available - prefer lightweight for better performance
    logger.info("Multiple dashboard versions available:")
    for i, (name, path) in enumerate(available_apps):
        logger.info(f"  {i+1}. {name} ({Path(path).name})")
    
    # Default to lightweight if available
    for name, path in available_apps:
        if "lightweight" in name.lower():
            logger.info(f"Auto-selecting {name} for better performance")
            return path
    
    # Otherwise use the first available
    return available_apps[0][1]

def run_dashboard(app_file=None):
    """Run the Streamlit dashboard"""
    if app_file is None:
        app_file = select_app_file()
    
    if app_file is None:
        return False
    
    try:
        logger.info("Starting Fundamental News Trading Dashboard...")
        logger.info(f"Running: {Path(app_file).name}")
        logger.info("Dashboard will be available at: http://localhost:8501")
        logger.info("Press Ctrl+C to stop the dashboard")
        
        # Run Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_file),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user")
    except FileNotFoundError:
        logger.error("Streamlit not found. Please install it with: pip install streamlit")
        return False
    except Exception as e:
        logger.error(f"Failed to run dashboard: {e}")
        return False
    
    return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run the Fundamental News Trading Dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_dashboard.py                    # Auto-select best available app
  python run_dashboard.py --app full        # Run full dashboard
  python run_dashboard.py --app lightweight # Run lightweight dashboard
  python run_dashboard.py --port 8502       # Run on custom port
  python run_dashboard.py --no-install      # Skip automatic package installation
        """
    )
    
    parser.add_argument(
        '--app',
        choices=['full', 'lightweight', 'auto'],
        default='auto',
        help='Which dashboard version to run (default: auto)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8501,
        help='Port to run the dashboard on (default: 8501)'
    )
    
    parser.add_argument(
        '--no-install',
        action='store_true',
        help='Skip automatic package installation'
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
    
    logger.info("=== Fundamental News Trading Dashboard ===")
    
    # Print system information if verbose
    if args.verbose:
        print_system_info()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Validate dashboard files
    if not validate_dashboard_files():
        logger.error("Dashboard validation failed. Please check the issues above.")
        sys.exit(1)
    
    # Check and install requirements if needed
    if not args.no_install:
        if not check_requirements():
            logger.info("Installing missing requirements...")
            if not install_requirements():
                logger.error("Failed to install requirements. Use --no-install to skip this step.")
                sys.exit(1)
            # Re-check after installation
            if not check_requirements():
                logger.error("Requirements still missing after installation.")
                sys.exit(1)
    else:
        logger.info("Skipping package installation check (--no-install)")
    
    # Setup environment
    if not setup_environment():
        logger.warning("Environment setup incomplete. Some features may not work.")
    
    # Select app file based on argument
    app_file = None
    if args.app != 'auto':
        app_dir = Path(__file__).parent
        if args.app == 'full':
            app_file = str(app_dir / "app.py")
            if not Path(app_file).exists():
                logger.error("Full dashboard (app.py) not found")
                sys.exit(1)
        elif args.app == 'lightweight':
            app_file = str(app_dir / "lightweight_app.py")
            if not Path(app_file).exists():
                logger.error("Lightweight dashboard (lightweight_app.py) not found")
                sys.exit(1)
    
    # Run dashboard
    if not run_dashboard_with_port(app_file, args.port):
        sys.exit(1)

def run_dashboard_with_port(app_file=None, port=8501):
    """Run the Streamlit dashboard with custom port"""
    if app_file is None:
        app_file = select_app_file()
    
    if app_file is None:
        return False
    
    # Check if port is available
    if not check_port_available(port):
        logger.warning(f"Port {port} is already in use")
        # Try to find an available port
        for alt_port in range(port + 1, port + 10):
            if check_port_available(alt_port):
                logger.info(f"Using alternative port: {alt_port}")
                port = alt_port
                break
        else:
            logger.error(f"No available ports found in range {port}-{port+9}")
            return False
    
    try:
        logger.info("Starting Fundamental News Trading Dashboard...")
        logger.info(f"Running: {Path(app_file).name}")
        logger.info(f"Dashboard will be available at: http://localhost:{port}")
        logger.info("Press Ctrl+C to stop the dashboard")
        logger.info("")
        logger.info("Tip: If the browser doesn't open automatically, copy the URL above")
        
        # Run Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_file),
            "--server.port", str(port),
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "false"
        ])
        
    except KeyboardInterrupt:
        logger.info("\nDashboard stopped by user")
    except FileNotFoundError:
        logger.error("Streamlit not found. Please install it with: pip install streamlit")
        return False
    except Exception as e:
        logger.error(f"Failed to run dashboard: {e}")
        logger.error("Try running with --verbose for more details")
        return False
    
    return True

if __name__ == "__main__":
    main()