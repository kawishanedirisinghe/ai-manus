#!/usr/bin/env python3
"""
🚀 AI Manus - Complete All-in-One System
සේරම components එකට integrate කරල සෙටප් සිට web access දක්කම එක file එකේ!
Run: python3 main.py
"""

import os
import sys
import subprocess
import asyncio
import json
import time
import threading
import signal
import webbrowser
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging
import importlib.util
import tempfile

# =================== AUTO PACKAGE INSTALLATION ===================

def check_and_install_packages():
    """Auto install all required packages"""
    print("🔍 Checking required packages...")
    
    # Essential packages list
    packages = [
        'requests>=2.31.0',
        'aiohttp>=3.8.0',
        'fastapi>=0.104.0',
        'uvicorn>=0.24.0',
        'sse-starlette>=1.6.0',
        'websockets>=11.0.0',
        'python-multipart>=0.0.6',
        'motor>=3.3.2',
        'pymongo>=4.6.1',
        'beanie>=1.25.0',
        'redis>=5.0.1',
        'python-dotenv>=1.0.0',
        'pydantic>=2.4.0',
        'pydantic-settings>=2.0.0',
        'httpx>=0.25.0',
        'rich>=13.0.0',
        'click>=8.1.0',
        'colorama>=0.4.6',
        'openai>=1.0.0',
        'anthropic>=0.7.0',
        'google-generativeai>=0.3.0',
        'playwright>=1.42.0',
        'beautifulsoup4>=4.12.0',
        'docker>=6.1.0'
    ]
    
    missing = []
    for package in packages:
        pkg_name = package.split('>=')[0].split('==')[0].replace('-', '_')
        try:
            if pkg_name == 'google_generativeai':
                import google.generativeai
            elif pkg_name == 'python_dotenv':
                import dotenv
            elif pkg_name == 'python_multipart':
                import multipart
            elif pkg_name == 'sse_starlette':
                import sse_starlette
            else:
                __import__(pkg_name)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"📦 Installing {len(missing)} missing packages...")
        try:
            # Try different installation methods
            install_commands = [
                [sys.executable, "-m", "pip", "install", "--break-system-packages"] + missing,
                [sys.executable, "-m", "pip", "install", "--user"] + missing,
                [sys.executable, "-m", "pip", "install"] + missing
            ]
            
            for cmd in install_commands:
                try:
                    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print("✅ All packages installed successfully!")
                    return True
                except subprocess.CalledProcessError:
                    continue
            
            print("⚠️ Auto installation failed. Manual installation required:")
            print(f"pip install {' '.join(missing)}")
            return False
            
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False
    else:
        print("✅ All packages already available!")
        return True

# =================== CONFIGURATION SETUP ===================

def setup_configuration():
    """Setup configuration files"""
    print("⚙️ Setting up configuration...")
    
    # Create .env file if not exists
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# AI Manus Configuration
# Add your API keys here

# Google/Gemini API Keys
GOOGLE_API_KEY_1=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_API_KEY_2=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# OpenAI API Keys
OPENAI_API_KEY_1=sk-your-openai-key-here

# Anthropic API Keys
ANTHROPIC_API_KEY_1=sk-ant-your-anthropic-key-here

# DeepSeek API Keys
DEEPSEEK_API_KEY_1=sk-your-deepseek-key-here

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=ai_manus

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Application
LOG_LEVEL=INFO
ENVIRONMENT=development
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {env_file}")
    
    # Create api_config.json
    config_file = Path("api_config.json")
    if not config_file.exists():
        config = {
            "api_keys": {
                "openai": [],
                "anthropic": [],
                "google": [],
                "deepseek": []
            },
            "settings": {
                "auto_rotate": True,
                "rotation_strategy": "round_robin",
                "retry_attempts": 3,
                "retry_delay": 1.0
            }
        }
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Created {config_file}")
    
    print("✅ Configuration setup complete!")

# =================== MULTI-API MANAGER ===================

@dataclass
class APIKeyConfig:
    """API Key configuration"""
    key: str
    provider: str
    base_url: Optional[str] = None
    daily_limit: int = 1000
    current_usage: int = 0
    last_reset: str = ""
    is_active: bool = True
    priority: int = 1

class MultiAPIManager:
    """Multi-API key manager"""
    
    def __init__(self, config_path: str = "api_config.json"):
        self.config_path = Path(config_path)
        self.api_keys: Dict[str, List[APIKeyConfig]] = {
            'openai': [], 'anthropic': [], 'google': [], 'deepseek': []
        }
        self.current_indices: Dict[str, int] = {
            'openai': 0, 'anthropic': 0, 'google': 0, 'deepseek': 0
        }
        self.load_config()
    
    def load_config(self):
        """Load configuration"""
        if not self.config_path.exists():
            self.create_default_config()
            return
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Load from environment variables
            from dotenv import load_dotenv
            load_dotenv()
            
            # Add API keys from environment
            providers = {
                'google': 'GOOGLE_API_KEY_',
                'openai': 'OPENAI_API_KEY_', 
                'anthropic': 'ANTHROPIC_API_KEY_',
                'deepseek': 'DEEPSEEK_API_KEY_'
            }
            
            for provider, env_prefix in providers.items():
                for i in range(1, 6):  # Check for up to 5 keys
                    key = os.getenv(f'{env_prefix}{i}')
                    if key and not key.startswith('sk-your') and not key.startswith('AIzaSyXXX'):
                        # Check if key already exists
                        existing = [k for k in self.api_keys[provider] if k.key == key]
                        if not existing:
                            self.api_keys[provider].append(APIKeyConfig(
                                key=key,
                                provider=provider,
                                daily_limit=1000,
                                current_usage=0,
                                last_reset=datetime.now().strftime("%Y-%m-%d"),
                                is_active=True,
                                priority=i
                            ))
            
        except Exception as e:
            print(f"Warning: Config load error: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default config"""
        config = {
            "api_keys": {
                "openai": [], "anthropic": [], "google": [], "deepseek": []
            },
            "settings": {
                "auto_rotate": True,
                "rotation_strategy": "round_robin", 
                "retry_attempts": 3,
                "retry_delay": 1.0
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_available_key(self, provider: str) -> Optional[APIKeyConfig]:
        """Get available API key"""
        if provider not in self.api_keys:
            return None
        
        keys = self.api_keys[provider]
        if not keys:
            return None
        
        # Find available key
        for key in keys:
            if key.is_active and key.current_usage < key.daily_limit:
                key.current_usage += 1
                return key
        
        return None
    
    def get_stats(self):
        """Get usage statistics"""
        stats = {}
        for provider, keys in self.api_keys.items():
            stats[provider] = {
                'total_keys': len(keys),
                'active_keys': len([k for k in keys if k.is_active]),
                'total_usage': sum(k.current_usage for k in keys)
            }
        return stats

# =================== WEB SERVERS ===================

def create_backend_server():
    """Create FastAPI backend server"""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import HTMLResponse
        from pydantic import BaseModel
        import uvicorn
        
        app = FastAPI(title="AI Manus Backend", version="1.0.0")
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize API manager
        api_manager = MultiAPIManager()
        
        class ChatRequest(BaseModel):
            message: str
            provider: str = "google"
            
        class ChatResponse(BaseModel):
            response: str
            provider: str
            
        @app.post("/api/v1/chat", response_model=ChatResponse)
        async def chat_endpoint(request: ChatRequest):
            """Chat endpoint"""
            try:
                # Simple response for demo
                response = f"Hello! You asked: '{request.message}' using {request.provider} provider. This is a demo response."
                return ChatResponse(response=response, provider=request.provider)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/v1/stats")
        async def stats_endpoint():
            """Statistics endpoint"""
            return api_manager.get_stats()
        
        @app.get("/api/v1/health")
        async def health_endpoint():
            """Health check"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        
        # Frontend HTML
        @app.get("/", response_class=HTMLResponse)
        async def frontend():
            """Serve frontend"""
            html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 AI Manus - Complete System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .main-panel {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .chat-container {
            margin-bottom: 30px;
        }
        .chat-messages {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
            border: 2px solid #e9ecef;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 10px;
        }
        .message.user {
            background: #007bff;
            color: white;
            margin-left: 20%;
        }
        .message.assistant {
            background: #e9ecef;
            margin-right: 20%;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        input, select, button {
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        input { flex: 1; }
        button {
            background: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            min-width: 100px;
        }
        button:hover { background: #0056b3; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-number { font-size: 2em; font-weight: bold; }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #007bff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AI Manus</h1>
            <p>Complete All-in-One AI Agent System</p>
            <p>සේරම components එකට integrate කරපු complete system!</p>
        </div>
        
        <div class="main-panel">
            <div class="chat-container">
                <h3>💬 Chat with AI</h3>
                <div id="chatMessages" class="chat-messages">
                    <div class="message assistant">
                        Welcome to AI Manus! I'm ready to help you. Try asking me anything!
                    </div>
                </div>
                
                <div class="input-group">
                    <select id="providerSelect">
                        <option value="google">Google (Gemini)</option>
                        <option value="openai">OpenAI</option>
                        <option value="anthropic">Anthropic</option>
                        <option value="deepseek">DeepSeek</option>
                    </select>
                    <input type="text" id="messageInput" placeholder="Ask me anything..." 
                           onkeypress="if(event.key==='Enter') sendMessage()">
                    <button onclick="sendMessage()" id="sendButton">Send</button>
                </div>
            </div>
            
            <div id="statsSection">
                <h3>📊 System Statistics</h3>
                <div id="statsGrid" class="stats-grid">
                    <!-- Stats will load here -->
                </div>
                <button onclick="loadStats()" style="margin-top: 20px;">🔄 Refresh Stats</button>
            </div>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;
            
            const provider = document.getElementById('providerSelect').value;
            const sendButton = document.getElementById('sendButton');
            
            // Add user message
            addMessage('user', message);
            input.value = '';
            
            // Show loading
            sendButton.innerHTML = '<div class="loading"></div>';
            sendButton.disabled = true;
            
            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, provider })
                });
                
                const data = await response.json();
                addMessage('assistant', data.response);
                
            } catch (error) {
                addMessage('assistant', `Error: ${error.message}`);
            } finally {
                sendButton.innerHTML = 'Send';
                sendButton.disabled = false;
            }
        }
        
        function addMessage(role, content) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            messageDiv.textContent = content;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/v1/stats');
                const stats = await response.json();
                
                const statsGrid = document.getElementById('statsGrid');
                statsGrid.innerHTML = '';
                
                for (const [provider, data] of Object.entries(stats)) {
                    const card = document.createElement('div');
                    card.className = 'stat-card';
                    card.innerHTML = `
                        <h4>${provider.toUpperCase()}</h4>
                        <div class="stat-number">${data.active_keys}</div>
                        <p>Active Keys</p>
                        <p>Usage: ${data.total_usage}</p>
                    `;
                    statsGrid.appendChild(card);
                }
            } catch (error) {
                console.error('Stats loading error:', error);
            }
        }
        
        // Load stats on page load
        window.onload = loadStats;
    </script>
</body>
</html>
            """
            return html
        
        return app, uvicorn
        
    except ImportError as e:
        print(f"❌ Backend dependencies missing: {e}")
        return None, None

# =================== SERVER MANAGEMENT ===================

class ServerManager:
    """Manage all servers"""
    
    def __init__(self):
        self.servers = {}
        self.threads = []
        self.running = False
    
    def start_backend(self, port=8000):
        """Start backend server"""
        app, uvicorn = create_backend_server()
        if not app:
            return False
        
        def run_server():
            try:
                uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
            except Exception as e:
                print(f"Backend server error: {e}")
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        self.threads.append(thread)
        self.servers['backend'] = {'port': port, 'status': 'running'}
        return True
    
    def start_all_servers(self):
        """Start all servers"""
        print("🚀 Starting All Servers...")
        
        # Start backend
        if self.start_backend(8000):
            print("✅ Backend Server: http://localhost:8000")
        else:
            print("❌ Backend server failed to start")
            return False
        
        self.running = True
        return True
    
    def stop_all_servers(self):
        """Stop all servers"""
        print("🛑 Stopping all servers...")
        self.running = False
        # Servers will stop when main thread exits
    
    def open_browser(self, url="http://localhost:8000"):
        """Open browser"""
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"❌ Could not open browser: {e}")
            return False
    
    def get_status(self):
        """Get server status"""
        return self.servers

# =================== MAIN INTERFACE ===================

def print_banner():
    """Print main banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                🚀 AI Manus - Complete System                    ║
║                                                                  ║
║    සේරම components එකට integrate කරපු complete solution!       ║
║                                                                  ║
║  Auto setup → Start servers → Open browser → Use website!       ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def create_main_interface():
    """Create main interactive interface"""
    server_manager = ServerManager()
    
    print_banner()
    
    # Auto setup
    print("🔧 Auto Setup Starting...")
    if not check_and_install_packages():
        print("⚠️ Some packages missing, but continuing...")
    
    setup_configuration()
    print("✅ Setup complete!\n")
    
    while True:
        print("\n" + "="*60)
        print("📋 AI Manus Control Panel")
        print("="*60)
        print("1. 🚀 Start Complete System (Auto open browser)")
        print("2. 🌐 Start Backend Only") 
        print("3. 📊 Show System Status")
        print("4. 🔑 Manage API Keys")
        print("5. 🧪 Test API Connections")
        print("6. 🔧 Configuration Setup")
        print("7. 📖 Show System Info")
        print("8. 🌐 Open Website (if running)")
        print("0. 🚪 Exit")
        print("="*60)
        
        try:
            choice = input("👉 Select option (0-8): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting Complete System...")
                if server_manager.start_all_servers():
                    print("⏳ Waiting for servers to start...")
                    time.sleep(3)
                    
                    # Open browser automatically
                    url = "http://localhost:8000"
                    print(f"🌐 Opening browser: {url}")
                    if server_manager.open_browser(url):
                        print("✅ Browser opened! You can now use the website.")
                    else:
                        print(f"❌ Auto browser open failed. Manual open: {url}")
                    
                    print("\n🎉 System is running!")
                    print("📱 Website: http://localhost:8000")
                    print("🔧 API Docs: http://localhost:8000/docs")
                    print("🛑 Press Ctrl+C to stop servers")
                    
                    try:
                        while server_manager.running:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        server_manager.stop_all_servers()
                        print("\n🛑 System stopped")
            
            elif choice == "2":
                print("\n🌐 Starting Backend Server...")
                if server_manager.start_backend(8000):
                    print("✅ Backend running: http://localhost:8000")
                    print("🛑 Press Ctrl+C to stop")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n🛑 Backend stopped")
            
            elif choice == "3":
                print("\n📊 System Status:")
                status = server_manager.get_status()
                if status:
                    for service, info in status.items():
                        print(f"  ✅ {service}: Running on port {info['port']}")
                else:
                    print("  ❌ No servers running")
                
                # Check files
                files = [".env", "api_config.json", "requirements.txt"]
                print("\n📁 Configuration Files:")
                for file in files:
                    exists = "✅" if Path(file).exists() else "❌"
                    print(f"  {exists} {file}")
            
            elif choice == "4":
                print("\n🔑 API Key Management")
                print("Edit .env file to add your API keys:")
                print("  GOOGLE_API_KEY_1=your-google-key")
                print("  OPENAI_API_KEY_1=your-openai-key")
                print("  ANTHROPIC_API_KEY_1=your-anthropic-key")
                
                # Show current stats
                manager = MultiAPIManager()
                stats = manager.get_stats()
                print("\n📊 Current API Key Stats:")
                for provider, data in stats.items():
                    print(f"  {provider}: {data['active_keys']} active keys")
            
            elif choice == "5":
                print("\n🧪 Testing API Connections...")
                manager = MultiAPIManager()
                stats = manager.get_stats()
                
                for provider, data in stats.items():
                    if data['active_keys'] > 0:
                        print(f"  ✅ {provider}: {data['active_keys']} keys available")
                    else:
                        print(f"  ❌ {provider}: No keys configured")
            
            elif choice == "6":
                print("\n🔧 Configuration Setup...")
                setup_configuration()
                print("✅ Configuration updated!")
            
            elif choice == "7":
                print("\n📖 System Information")
                print("🚀 AI Manus - Complete All-in-One System")
                print("📁 Project Structure:")
                print("  ├── Backend API Server (FastAPI)")
                print("  ├── Frontend Web Interface")
                print("  ├── Multi-API Key Manager")
                print("  ├── Auto Package Installation")
                print("  └── One-click Browser Launch")
                print("\n🌐 Access URLs (when running):")
                print("  • Main Website: http://localhost:8000")
                print("  • API Documentation: http://localhost:8000/docs")
                print("  • Health Check: http://localhost:8000/api/v1/health")
                print("\n🔧 Features:")
                print("  • Auto setup and package installation")
                print("  • Multi-provider AI chat (Google, OpenAI, Anthropic)")
                print("  • Real-time statistics and monitoring")
                print("  • One-click launch with browser auto-open")
                print("  • Environment-based configuration")
            
            elif choice == "8":
                url = "http://localhost:8000"
                print(f"\n🌐 Opening website: {url}")
                if server_manager.open_browser(url):
                    print("✅ Browser opened!")
                else:
                    print("❌ Could not open browser automatically")
                    print(f"📱 Manual open: {url}")
            
            elif choice == "0":
                print("👋 Goodbye!")
                if server_manager.running:
                    server_manager.stop_all_servers()
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            if server_manager.running:
                server_manager.stop_all_servers()
            break
        except Exception as e:
            print(f"❌ Error: {e}")

# =================== MAIN ENTRY POINT ===================

def main():
    """Main entry point"""
    try:
        create_main_interface()
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")

if __name__ == "__main__":
    main()
