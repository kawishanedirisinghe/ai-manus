#!/usr/bin/env python3
"""
AI Manus - Unified Interactive Main Entry Point
Run: python3 main.py
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any
import json

def print_banner():
    """Print AI Manus banner"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                    🤖 AI Manus                          ║
║           General-purpose AI Agent System               ║
║                                                          ║
║          Simple Setup • Easy Use • All-in-One          ║
╚══════════════════════════════════════════════════════════╝
""")

def print_loading(message: str, duration: int = 3):
    """Print loading animation"""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    for i in range(duration * 10):
        print(f"\r{chars[i % len(chars)]} {message}", end="", flush=True)
        time.sleep(0.1)
    print(f"\r✅ {message} - Complete!")

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
        # Check if requirements.txt exists
        if not Path("requirements.txt").exists():
            print("❌ requirements.txt not found!")
            return False
            
        # Upgrade pip first
        print("   Upgrading pip...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Install packages from requirements.txt
        print("   Installing packages (this may take a few minutes)...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All packages installed successfully!")
            return True
        else:
            print(f"❌ Failed to install packages:")
            print(result.stderr)
            return False
        
    except Exception as e:
        print(f"❌ Failed to install packages: {e}")
        print("💡 Try running manually: pip install -r requirements.txt")
        return False

def setup_system():
    """Complete system setup"""
    print("\n🚀 Setting up AI Manus system...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install packages
    if not install_packages():
        return False
    
    # Create config if needed
    try:
        from tools.multi_api_manager import MultiAPIManager
        manager = MultiAPIManager()
        print("✅ API configuration file created!")
    except Exception as e:
        print(f"⚠️  API config creation skipped: {e}")
    
    print("""
🎉 Setup Complete!

📋 Next Steps:
1. Edit 'api_config.json' and add your real API keys (optional)
2. Select an option from the menu below to start using the system

📝 Example API Keys Format:
   - OpenAI: sk-proj-xxxxxxxxxx
   - Anthropic: sk-ant-xxxxxxxxxx  
   - Google: AIzaxxxxxxxxxx
   - DeepSeek: sk-xxxxxxxxxx

Ready to use! 🎯
""")
    return True

def start_backend():
    """Start the backend service"""
    print("\n🔧 Starting Backend API Service...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found.")
        return None
        
    try:
        # Change to backend directory and start uvicorn
        os.chdir(backend_dir)
        print("   Backend starting on: http://localhost:8000")
        print("   API docs available at: http://localhost:8000/docs")
        print("   Press Ctrl+C to stop the backend")
        
        # Start the backend server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
    finally:
        # Return to root directory
        os.chdir(Path(__file__).parent)

def start_frontend():
    """Start the frontend development server"""
    print("\n🎨 Starting Frontend Development Server...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found.")
        return None
        
    try:
        # Change to frontend directory
        os.chdir(frontend_dir)
        
        # Check if node_modules exists, if not install dependencies
        if not Path("node_modules").exists():
            print("   Installing frontend dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        print("   Frontend starting on: http://localhost:3000")
        print("   Press Ctrl+C to stop the frontend")
        
        # Start the frontend dev server
        subprocess.run(["npm", "run", "dev"])
        
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except subprocess.CalledProcessError:
        print("❌ Failed to start frontend. Make sure Node.js and npm are installed.")
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
    finally:
        # Return to root directory
        os.chdir(Path(__file__).parent)

def start_full_stack():
    """Start both backend and frontend"""
    print("\n🚀 Starting Full Stack Application...")
    print("   Backend: http://localhost:8000")
    print("   Frontend: http://localhost:3000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n   Opening browsers...")
    
    def start_backend_thread():
        try:
            backend_dir = Path("backend")
            os.chdir(backend_dir)
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "app.main:app", 
                "--reload", 
                "--host", "0.0.0.0", 
                "--port", "8000"
            ])
        except Exception as e:
            print(f"❌ Backend error: {e}")
        finally:
            os.chdir(Path(__file__).parent)
    
    def start_frontend_thread():
        try:
            time.sleep(2)  # Give backend time to start
            frontend_dir = Path("frontend")
            os.chdir(frontend_dir)
            
            if not Path("node_modules").exists():
                subprocess.run(["npm", "install"], check=True)
            
            subprocess.run(["npm", "run", "dev"])
        except Exception as e:
            print(f"❌ Frontend error: {e}")
        finally:
            os.chdir(Path(__file__).parent)
    
    # Start services in separate threads
    backend_thread = threading.Thread(target=start_backend_thread, daemon=True)
    frontend_thread = threading.Thread(target=start_frontend_thread, daemon=True)
    
    backend_thread.start()
    frontend_thread.start()
    
    # Wait a moment then open browsers
    time.sleep(3)
    try:
        webbrowser.open("http://localhost:3000")
        webbrowser.open("http://localhost:8000/docs")
    except:
        pass
    
    try:
        print("\n   Press Ctrl+C to stop all services")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 All services stopped by user")

def run_api_manager():
    """Run the API manager tool"""
    print("\n🔑 Starting API Manager...")
    
    api_manager = Path("tools/multi_api_manager.py")
    if not api_manager.exists():
        print("❌ API manager tool not found.")
        return
        
    try:
        subprocess.run([sys.executable, str(api_manager)])
    except Exception as e:
        print(f"❌ Failed to start API manager: {e}")

def start_with_docker():
    """Start using Docker Compose"""
    print("\n🐳 Starting with Docker...")
    
    if not Path("docker-compose.yml").exists():
        print("❌ docker-compose.yml not found.")
        return
    
    try:
        print("   Starting services with Docker Compose...")
        print("   Backend: http://localhost:8000")
        print("   Frontend: http://localhost:3000")
        subprocess.run(["docker-compose", "up", "--build"])
    except KeyboardInterrupt:
        print("\n🛑 Docker services stopped by user")
    except Exception as e:
        print(f"❌ Failed to start with Docker: {e}")

def show_system_status():
    """Show system status"""
    print("\n🔍 System Status:")
    
    # Check Python
    print(f"  ✅ Python: {sys.version.split()[0]}")
    
    # Check config files
    config_files = [
        ("api_config.json", "API Configuration"),
        ("requirements.txt", "Python Dependencies"),
        ("docker-compose.yml", "Docker Configuration")
    ]
    
    for file_path, description in config_files:
        status = "✅" if Path(file_path).exists() else "❌"
        print(f"  {status} {description}: {file_path}")
    
    # Check directories
    directories = [
        ("backend", "Backend API"),
        ("frontend", "Frontend UI"),
        ("tools", "Tools & Scripts")
    ]
    
    for dir_path, description in directories:
        status = "✅" if Path(dir_path).exists() else "❌"
        print(f"  {status} {description}: {dir_path}/")
    
    # Check external tools
    external_tools = [
        ("docker", "Docker"),
        ("node", "Node.js"),
        ("npm", "NPM")
    ]
    
    for tool, description in external_tools:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print(f"  ✅ {description}: {version}")
            else:
                print(f"  ❌ {description}: Not available")
        except FileNotFoundError:
            print(f"  ❌ {description}: Not installed")

def show_help():
    """Show help information"""
    print("""
📖 AI Manus Help Guide

🔧 What is AI Manus?
AI Manus is a general-purpose AI Agent system with:
- Multi-API key management and rotation
- Web-based chat interface
- RESTful API backend
- Docker support
- Automatic setup and configuration

🚀 Getting Started:
1. First time? Choose option 1 (Setup System)
2. Want to chat with AI? Choose option 4 (Full Stack)
3. Need API management? Choose option 6 (API Manager)

📁 Key Files:
- api_config.json: Configure your AI API keys
- requirements.txt: Python package dependencies
- docker-compose.yml: Docker container configuration

🌐 Web Interfaces:
- Frontend (Chat): http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

🔑 API Keys Setup:
Edit api_config.json and add your keys:
- OpenAI: sk-proj-xxxxxxxxxx
- Anthropic: sk-ant-xxxxxxxxxx
- Google: AIzaxxxxxxxxxx
- DeepSeek: sk-xxxxxxxxxx

❓ Need more help?
Check the README.md file or visit the project documentation.
""")

def interactive_menu():
    """Show interactive menu"""
    while True:
        print("\n" + "="*60)
        print("🤖 AI Manus - Main Menu")
        print("="*60)
        print("1. 🛠️  Setup System (First time setup)")
        print("2. 🔧 Start Backend Only")
        print("3. 🎨 Start Frontend Only") 
        print("4. 🚀 Start Full Stack (Recommended)")
        print("5. 🐳 Start with Docker")
        print("6. 🔑 API Manager Tool")
        print("7. 🔍 System Status")
        print("8. 📖 Help & Documentation")
        print("9. ❌ Exit")
        print("="*60)
        
        try:
            choice = input("\n🎯 Select an option (1-9): ").strip()
            
            if choice == "1":
                setup_system()
            elif choice == "2":
                start_backend()
            elif choice == "3":
                start_frontend()
            elif choice == "4":
                start_full_stack()
            elif choice == "5":
                start_with_docker()
            elif choice == "6":
                run_api_manager()
            elif choice == "7":
                show_system_status()
            elif choice == "8":
                show_help()
            elif choice == "9":
                print("\n👋 Thank you for using AI Manus!")
                break
            else:
                print("\n❌ Invalid choice. Please select 1-9.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Thank you for using AI Manus!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Main entry point"""
    # Print banner
    print_banner()
    
    # Check if running with arguments (backward compatibility)
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            setup_system()
        elif command == "backend":
            start_backend()
        elif command == "frontend":
            start_frontend()
        elif command == "fullstack" or command == "full":
            start_full_stack()
        elif command == "docker":
            start_with_docker()
        elif command == "api":
            run_api_manager()
        elif command == "status":
            show_system_status()
        elif command == "help":
            show_help()
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
    else:
        # Interactive mode
        interactive_menu()

if __name__ == "__main__":
    main()
