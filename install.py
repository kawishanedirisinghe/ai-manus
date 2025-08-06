#!/usr/bin/env python3
"""
Installation and Setup Script for AI Manus Python Migration
Helps users set up the environment and configure everything for Replit deployment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors"""
    print(f"🔄 {description}")
    print(f"   Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ Success")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def setup_environment():
    """Setup environment files"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("✅ Created .env from .env.example")
            print("   📝 Please edit .env with your actual API keys")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env already exists")
    
    if not os.path.exists("api_config.json"):
        if os.path.exists("api_config.json.example"):
            shutil.copy("api_config.json.example", "api_config.json")
            print("✅ Created api_config.json from example")
            print("   📝 Please edit api_config.json with your actual API keys")
        else:
            print("❌ api_config.json.example not found")
            return False
    else:
        print("✅ api_config.json already exists")
    
    return True

def setup_replit():
    """Setup Replit configuration"""
    return run_command("python docker_manager.py setup-replit", "Setting up Replit configuration")

def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    
    # Test main.py
    result = run_command("python main.py", "Testing main.py")
    if not result:
        return False
    
    # Test update_doc.py
    result = run_command("python update_doc.py --help || python update_doc.py", "Testing update_doc.py")
    if not result:
        return False
    
    # Test docker_manager.py
    result = run_command("python docker_manager.py --help || echo 'Docker manager loaded'", "Testing docker_manager.py")
    if not result:
        return False
    
    return True

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("1. 🔑 Configure your API keys:")
    print("   - Edit .env file with your API keys")
    print("   - Or edit api_config.json with your API keys")
    print("   - Or set environment variables (OPENAI_API_KEY_1, etc.)")
    print()
    print("2. 🚀 For Replit deployment:")
    print("   - Upload this project to Replit")
    print("   - Add your API keys to Replit Secrets")
    print("   - Run: python main.py run")
    print()
    print("3. 🖥️  For local development:")
    print("   - Run: python docker_manager.py dev")
    print("   - Or: python main.py run dev")
    print()
    print("📖 AVAILABLE COMMANDS:")
    print()
    print("   python main.py run [env]     - Start services")
    print("   python main.py build         - Build containers")
    print("   python main.py status        - Check status")
    print("   python main.py logs          - View logs")
    print("   python main.py stop          - Stop services")
    print("   python main.py update-docs   - Update documentation")
    print()
    print("📚 Documentation:")
    print("   - Read PYTHON_MIGRATION.md for detailed instructions")
    print("   - Check README.md for project information")
    print()
    print("🆘 Need help? Check the troubleshooting section in PYTHON_MIGRATION.md")
    print("="*60)

def main():
    """Main installation function"""
    print("🚀 AI Manus Python Migration Setup")
    print("="*40)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print("\n📦 Installing dependencies...")
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    print("\n⚙️  Setting up environment...")
    if not setup_environment():
        print("❌ Failed to setup environment")
        sys.exit(1)
    
    print("\n🌐 Setting up Replit configuration...")
    if not setup_replit():
        print("❌ Failed to setup Replit configuration")
        sys.exit(1)
    
    print("\n🧪 Testing installation...")
    if not test_installation():
        print("❌ Installation test failed")
        print("   Please check the errors above and try again")
        sys.exit(1)
    
    # Make scripts executable
    run_command("chmod +x *.py", "Making scripts executable")
    
    print_usage_instructions()

if __name__ == "__main__":
    main()