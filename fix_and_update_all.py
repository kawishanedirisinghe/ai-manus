#!/usr/bin/env python3
"""
Comprehensive Fix and Update Script for AI Manus Project
Addresses Docker Compose, Python dependencies, and environment setup
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print script header"""
    print("🚀 AI Manus - Comprehensive Fix and Update Script")
    print("=" * 60)
    print("🔧 Fixing Docker Compose, Python dependencies, and environment")
    print()

def run_command(cmd, description="", check=True, shell=True):
    """Run a command with error handling"""
    print(f"📋 {description}")
    print(f"   Command: {cmd}")
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"   ❌ Failed (exit code: {result.returncode})")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            if check:
                return False
        return True
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        if check:
            return False
        return True

def check_docker_compose():
    """Check and fix Docker Compose availability"""
    print("\n🐳 Checking Docker Compose...")
    
    # Check for docker compose (new command)
    if run_command("docker compose version", "Checking 'docker compose'", check=False):
        print("   ✅ 'docker compose' is available")
        return "docker compose"
    
    # Check for docker-compose (legacy command)
    if run_command("docker-compose --version", "Checking 'docker-compose'", check=False):
        print("   ✅ 'docker-compose' is available")
        return "docker-compose"
    
    print("   ⚠️ Neither 'docker compose' nor 'docker-compose' found")
    return None

def fix_python_dependencies():
    """Fix Python dependency installation issues"""
    print("\n🐍 Fixing Python Dependencies...")
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("   📦 Virtual environment not found, creating...")
        if not run_command("python3 -m venv venv", "Creating virtual environment"):
            return False
    
    # Activate venv and install dependencies
    activate_cmd = "source venv/bin/activate"
    
    # Upgrade pip
    if not run_command(f"{activate_cmd} && pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{activate_cmd} && pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def create_docker_wrapper():
    """Create a wrapper script for Docker commands if needed"""
    print("\n🔧 Creating Docker wrapper...")
    
    wrapper_content = '''#!/bin/bash
# Docker wrapper script to handle permissions

if command -v docker >/dev/null 2>&1; then
    sudo docker "$@"
else
    echo "Docker not found!"
    exit 1
fi
'''
    
    wrapper_path = Path("docker_wrapper.sh")
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_content)
    
    os.chmod(wrapper_path, 0o755)
    print("   ✅ Docker wrapper created")

def update_environment():
    """Update and verify environment setup"""
    print("\n🔄 Updating Environment...")
    
    # Check Python version
    result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ Python: {result.stdout.strip()}")
    
    # Check if venv is activated
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   ✅ Virtual environment is active")
    else:
        print("   ⚠️ Virtual environment not active - run 'source venv/bin/activate'")
    
    # Check key packages
    key_packages = ['requests', 'aiohttp', 'python-dotenv', 'rich']
    for package in key_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package} is available")
        except ImportError:
            print(f"   ❌ {package} not found")

def create_setup_script():
    """Create a setup script for easy environment initialization"""
    print("\n📝 Creating setup script...")
    
    setup_content = '''#!/bin/bash
# AI Manus Setup Script

echo "🚀 AI Manus Environment Setup"
echo "============================"

# Activate virtual environment
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run fix_and_update_all.py first."
    exit 1
fi

# Check if Docker is available
if command -v docker >/dev/null 2>&1; then
    echo "🐳 Docker is available"
    
    # Try to check Docker daemon
    if sudo docker ps >/dev/null 2>&1; then
        echo "✅ Docker daemon is running"
    else
        echo "⚠️ Docker daemon may not be running"
    fi
    
    # Check Docker Compose
    if docker compose version >/dev/null 2>&1; then
        echo "✅ docker compose is available"
    elif docker-compose --version >/dev/null 2>&1; then
        echo "✅ docker-compose is available"
    else
        echo "❌ Neither docker compose nor docker-compose found"
    fi
else
    echo "❌ Docker not found"
fi

echo ""
echo "🎯 Environment ready! You can now run your applications."
echo "📋 Common commands:"
echo "   • python main.py           - Run main application"
echo "   • sudo docker compose up  - Start Docker services"
echo "   • python setup_and_run.py - Run setup and start"
'''
    
    setup_path = Path("setup_environment.sh")
    with open(setup_path, 'w') as f:
        f.write(setup_content)
    
    os.chmod(setup_path, 0o755)
    print("   ✅ Setup script created: setup_environment.sh")

def main():
    """Main function"""
    print_header()
    
    # Change to workspace directory
    os.chdir('/workspace')
    
    success = True
    
    # Check Docker Compose
    docker_compose_cmd = check_docker_compose()
    if not docker_compose_cmd:
        print("   ⚠️ Docker Compose issues detected but continuing...")
    
    # Fix Python dependencies
    if not fix_python_dependencies():
        print("   ❌ Failed to fix Python dependencies")
        success = False
    
    # Create Docker wrapper
    create_docker_wrapper()
    
    # Update environment
    update_environment()
    
    # Create setup script
    create_setup_script()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All fixes completed successfully!")
        print("📋 Next steps:")
        print("   1. Run: source venv/bin/activate")
        print("   2. Test: python --version")
        print("   3. For Docker: sudo docker ps")
        print("   4. Or use: ./setup_environment.sh")
    else:
        print("⚠️ Some issues remain - check the output above")
    
    print("=" * 60)

if __name__ == "__main__":
    main()