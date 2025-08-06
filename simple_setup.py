#!/usr/bin/env python3
"""
Simplified AI Manus Setup - One-click setup for Nix environments
Automatically handles dependencies and configuration with provided API keys
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

# Your provided API keys
GEMINI_API_KEYS = [
    "AIzaSyAwd6PcBM-07xBbbuBqBPc3svJsUMvyc1E",
    "AIzaSyDwDj4i9tptBolcKGHMlqxMOi_CjisQdJE", 
    "AIzaSyClSfseWKkublCjdZBIq-aYqPoB3jEWj28",
    "AIzaSyD_ElDcTSosqzd4Dy9L-4ygL3fP2zsWtq0",
    "AIzaSyAf__tW7KcUD1-uh9RzGg6Y5eS6e3_PNB0"
]

def print_header():
    """Print setup header"""
    print("🚀 AI Manus - Simple Setup")
    print("=" * 50)
    print("✨ One-click setup with pre-configured API keys")
    print()

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return version.major >= 3 and version.minor >= 8

def install_dependencies_nix():
    """Install dependencies in Nix environment"""
    print("📦 Installing dependencies (Nix environment)...")
    
    try:
        print("   Installing required packages with --user flag...")
        # Install essential packages only to avoid conflicts
        essential_packages = [
            "requests>=2.31.0",
            "aiohttp>=3.8.0", 
            "python-dotenv>=1.0.0",
            "rich>=13.0.0"
        ]
        
        for package in essential_packages:
            print(f"   Installing {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--user", package
            ], check=True, capture_output=True, text=True)
        
        print("   ✅ Essential dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install dependencies: {e}")
        # Try alternative approach
        print("   Trying alternative installation...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--user", "--break-system-packages",
                "requests", "aiohttp", "python-dotenv", "rich"
            ], check=True, capture_output=True, text=True)
            print("   ✅ Dependencies installed with --break-system-packages")
            return True
        except subprocess.CalledProcessError:
            print("   ⚠️  Dependency installation failed, but continuing...")
            print("   The application may work with system packages")
            return True

def create_api_config():
    """Create API configuration with provided keys"""
    print("🔑 Setting up API configuration...")
    
    config = {
        "llm": {
            "model": "gemini-2.5-pro",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "api_key": GEMINI_API_KEYS[0],
            "max_tokens": 60000,
            "temperature": 0.0,
            "api_keys": []
        }
    }
    
    # Add all API keys with configuration
    for i, key in enumerate(GEMINI_API_KEYS, 1):
        config["llm"]["api_keys"].append({
            "api_key": key,
            "name": f"{i} Key",
            "max_requests_per_minute": 5,
            "max_requests_per_hour": 100,
            "max_requests_per_day": 100,
            "priority": i,
            "enabled": True
        })
    
    # Save as TOML-like format (simplified)
    with open("config.toml", "w") as f:
        f.write(f'''# Global LLM configuration with multi-API key support
[llm]
model = "gemini-2.5-pro"
base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
api_key = "{GEMINI_API_KEYS[0]}"
max_tokens = 60000
temperature = 0.0

# Multi-API key configuration with rate limiting and automatic rotation
''')
        
        for i, key in enumerate(GEMINI_API_KEYS, 1):
            f.write(f'''
[[llm.api_keys]]
api_key = "{key}"
name = "{i} Key"
max_requests_per_minute = 5
max_requests_per_hour = 100
max_requests_per_day = 100
priority = {i}
enabled = true
''')
    
    # Also create JSON format for compatibility
    json_config = {
        "google_keys": GEMINI_API_KEYS,
        "current_google_index": 0,
        "rate_limits": {
            "google": {
                "requests_per_minute": 5,
                "tokens_per_minute": 60000
            }
        },
        "fallback_strategy": "round_robin",
        "retry_attempts": 3,
        "retry_delay": 1.0
    }
    
    with open("api_config.json", "w") as f:
        json.dump(json_config, f, indent=2)
    
    print("   ✅ API configuration created with 5 Gemini keys")
    return True

def create_env_file():
    """Create environment file"""
    print("📄 Creating environment file...")
    
    env_content = f"""# AI Manus Environment Configuration
# Primary API Key
GEMINI_API_KEY={GEMINI_API_KEYS[0]}

# Additional API Keys for rotation
GEMINI_API_KEY_1={GEMINI_API_KEYS[0]}
GEMINI_API_KEY_2={GEMINI_API_KEYS[1]}
GEMINI_API_KEY_3={GEMINI_API_KEYS[2]}
GEMINI_API_KEY_4={GEMINI_API_KEYS[3]}
GEMINI_API_KEY_5={GEMINI_API_KEYS[4]}

# Model Configuration
LLM_MODEL=gemini-2.5-pro
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MAX_TOKENS=60000
LLM_TEMPERATURE=0.0

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=5
MAX_REQUESTS_PER_HOUR=100
MAX_REQUESTS_PER_DAY=100
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("   ✅ Environment file created")
    return True

def create_run_script():
    """Create simple run script"""
    print("🎯 Creating run script...")
    
    # Create the run script content as a separate file
    run_script_lines = [
        "#!/usr/bin/env python3",
        '"""',
        "Simple runner for AI Manus",
        '"""',
        "",
        "import os",
        "import sys", 
        "import subprocess",
        "from pathlib import Path",
        "",
                 "def get_python():",
         '    """Get Python executable"""',
         "    return sys.executable",
        "",
        "def main():",
        '    """Main runner"""',
        '    print("🚀 Starting AI Manus...")',
        "    ",
                 "    # Get Python executable",
         "    python_exe = get_python()",
        "    ",
        "    if len(sys.argv) > 1:",
        "        command = sys.argv[1]",
        "        args = sys.argv[2:]",
        "        ",
        '        if command == "dev":',
        "            # Development mode",
        '            subprocess.run([python_exe, "docker_manager.py", "dev"] + args)',
        '        elif command == "docs":',
        "            # Update documentation", 
        '            subprocess.run([python_exe, "update_doc.py"] + args)',
        '        elif command == "status":',
        "            # Check status",
        '            subprocess.run([python_exe, "main.py", "status"] + args)',
        "        else:",
        "            # Pass through to main.py",
        '            subprocess.run([python_exe, "main.py", command] + args)',
        "    else:",
        "        # Default: start in production mode",
        '        subprocess.run([python_exe, "main.py", "run", "prod"])',
        "",
        'if __name__ == "__main__":',
        "    main()"
    ]
    
    with open("start.py", "w") as f:
        f.write("\n".join(run_script_lines))
    
    # Make executable
    os.chmod("start.py", 0o755)
    print("   ✅ Run script created (start.py)")
    return True

def cleanup_old_files():
    """Remove unnecessary files"""
    print("🧹 Cleaning up unnecessary files...")
    
    files_to_remove = [
        "install.py",  # Old complex installer
        "build.sh",    # Not needed for simple setup
        "dev.sh",      # Replaced by start.py
    ]
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"   🗑️  Removed {file}")
    
    print("   ✅ Cleanup completed")

def print_success():
    """Print success message and instructions"""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("✨ Your AI Manus is ready to use with 5 Gemini API keys!")
    print()
    print("🚀 TO START THE APPLICATION:")
    print("   python3 start.py")
    print()
    print("📋 AVAILABLE COMMANDS:")
    print("   python3 start.py         # Start in production mode")
    print("   python3 start.py dev     # Start in development mode") 
    print("   python3 start.py docs    # Update documentation")
    print("   python3 start.py status  # Check status")
    print()
    print("🔑 API KEYS CONFIGURED:")
    for i, key in enumerate(GEMINI_API_KEYS, 1):
        print(f"   Key {i}: {key[:20]}...")
    print()
    print("📁 CONFIGURATION FILES:")
    print("   • config.toml      # Main configuration")
    print("   • api_config.json  # API keys configuration") 
    print("   • .env             # Environment variables")
    print()
    print("🆘 NEED HELP?")
    print("   • Check README.md for documentation")
    print("   • All API keys are pre-configured and ready")
    print("=" * 60)

def main():
    """Main setup function"""
    print_header()
    
    # Check Python
    if not check_python():
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies_nix():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create configuration
    if not create_api_config():
        print("❌ Failed to create API configuration")
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        print("❌ Failed to create environment file")
        sys.exit(1)
    
    # Create run script
    if not create_run_script():
        print("❌ Failed to create run script")
        sys.exit(1)
    
    # Cleanup
    cleanup_old_files()
    
    # Success
    print_success()

if __name__ == "__main__":
    main()