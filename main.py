#!/usr/bin/env python3
"""
🚀 Complete Multi-API Manager with All Components
සේරම folders ටික एक file එකේ - backend, frontend, sandbox, mockserver, API management
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
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging
import importlib.util
import tempfile

# =================== PACKAGE INSTALLATION ===================

def install_all_packages():
    """Install all required packages for all components"""
    print("🚀 Complete Multi-API Manager Setup")
    print("📦 Installing ALL required packages...")
    
    # Comprehensive package list from all folders
    all_packages = [
        # Core API packages
        'requests>=2.31.0',
        'aiohttp>=3.8.0',
        'asyncio-throttle>=1.0.2',
        'openai>=1.0.0',
        'anthropic>=0.7.0',
        'google-generativeai>=0.3.0',
        
        # Web framework (backend/sandbox/mockserver)
        'fastapi>=0.104.0',
        'uvicorn>=0.24.0',
        'sse-starlette>=1.6.0',
        'websockets>=11.0.0',
        'python-multipart>=0.0.6',
        
        # Database & Storage (backend)
        'motor>=3.3.2',
        'pymongo>=4.6.1',
        'beanie>=1.25.0',
        'redis>=5.0.1',
        'async-lru>=2.0.0',
        
        # Configuration & Environment
        'python-dotenv>=1.0.0',
        'pydantic>=2.4.0',
        'pydantic-settings>=2.0.0',
        'email-validator>=2.0.0',
        
        # HTTP & Web
        'httpx>=0.25.0',
        'beautifulsoup4>=4.12.0',
        'markdownify>=0.11.0',
        
        # Automation & Browser
        'playwright>=1.42.0',
        'docker>=6.1.0',
        
        # Utilities
        'rich>=13.0.0',
        'structlog>=23.0.0',
        'pathlib2>=2.3.7',
        'watchdog>=3.0.0',
        'click>=8.1.0',
        'colorama>=0.4.6',
        'tabulate>=0.9.0',
        'PyYAML>=6.0.1',
        
        # MCP
        'mcp>=1.9.0',
        
        # Testing
        'pytest>=7.0.0',
        'pytest-asyncio>=0.21.0',
    ]
    
    missing_packages = []
    for package in all_packages:
        package_name = package.split('>=')[0].split('==')[0].split('[')[0]
        try:
            if package_name == 'google-generativeai':
                import google.generativeai
            elif package_name == 'python-dotenv':
                import dotenv
            elif package_name == 'python-multipart':
                import multipart
            elif package_name == 'email-validator':
                import email_validator
            elif package_name == 'sse-starlette':
                import sse_starlette
            else:
                __import__(package_name.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 Installing {len(missing_packages)} missing packages...")
        try:
            # Try with --break-system-packages for externally managed environments
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--break-system-packages"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "--break-system-packages", *missing_packages
                ])
            except subprocess.CalledProcessError:
                # Fallback to user install
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "--user", *missing_packages
                ])
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Automatic installation failed: {e}")
            print("📋 Please install manually:")
            print(f"pip install --break-system-packages {' '.join(missing_packages)}")
            print("or")
            print(f"pip install --user {' '.join(missing_packages)}")
            return False
    else:
        print("✅ All packages already installed!")
    
    return True

# =================== MULTI-API MANAGER ===================

@dataclass
class APIKeyConfig:
    """Configuration for a single API key"""
    key: str
    provider: str
    base_url: Optional[str] = None
    daily_limit: int = 1000
    current_usage: int = 0
    last_reset: str = ""
    is_active: bool = True
    priority: int = 1

class MultiAPIManager:
    """Multi-API key manager with automatic rotation and usage tracking"""
    
    def __init__(self, config_path: str = "api_config.json"):
        self.config_path = Path(config_path)
        self.api_keys: Dict[str, List[APIKeyConfig]] = {
            'openai': [], 'anthropic': [], 'google': [], 'deepseek': []
        }
        self.current_indices: Dict[str, int] = {
            'openai': 0, 'anthropic': 0, 'google': 0, 'deepseek': 0
        }
        self.load_config()
        
    def create_default_config(self):
        """Create a default configuration file"""
        default_config = {
            "api_keys": {
                "openai": [{
                    "key": "sk-proj-your-openai-key-here",
                    "provider": "openai",
                    "base_url": "https://api.openai.com/v1",
                    "daily_limit": 1000,
                    "current_usage": 0,
                    "last_reset": datetime.now().strftime("%Y-%m-%d"),
                    "is_active": True,
                    "priority": 1
                }],
                "anthropic": [{
                    "key": "sk-ant-your-anthropic-key-here",
                    "provider": "anthropic",
                    "base_url": "https://api.anthropic.com",
                    "daily_limit": 1000,
                    "current_usage": 0,
                    "last_reset": datetime.now().strftime("%Y-%m-%d"),
                    "is_active": True,
                    "priority": 1
                }],
                "google": [{
                    "key": "AIza-your-google-key-here",
                    "provider": "google",
                    "base_url": None,
                    "daily_limit": 1000,
                    "current_usage": 0,
                    "last_reset": datetime.now().strftime("%Y-%m-%d"),
                    "is_active": True,
                    "priority": 1
                }],
                "deepseek": [{
                    "key": "sk-your-deepseek-key-here",
                    "provider": "deepseek",
                    "base_url": "https://api.deepseek.com/v1",
                    "daily_limit": 1000,
                    "current_usage": 0,
                    "last_reset": datetime.now().strftime("%Y-%m-%d"),
                    "is_active": True,
                    "priority": 1
                }]
            },
            "settings": {
                "auto_rotate": True,
                "rotation_strategy": "round_robin",
                "retry_attempts": 3,
                "retry_delay": 1.0,
                "enable_usage_tracking": True,
                "daily_reset_hour": 0
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"🔧 Default configuration created at {self.config_path}")
        print("📝 Please edit this file and add your real API keys!")
        
    def load_config(self):
        """Load configuration from file"""
        if not self.config_path.exists():
            self.create_default_config()
            return
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            for provider, keys in config.get('api_keys', {}).items():
                self.api_keys[provider] = [
                    APIKeyConfig(**key_config) for key_config in keys
                ]
                
            self.settings = config.get('settings', {})
            self.reset_daily_usage_if_needed()
            
        except Exception as e:
            print(f"Error loading config: {e}")
            self.create_default_config()
            
    def save_config(self):
        """Save current configuration to file"""
        config = {
            "api_keys": {
                provider: [asdict(key) for key in keys]
                for provider, keys in self.api_keys.items()
            },
            "settings": getattr(self, 'settings', {})
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
    def reset_daily_usage_if_needed(self):
        """Reset daily usage counters if it's a new day"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        for provider, keys in self.api_keys.items():
            for key in keys:
                if key.last_reset != today:
                    key.current_usage = 0
                    key.last_reset = today
                    
    def get_available_key(self, provider: str) -> Optional[APIKeyConfig]:
        """Get an available API key for the provider"""
        if provider not in self.api_keys:
            return None
            
        keys = self.api_keys[provider]
        if not keys:
            return None
            
        available_keys = [
            key for key in keys 
            if key.is_active and key.current_usage < key.daily_limit
        ]
        
        if not available_keys:
            return None
            
        # Round robin selection
        current_idx = self.current_indices[provider]
        for i in range(len(keys)):
            idx = (current_idx + i) % len(keys)
            key = keys[idx]
            if key.is_active and key.current_usage < key.daily_limit:
                self.current_indices[provider] = (idx + 1) % len(keys)
                return key
                
        return None
        
    async def make_request(self, provider: str, **kwargs) -> Dict[str, Any]:
        """Make an API request with automatic key rotation"""
        key_config = self.get_available_key(provider)
        if not key_config:
            raise Exception(f"No available API keys for {provider}")
            
        key_config.current_usage += 1
        self.save_config()
        
        # Import here to avoid early import errors
        if provider in ['openai', 'deepseek']:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=key_config.key, base_url=key_config.base_url)
            response = await client.chat.completions.create(**kwargs)
            return {'provider': provider, 'response': response, 'key_used': f"...{key_config.key[-8:]}"}
            
        elif provider == 'anthropic':
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=key_config.key)
            response = await client.messages.create(**kwargs)
            return {'provider': provider, 'response': response, 'key_used': f"...{key_config.key[-8:]}"}
            
        elif provider == 'google':
            import google.generativeai as genai
            genai.configure(api_key=key_config.key)
            model = genai.GenerativeModel(kwargs.get('model', 'gemini-pro'))
            messages = kwargs.get('messages', [])
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            response = await model.generate_content_async(prompt)
            return {'provider': provider, 'response': response, 'key_used': f"...{key_config.key[-8:]}"}
            
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        stats = {}
        for provider, keys in self.api_keys.items():
            provider_stats = {
                'total_keys': len(keys),
                'active_keys': len([k for k in keys if k.is_active]),
                'total_usage': sum(k.current_usage for k in keys),
                'total_limit': sum(k.daily_limit for k in keys),
                'keys': [
                    {
                        'key_suffix': f"...{k.key[-8:]}",
                        'usage': k.current_usage,
                        'limit': k.daily_limit,
                        'is_active': k.is_active,
                        'last_reset': k.last_reset
                    } for k in keys
                ]
            }
            stats[provider] = provider_stats
        return stats

# =================== SIMPLE CHAT FUNCTIONS ===================

def init_api_manager() -> MultiAPIManager:
    """Initialize the API manager"""
    return MultiAPIManager()

async def chat_completion(prompt: str, provider: str = 'openai', model: str = None) -> str:
    """Simple chat completion function"""
    manager = init_api_manager()
    messages = [{"role": "user", "content": prompt}]
    
    if model is None:
        model_defaults = {
            'openai': 'gpt-3.5-turbo',
            'anthropic': 'claude-3-sonnet-20240229',
            'google': 'gemini-pro',
            'deepseek': 'deepseek-chat'
        }
        model = model_defaults.get(provider, 'gpt-3.5-turbo')
    
    try:
        result = await manager.make_request(
            provider=provider,
            model=model,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        # Extract text response based on provider
        if provider in ['openai', 'deepseek']:
            return result['response'].choices[0].message.content
        elif provider == 'anthropic':
            return result['response'].content[0].text
        elif provider == 'google':
            return result['response'].text
        else:
            return str(result['response'])
            
    except Exception as e:
        return f"Error: {e}"

def print_usage_stats():
    """Print current usage statistics"""
    manager = init_api_manager()
    stats = manager.get_usage_stats()
    
    print("\n📊 API Usage Statistics")
    print("=" * 50)
    
    for provider, provider_stats in stats.items():
        print(f"\n🔑 {provider.upper()}")
        print(f"   Total Keys: {provider_stats['total_keys']}")
        print(f"   Active Keys: {provider_stats['active_keys']}")
        print(f"   Total Usage: {provider_stats['total_usage']}/{provider_stats['total_limit']}")
        
        for key_info in provider_stats['keys']:
            status = "✅" if key_info['is_active'] else "❌"
            usage_pct = (key_info['usage'] / key_info['limit']) * 100 if key_info['limit'] > 0 else 0
            print(f"   {status} {key_info['key_suffix']}: {key_info['usage']}/{key_info['limit']} ({usage_pct:.1f}%)")

# =================== BACKEND SERVER ===================

def create_backend_server():
    """Create the backend FastAPI server"""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        import uvicorn
        
        app = FastAPI(title="Multi-API Backend", version="1.0.0")
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        class ChatRequest(BaseModel):
            message: str
            provider: str = "openai"
            
        class ChatResponse(BaseModel):
            response: str
            provider: str
            
        @app.post("/api/v1/chat", response_model=ChatResponse)
        async def chat_endpoint(request: ChatRequest):
            try:
                response = await chat_completion(request.message, request.provider)
                return ChatResponse(response=response, provider=request.provider)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        @app.get("/api/v1/stats")
        async def stats_endpoint():
            manager = init_api_manager()
            return manager.get_usage_stats()
            
        @app.get("/api/v1/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
            
        return app, uvicorn
        
    except ImportError as e:
        print(f"Backend dependencies missing: {e}")
        return None, None

# =================== MOCKSERVER ===================

def create_mock_server():
    """Create a mock API server for testing"""
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        import uvicorn
        
        app = FastAPI(title="Mock API Server")
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        class Message(BaseModel):
            role: str
            content: str
            
        class ChatRequest(BaseModel):
            model: str
            messages: List[Message]
            
        class ChatResponse(BaseModel):
            choices: List[dict]
            
        @app.post("/v1/chat/completions", response_model=ChatResponse)
        async def mock_chat_completions(request: ChatRequest):
            return ChatResponse(choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Mock response for: {request.messages[-1].content if request.messages else 'No message'}"
                },
                "finish_reason": "stop"
            }])
            
        return app, uvicorn
        
    except ImportError:
        return None, None

# =================== FRONTEND SERVER ===================

def start_frontend_server():
    """Start the frontend development server"""
    try:
        # Create a simple HTML interface
        html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-API Manager</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
        input, select, button { padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #007bff; color: white; cursor: pointer; }
        button:hover { background: #0056b3; }
        .response { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Multi-API Manager</h1>
        <div>
            <input type="text" id="messageInput" placeholder="Enter your message..." style="width: 60%;">
            <select id="providerSelect">
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="google">Google</option>
                <option value="deepseek">DeepSeek</option>
            </select>
            <button onclick="sendMessage()">Send</button>
        </div>
        <div id="responses"></div>
    </div>
    
    <script>
        async function sendMessage() {
            const message = document.getElementById('messageInput').value;
            const provider = document.getElementById('providerSelect').value;
            
            if (!message) return;
            
            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, provider })
                });
                
                const data = await response.json();
                
                const responsesDiv = document.getElementById('responses');
                const responseDiv = document.createElement('div');
                responseDiv.className = 'response';
                responseDiv.innerHTML = `<strong>${provider}:</strong> ${data.response}`;
                responsesDiv.appendChild(responseDiv);
                
                document.getElementById('messageInput').value = '';
            } catch (error) {
                console.error('Error:', error);
                alert('Error sending message');
            }
        }
        
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
        '''
        
        # Write HTML to temp file
        html_path = Path("frontend_interface.html")
        with open(html_path, 'w') as f:
            f.write(html_content)
            
        print(f"✅ Frontend interface created at: {html_path}")
        print("🌐 Open this file in your browser or serve via backend")
        
        return True
        
    except Exception as e:
        print(f"Error creating frontend: {e}")
        return False

# =================== INTERACTIVE INTERFACE ===================

async def handle_chat():
    """Handle chat interface"""
    print("\n💬 Chat with AI")
    print("Available providers: openai, anthropic, google, deepseek")
    
    provider = input("👉 Choose provider (default: openai): ").strip() or 'openai'
    
    if provider not in ['openai', 'anthropic', 'google', 'deepseek']:
        print("❌ Invalid provider!")
        return
    
    print(f"\n🤖 Chatting with {provider}. Type 'exit' to quit.")
    
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

def handle_key_management():
    """Handle API key management"""
    manager = init_api_manager()
    
    while True:
        print("\n⚙️ API Key Management")
        print("1. 📋 List all keys")
        print("2. ➕ Add new key")
        print("3. ❌ Remove key")
        print("4. 🔄 Toggle key status")
        print("0. 🔙 Back")
        
        choice = input("👉 Choose option: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            print_usage_stats()
        elif choice == "2":
            provider = input("Provider (openai/anthropic/google/deepseek): ").strip()
            key = input("API Key: ").strip()
            daily_limit = input("Daily limit (default 1000): ").strip() or "1000"
            
            if provider in manager.api_keys:
                new_key = APIKeyConfig(
                    key=key,
                    provider=provider,
                    daily_limit=int(daily_limit),
                    current_usage=0,
                    last_reset=datetime.now().strftime("%Y-%m-%d"),
                    is_active=True,
                    priority=1
                )
                manager.api_keys[provider].append(new_key)
                manager.save_config()
                print("✅ API key added!")

async def test_all_providers():
    """Test all providers"""
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

def create_simple_interface():
    """Create a simple command-line interface"""
    
    print("\n" + "="*60)
    print("🚀 Complete Multi-API Manager")
    print("සේරම components එක file එකේ!")
    print("="*60)
    
    while True:
        print("\n📋 Available Commands:")
        print("1. 💬 Chat with AI")
        print("2. 📊 Show Usage Statistics") 
        print("3. ⚙️ Manage API Keys")
        print("4. 🧪 Test All Providers")
        print("5. 🏃 Start Backend Server (Port 8000)")
        print("6. 🌐 Create Frontend Interface")
        print("7. 🔧 Start Mock Server (Port 8001)")
        print("8. 📖 Show Documentation")
        print("0. 🚪 Exit")
        
        try:
            choice = input("\n👉 Enter your choice (0-8): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
                
            elif choice == "1":
                asyncio.run(handle_chat())
                
            elif choice == "2":
                print_usage_stats()
                
            elif choice == "3":
                handle_key_management()
                
            elif choice == "4":
                asyncio.run(test_all_providers())
                
            elif choice == "5":
                app, uvicorn = create_backend_server()
                if app and uvicorn:
                    print("🏃 Starting Backend Server on http://localhost:8000")
                    print("📋 API Endpoints:")
                    print("   POST /api/v1/chat - Chat endpoint")
                    print("   GET /api/v1/stats - Usage statistics")
                    print("   GET /api/v1/health - Health check")
                    print("🛑 Press Ctrl+C to stop")
                    try:
                        uvicorn.run(app, host="0.0.0.0", port=8000)
                    except KeyboardInterrupt:
                        print("\n🛑 Backend server stopped")
                else:
                    print("❌ Could not start backend server")
                
            elif choice == "6":
                if start_frontend_server():
                    print("✅ Frontend interface created!")
                else:
                    print("❌ Could not create frontend")
                    
            elif choice == "7":
                app, uvicorn = create_mock_server()
                if app and uvicorn:
                    print("🔧 Starting Mock Server on http://localhost:8001")
                    print("🛑 Press Ctrl+C to stop")
                    try:
                        uvicorn.run(app, host="0.0.0.0", port=8001)
                    except KeyboardInterrupt:
                        print("\n🛑 Mock server stopped")
                else:
                    print("❌ Could not start mock server")
                
            elif choice == "8":
                show_documentation()
                
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def show_documentation():
    """Show documentation"""
    docs = """
📖 Complete Multi-API Manager Documentation

🎯 Features:
✅ Multi-API key management (OpenAI, Anthropic, Google, DeepSeek)
✅ Automatic key rotation and usage tracking
✅ Built-in backend server with REST API
✅ Frontend web interface
✅ Mock server for testing
✅ All components in one file!

🚀 Quick Start:
1. Run: python3 main.py
2. Choose option 3 to add your API keys
3. Use option 1 to chat with AI
4. Start backend server with option 5

📋 All Components Included:
🔧 Backend Server - Full REST API (Port 8000)
🌐 Frontend Interface - Web UI 
🧪 Mock Server - Testing API (Port 8001)
🤖 API Manager - Multi-provider support
📊 Usage Tracking - Daily limits & statistics

🔑 API Endpoints (Backend):
POST /api/v1/chat - Send chat message
GET /api/v1/stats - Get usage statistics  
GET /api/v1/health - Health check

📁 Files Created:
- api_config.json - API key configuration
- frontend_interface.html - Web interface
- api_usage.log - Usage logs (when available)

🎮 Commands:
Option 1: Chat directly with any AI provider
Option 2: View real-time usage statistics
Option 3: Add/remove/manage API keys
Option 4: Test all providers at once
Option 5: Start full backend server
Option 6: Create web interface
Option 7: Start mock server for testing
Option 8: This documentation

💡 Tips:
- Add multiple keys per provider for better reliability
- Use the web interface by starting backend server first
- Check usage statistics regularly
- Test all providers to ensure they work

🔧 Configuration:
Edit api_config.json to add your real API keys:
{
  "api_keys": {
    "openai": [{"key": "sk-proj-your-key", "daily_limit": 1000}],
    "anthropic": [{"key": "sk-ant-your-key", "daily_limit": 1000}]
  }
}

🆘 Support:
All functionality is built into this single file!
No external dependencies on other folders.
Everything works independently.
"""
    print(docs)

# =================== MAIN FUNCTION ===================

def main():
    """Main entry point"""
    print("🚀 Complete Multi-API Manager")
    print("සේරම folders ටික එක file එකේ!")
    
    # Install packages
    if not install_all_packages():
        print("⚠️ Some packages may be missing, but continuing...")
    
    # Create interface
    create_simple_interface()

if __name__ == "__main__":
    main()
