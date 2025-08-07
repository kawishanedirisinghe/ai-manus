#!/usr/bin/env python3
"""
AI Manus - Ultimate One-Button Setup & Run
Just run this script and everything will be configured and started automatically!
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """One-button setup and run"""
    print("🚀 AI Manus - One-Button Setup & Run")
    print("=" * 50)
    
    # Check if setup is needed
    config_files = [
        Path("config.toml"),
        Path("api_config.json"), 
        Path(".env"),
        Path("start.py")
    ]
    
    setup_needed = not all(f.exists() for f in config_files)
    
    if setup_needed:
        print("🔧 First time setup needed...")
        print("   Running setup script...")
        
        try:
            result = subprocess.run([sys.executable, "simple_setup.py"], check=True)
            print("   ✅ Setup completed successfully!")
        except subprocess.CalledProcessError:
            print("   ❌ Setup failed!")
            sys.exit(1)
    else:
        print("✅ Configuration already exists, skipping setup")
    
    print("\n🚀 Starting AI Manus...")
    
    # Start the application
    try:
        subprocess.run([sys.executable, "start.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")

if __name__ == "__main__":
    main()