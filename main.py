#!/usr/bin/env python3
"""
Simple Multi-API Manager - Easy Setup and Usage
Run: python main.py
"""

import os
import sys
import subprocess
import asyncio
import json
from pathlib import Path
import importlib.util

def check_and_install_packages():
    """Check and install required packages"""
    required_packages = [
        'requests', 'aiohttp', 'openai>=1.0.0', 'anthropic>=0.7.0', 
        'google-generativeai>=0.3.0', 'python-dotenv>=1.0.0', 
        'pydantic>=2.0.0', 'rich>=13.0.0'
    ]
    
    print("🔍 Checking required packages...")
    
    missing_packages = []
    for package in required_packages:
        package_name = package.split('>=')[0].split('==')[0]
        try:
            if package_name == 'google-generativeai':
                import google.generativeai
            elif package_name == 'python-dotenv':
                import dotenv
            else:
                __import__(package_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ])
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", *missing_packages
            ])
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            print("Please run manually: pip install " + " ".join(missing_packages))
            return False
    else:
        print("✅ All required packages are already installed!")
    
    return True

def import_api_manager():
    """Import the API manager after ensuring packages are installed"""
    try:
        # Check if multi_api_manager.py exists
        if not Path("multi_api_manager.py").exists():
            print("❌ multi_api_manager.py not found!")
            return None
            
        # Import the manager
        from multi_api_manager import MultiAPIManager, chat_completion, print_usage_stats, init_api_manager
        return {
            'MultiAPIManager': MultiAPIManager,
            'chat_completion': chat_completion, 
            'print_usage_stats': print_usage_stats,
            'init_api_manager': init_api_manager
        }
    except ImportError as e:
        print(f"❌ Failed to import API manager: {e}")
        return None

def create_simple_interface():
    """Create a simple command-line interface"""
    
    print("\n" + "="*60)
    print("🚀 Multi-API Key Manager - Simple Interface")
    print("="*60)
    
    # Import API manager components
    api_components = import_api_manager()
    if not api_components:
        return
    
    chat_completion = api_components['chat_completion']
    print_usage_stats = api_components['print_usage_stats']
    init_api_manager = api_components['init_api_manager']
    
    while True:
        print("\n📋 Available Commands:")
        print("1. 💬 Chat with AI")
        print("2. 📊 Show Usage Statistics") 
        print("3. ⚙️  Manage API Keys")
        print("4. 🧪 Test All Providers")
        print("5. 🏃 Run Backend Server")
        print("6. 🌐 Run Frontend Server") 
        print("7. 📖 Documentation")
        print("0. 🚪 Exit")
        
        try:
            choice = input("\n👉 Enter your choice (0-7): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
                
            elif choice == "1":
                asyncio.run(handle_chat(chat_completion))
                
            elif choice == "2":
                print_usage_stats()
                
            elif choice == "3":
                handle_key_management(init_api_manager())
                
            elif choice == "4":
                asyncio.run(test_all_providers(chat_completion))
                
            elif choice == "5":
                run_backend_server()
                
            elif choice == "6":
                run_frontend_server()
                
            elif choice == "7":
                show_documentation()
                
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def handle_chat(chat_completion):
    """Handle chat interface"""
    print("\n💬 Chat with AI")
    print("Available providers: openai, anthropic, google, deepseek")
    
    provider = input("👉 Choose provider (or press Enter for 'openai'): ").strip() or 'openai'
    
    if provider not in ['openai', 'anthropic', 'google', 'deepseek']:
        print("❌ Invalid provider!")
        return
    
    while True:
        try:
            user_input = input(f"\n[{provider}] You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                break
                
            if not user_input:
                continue
                
            print(f"[{provider}] AI: Thinking...")
            response = await chat_completion(user_input, provider=provider)
            print(f"[{provider}] AI: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def handle_key_management(manager):
    """Handle API key management"""
    print("\n⚙️ API Key Management")
    
    while True:
        print("\n1. 📋 List all keys")
        print("2. ➕ Add new key") 
        print("3. ❌ Remove key")
        print("4. 🔄 Toggle key status")
        print("0. 🔙 Back to main menu")
        
        choice = input("\n👉 Enter your choice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            stats = manager.get_usage_stats()
            print("\n📋 Current API Keys:")
            for provider, provider_stats in stats.items():
                print(f"\n🔑 {provider.upper()}:")
                for key_info in provider_stats['keys']:
                    status = "✅ Active" if key_info['is_active'] else "❌ Inactive"
                    print(f"  {key_info['key_suffix']}: {status} - {key_info['usage']}/{key_info['limit']} requests")
                    
        elif choice == "2":
            provider = input("👉 Provider (openai/anthropic/google/deepseek): ").strip()
            key = input("👉 API Key: ").strip()
            daily_limit = input("👉 Daily limit (default 1000): ").strip() or "1000"
            
            try:
                manager.add_api_key(provider, key, daily_limit=int(daily_limit))
                print("✅ API key added successfully!")
            except Exception as e:
                print(f"❌ Error adding key: {e}")
                
        elif choice == "3":
            provider = input("👉 Provider: ").strip()
            key_suffix = input("👉 Key suffix (last 8 characters): ").strip()
            
            if manager.remove_api_key(provider, key_suffix):
                print("✅ API key removed successfully!")
            else:
                print("❌ Key not found!")
                
        elif choice == "4":
            provider = input("👉 Provider: ").strip()
            key_suffix = input("👉 Key suffix: ").strip()
            
            if manager.toggle_key_status(provider, key_suffix):
                print("✅ Key status toggled successfully!")
            else:
                print("❌ Key not found!")

async def test_all_providers(chat_completion):
    """Test all available providers"""
    print("\n🧪 Testing All Providers")
    test_prompt = "Hello! Please respond with a short greeting."
    
    providers = ['openai', 'anthropic', 'google', 'deepseek']
    
    for provider in providers:
        print(f"\n🔍 Testing {provider.upper()}...")
        try:
            response = await chat_completion(test_prompt, provider=provider)
            print(f"✅ {provider}: {response[:100]}...")
        except Exception as e:
            print(f"❌ {provider}: Failed - {e}")

def run_backend_server():
    """Run the backend server"""
    print("\n🏃 Starting Backend Server...")
    try:
        if Path("backend").exists():
            os.chdir("backend")
            subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
        else:
            print("❌ Backend directory not found!")
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped.")
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")

def run_frontend_server():
    """Run the frontend server"""
    print("\n🌐 Starting Frontend Server...")
    try:
        if Path("frontend").exists():
            os.chdir("frontend")
            subprocess.run(["npm", "run", "dev"])
        else:
            print("❌ Frontend directory not found!")
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped.")
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")

def show_documentation():
    """Show documentation"""
    docs = """
📖 Multi-API Key Manager Documentation

🔧 Configuration:
- API keys are stored in 'api_config.json'
- Edit this file to add your real API keys
- Supports OpenAI, Anthropic, Google, and DeepSeek

⚙️ Features:
- Automatic key rotation
- Daily usage limits
- Usage statistics tracking
- Rate limiting
- Fallback strategies

🚀 Quick Start:
1. Run 'python main.py'
2. Edit 'api_config.json' with your API keys
3. Use the chat interface or manage keys

📊 Usage Tracking:
- Daily limits per key
- Automatic reset at midnight
- Usage statistics and logs

🔄 Key Rotation Strategies:
- round_robin: Rotate keys evenly
- priority: Use high-priority keys first  
- usage_based: Use least-used keys first

📁 File Structure:
- main.py: Main interface
- multi_api_manager.py: API management
- api_config.json: Configuration file
- api_usage.log: Usage logs
- usage_stats.json: Statistics
"""
    print(docs)

def main():
    """Main entry point"""
    print("🚀 Multi-API Key Manager - Starting Setup...")
    
    # Check and install packages
    if not check_and_install_packages():
        sys.exit(1)
    
    # Create simple interface
    create_simple_interface()

if __name__ == "__main__":
    main()
