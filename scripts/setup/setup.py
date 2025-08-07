#!/usr/bin/env python3
"""
Simple Setup Script for Multi-API Manager
Run: python setup.py
"""

import subprocess
import sys
import os
from pathlib import Path

def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════╗
║           🚀 Multi-API Manager Setup Script              ║
║                                                          ║
║  This script will set up everything you need to use     ║
║  the Multi-API Key Manager with automatic rotation,     ║
║  usage tracking, and fallback support.                  ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_packages():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Install packages from requirements.txt
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        
        print("✅ All packages installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        print("💡 Try running manually: pip install -r requirements.txt")
        return False

def create_config_files():
    """Create necessary configuration files"""
    print("\n⚙️ Creating configuration files...")
    
    # Check if multi_api_manager.py exists
    if not Path("multi_api_manager.py").exists():
        print("❌ multi_api_manager.py not found!")
        return False
    
    # Import and initialize the API manager to create config
    try:
        from multi_api_manager import MultiAPIManager
        manager = MultiAPIManager()
        print("✅ API configuration file created!")
        return True
    except Exception as e:
        print(f"❌ Error creating config: {e}")
        return False

def show_next_steps():
    """Show user what to do next"""
    print("""
🎉 Setup Complete!

📋 Next Steps:
1. Edit 'api_config.json' and add your real API keys
2. Run 'python main.py' to start using the system
3. Use the interactive menu to chat with AI or manage keys

📝 Example API Keys Format:
   - OpenAI: sk-proj-xxxxxxxxxx
   - Anthropic: sk-ant-xxxxxxxxxx  
   - Google: AIzaxxxxxxxxxx
   - DeepSeek: sk-xxxxxxxxxx

🚀 Quick Start Commands:
   python main.py                    # Start interactive interface
   python multi_api_manager.py       # Test the API manager

📖 For help, choose option 7 in the main menu.

Happy coding! 🎯
""")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install packages
    if not install_packages():
        print("\n❌ Setup failed during package installation.")
        sys.exit(1)
    
    # Create config files
    if not create_config_files():
        print("\n❌ Setup failed during configuration creation.")
        sys.exit(1)
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()