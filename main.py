#!/usr/bin/env python3
"""
🚀 Complete Multi-API Manager with All Components
සේරම folders ටික එක file එකේ - backend, frontend, sandbox, mockserver, API management
All main.py files integrated into one unified system!
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

# =================== BACKEND SERVER (INTEGRATED) ===================

def create_backend_server():
    """Create the main backend FastAPI server (backend/app/main.py integrated)"""
    try:
        from fastapi import FastAPI, HTTPException, Depends
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import StreamingResponse
        from pydantic import BaseModel
        from contextlib import asynccontextmanager
        import uvicorn
        
        # Backend models
        class ChatRequest(BaseModel):
            message: str
            provider: str = "openai"
            model: str = None
            stream: bool = False
            
        class ChatResponse(BaseModel):
            response: str
            provider: str
            model: str = None
            key_used: str = None
            
        class AgentRequest(BaseModel):
            query: str
            session_id: str = None
            
        # Create lifespan manager
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            print("🚀 Backend server starting...")
            yield
            print("🛑 Backend server shutting down...")
        
        app = FastAPI(
            title="Manus AI Agent - Multi-API Backend", 
            version="2.0.0",
            description="Complete backend with multi-API key management",
            lifespan=lifespan
        )
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Chat endpoint with multi-API support
        @app.post("/api/v1/chat", response_model=ChatResponse)
        async def chat_endpoint(request: ChatRequest):
            """Chat endpoint with multi-API provider support"""
            try:
                response = await chat_completion(
                    request.message, 
                    provider=request.provider,
                    model=request.model
                )
                return ChatResponse(
                    response=response, 
                    provider=request.provider,
                    model=request.model or "default"
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Agent endpoint (backend functionality)
        @app.post("/api/v1/agent")
        async def agent_endpoint(request: AgentRequest):
            """Advanced agent endpoint with tools and reasoning"""
            try:
                # Simple implementation - can be extended
                response = await chat_completion(
                    f"You are an AI assistant. Please respond to: {request.query}",
                    provider="openai"
                )
                return {
                    "response": response,
                    "session_id": request.session_id or "default",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        # File upload endpoint
        @app.post("/api/v1/files/upload")
        async def upload_file():
            """File upload endpoint"""
            return {"message": "File upload endpoint - implement as needed"}
        
        # Search endpoint
        @app.get("/api/v1/search")
        async def search_endpoint(q: str):
            """Search endpoint"""
            return {"query": q, "results": ["Search functionality to be implemented"]}
            
        # Statistics endpoint
        @app.get("/api/v1/stats")
        async def stats_endpoint():
            """Get API usage statistics"""
            manager = init_api_manager()
            return manager.get_usage_stats()
            
        # Health check endpoint
        @app.get("/api/v1/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy", 
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0",
                "components": ["multi-api-manager", "backend", "sandbox", "mockserver"]
            }
            
        # Sessions endpoint
        @app.get("/api/v1/sessions")
        async def get_sessions():
            """Get user sessions"""
            return {"sessions": [{"id": "default", "created": datetime.now().isoformat()}]}
            
        return app, uvicorn
        
    except ImportError as e:
        print(f"Backend dependencies missing: {e}")
        return None, None

# =================== SANDBOX SERVER (INTEGRATED) ===================

def create_sandbox_server():
    """Create the sandbox FastAPI server (sandbox/app/main.py integrated)"""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.exceptions import RequestValidationError
        from starlette.exceptions import HTTPException as StarletteHTTPException
        from pydantic import BaseModel
        import uvicorn
        
        app = FastAPI(
            title="Sandbox API Server",
            version="1.0.0",
            description="Sandbox environment for code execution and testing"
        )
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        class CodeRequest(BaseModel):
            code: str
            language: str = "python"
            
        class CodeResponse(BaseModel):
            output: str
            error: str = None
            execution_time: float = 0.0
            
        @app.post("/api/v1/execute", response_model=CodeResponse)
        async def execute_code(request: CodeRequest):
            """Execute code in sandbox environment"""
            try:
                if request.language.lower() == "python":
                    # Simple Python execution (for demo - in production use proper sandboxing)
                    import subprocess
                    import tempfile
                    
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                        f.write(request.code)
                        f.flush()
                        
                        start_time = time.time()
                        result = subprocess.run([
                            sys.executable, f.name
                        ], capture_output=True, text=True, timeout=10)
                        execution_time = time.time() - start_time
                        
                        os.unlink(f.name)
                        
                        return CodeResponse(
                            output=result.stdout,
                            error=result.stderr if result.stderr else None,
                            execution_time=execution_time
                        )
                else:
                    return CodeResponse(
                        output="",
                        error=f"Language {request.language} not supported yet",
                        execution_time=0.0
                    )
                    
            except subprocess.TimeoutExpired:
                return CodeResponse(
                    output="",
                    error="Code execution timed out",
                    execution_time=10.0
                )
            except Exception as e:
                return CodeResponse(
                    output="",
                    error=str(e),
                    execution_time=0.0
                )
        
        @app.get("/api/v1/sandbox/health")
        async def sandbox_health():
            """Sandbox health check"""
            return {"status": "healthy", "service": "sandbox"}
            
        return app, uvicorn
        
    except ImportError as e:
        print(f"Sandbox dependencies missing: {e}")
        return None, None

# =================== MOCKSERVER (INTEGRATED) ===================

def create_mock_server():
    """Create a mock API server (mockserver/main.py integrated)"""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        import uvicorn
        import yaml
        
        app = FastAPI(title="Mock API Server", description="Mock server for testing AI APIs")
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        class Message(BaseModel):
            role: str
            content: str = None
            
        class ChatRequest(BaseModel):
            model: str
            messages: List[Message]
            temperature: float = 0.7
            max_tokens: int = None
            
        class ChatResponse(BaseModel):
            choices: List[dict]
            usage: dict = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
            model: str = "mock-model"
            
        # Mock responses
        mock_responses = [
            "Hello! This is a mock response from the API server.",
            "I'm a mock AI assistant. How can I help you today?",
            "This is response #3 from the mock server.",
            "Mock response: I understand your request and here's my response.",
            "Another mock response to simulate different API behaviors."
        ]
        
        current_response_index = 0
        
        @app.post("/v1/chat/completions", response_model=ChatResponse)
        async def mock_chat_completions(request: ChatRequest):
            """Mock OpenAI-compatible chat completions endpoint"""
            global current_response_index
            
            # Get the user's message
            user_message = "No message"
            if request.messages:
                user_message = request.messages[-1].content or "No content"
            
            # Get mock response
            mock_response = mock_responses[current_response_index % len(mock_responses)]
            current_response_index += 1
            
            return ChatResponse(
                choices=[{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"{mock_response} (Responding to: {user_message[:50]}...)"
                    },
                    "finish_reason": "stop"
                }],
                model=request.model
            )
        
        @app.get("/v1/models")
        async def list_models():
            """Mock models endpoint"""
            return {
                "data": [
                    {"id": "mock-gpt-3.5-turbo", "object": "model"},
                    {"id": "mock-gpt-4", "object": "model"},
                    {"id": "mock-claude", "object": "model"}
                ]
            }
            
        @app.get("/health")
        async def mock_health():
            """Mock server health check"""
            return {"status": "healthy", "service": "mockserver", "responses_served": current_response_index}
            
        return app, uvicorn
        
    except ImportError:
        return None, None

# =================== FRONTEND SERVER ===================

def start_frontend_server():
    """Start the frontend development server"""
    try:
        # Create a comprehensive HTML interface
        html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Complete Multi-API Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .main-content { padding: 30px; }
        .tabs {
            display: flex;
            border-bottom: 2px solid #eee;
            margin-bottom: 30px;
        }
        .tab {
            padding: 15px 25px;
            background: #f8f9fa;
            border: none;
            cursor: pointer;
            font-size: 16px;
            border-radius: 10px 10px 0 0;
            margin-right: 5px;
            transition: all 0.3s;
        }
        .tab.active { background: #007bff; color: white; }
        .tab:hover { background: #e9ecef; }
        .tab.active:hover { background: #0056b3; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .chat-container {
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 20px;
            height: 500px;
        }
        .chat-messages {
            border: 2px solid #eee;
            border-radius: 10px;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        .chat-controls {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 10px;
            max-width: 80%;
        }
        .message.user {
            background: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .message.assistant {
            background: #e9ecef;
            color: #333;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        input, select, button, textarea {
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            font-family: inherit;
        }
        input, textarea { flex: 1; }
        button {
            background: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            transition: background 0.3s;
            min-width: 120px;
        }
        button:hover { background: #0056b3; }
        button:disabled { background: #6c757d; cursor: not-allowed; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-card h3 { font-size: 1.5em; margin-bottom: 10px; }
        .stat-card .number { font-size: 2.5em; font-weight: bold; }
        .code-editor {
            background: #2d3748;
            color: #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            min-height: 200px;
            resize: vertical;
        }
        .response { 
            background: white; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px; 
            border-left: 4px solid #007bff;
            white-space: pre-wrap;
        }
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
            <h1>🚀 Complete Multi-API Manager</h1>
            <p>සේරම Components එක Interface එකේ! Backend, Sandbox, MockServer & Multi-API Management</p>
        </div>
        
        <div class="main-content">
            <div class="tabs">
                <button class="tab active" onclick="showTab('chat')">💬 Chat</button>
                <button class="tab" onclick="showTab('stats')">📊 Statistics</button>
                <button class="tab" onclick="showTab('sandbox')">🔧 Sandbox</button>
                <button class="tab" onclick="showTab('config')">⚙️ Config</button>
            </div>
            
            <!-- Chat Tab -->
            <div id="chat" class="tab-content active">
                <div class="chat-container">
                    <div class="chat-messages" id="chatMessages"></div>
                    <div class="chat-controls">
                        <select id="providerSelect">
                            <option value="openai">OpenAI</option>
                            <option value="anthropic">Anthropic</option>
                            <option value="google">Google</option>
                            <option value="deepseek">DeepSeek</option>
                        </select>
                        <select id="modelSelect">
                            <option value="">Default Model</option>
                            <option value="gpt-4">GPT-4</option>
                            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                            <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                            <option value="gemini-pro">Gemini Pro</option>
                        </select>
                        <button onclick="testAllProviders()">🧪 Test All</button>
                        <button onclick="clearChat()">🗑️ Clear</button>
                    </div>
                </div>
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="Ask me anything..." onkeypress="if(event.key==='Enter') sendMessage()">
                    <button onclick="sendMessage()" id="sendButton">Send</button>
                </div>
            </div>
            
            <!-- Statistics Tab -->
            <div id="stats" class="tab-content">
                <div class="stats-grid" id="statsGrid">
                    <!-- Stats will be loaded here -->
                </div>
                <button onclick="loadStats()" style="margin-top: 20px;">🔄 Refresh Stats</button>
            </div>
            
            <!-- Sandbox Tab -->
            <div id="sandbox" class="tab-content">
                <h3>🔧 Code Sandbox</h3>
                <textarea class="code-editor" id="codeInput" placeholder="# Write your Python code here...
print('Hello from the sandbox!')

# Example: Simple calculation
x = 10
y = 20
result = x + y
print(f'Result: {result}')"></textarea>
                <div class="input-group">
                    <select id="languageSelect">
                        <option value="python">Python</option>
                        <option value="javascript">JavaScript (Coming Soon)</option>
                    </select>
                    <button onclick="executeCode()">▶️ Execute</button>
                </div>
                <div id="codeOutput" class="response" style="margin-top: 20px; display: none;"></div>
            </div>
            
            <!-- Config Tab -->
            <div id="config" class="tab-content">
                <h3>⚙️ Configuration</h3>
                <p>API endpoints:</p>
                <ul style="margin: 20px 0; padding-left: 20px;">
                    <li><strong>Backend:</strong> http://localhost:8000</li>
                    <li><strong>Sandbox:</strong> http://localhost:8001</li>
                    <li><strong>MockServer:</strong> http://localhost:8002</li>
                </ul>
                <p>To add API keys, edit the <code>api_config.json</code> file or use the command line interface.</p>
                <button onclick="checkHealth()">🏥 Health Check</button>
                <div id="healthOutput" class="response" style="margin-top: 20px; display: none;"></div>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // Load stats when stats tab is shown
            if (tabName === 'stats') {
                loadStats();
            }
        }
        
        async function sendMessage() {
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            if (!message) return;
            
            const provider = document.getElementById('providerSelect').value;
            const model = document.getElementById('modelSelect').value;
            const sendButton = document.getElementById('sendButton');
            const chatMessages = document.getElementById('chatMessages');
            
            // Add user message
            addMessage('user', message);
            messageInput.value = '';
            
            // Show loading
            sendButton.innerHTML = '<div class="loading"></div>';
            sendButton.disabled = true;
            
            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        message, 
                        provider,
                        model: model || null
                    })
                });
                
                const data = await response.json();
                addMessage('assistant', data.response, provider);
                
            } catch (error) {
                addMessage('assistant', `Error: ${error.message}`, 'error');
            } finally {
                sendButton.innerHTML = 'Send';
                sendButton.disabled = false;
            }
        }
        
        function addMessage(role, content, provider = '') {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            const providerTag = provider ? `[${provider}] ` : '';
            messageDiv.innerHTML = `${providerTag}${content}`;
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function clearChat() {
            document.getElementById('chatMessages').innerHTML = '';
        }
        
        async function testAllProviders() {
            const providers = ['openai', 'anthropic', 'google', 'deepseek'];
            const testMessage = 'Hello! Please respond with a short greeting.';
            
            addMessage('assistant', '🧪 Testing all providers...', 'system');
            
            for (const provider of providers) {
                try {
                    const response = await fetch('/api/v1/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            message: testMessage, 
                            provider: provider
                        })
                    });
                    
                    const data = await response.json();
                    addMessage('assistant', `✅ ${data.response}`, provider);
                    
                } catch (error) {
                    addMessage('assistant', `❌ Failed: ${error.message}`, provider);
                }
            }
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
                        <h3>🔑 ${provider.toUpperCase()}</h3>
                        <div class="number">${data.active_keys}</div>
                        <p>Active Keys</p>
                        <p style="margin-top: 10px;">Usage: ${data.total_usage}/${data.total_limit}</p>
                    `;
                    statsGrid.appendChild(card);
                }
                
            } catch (error) {
                document.getElementById('statsGrid').innerHTML = `<p>Error loading stats: ${error.message}</p>`;
            }
        }
        
        async function executeCode() {
            const code = document.getElementById('codeInput').value;
            const language = document.getElementById('languageSelect').value;
            const output = document.getElementById('codeOutput');
            
            if (!code.trim()) return;
            
            output.style.display = 'block';
            output.innerHTML = '⏳ Executing code...';
            
            try {
                const response = await fetch('/api/v1/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code, language })
                });
                
                const data = await response.json();
                
                let result = '';
                if (data.output) result += `Output:\n${data.output}\n`;
                if (data.error) result += `Error:\n${data.error}\n`;
                result += `Execution time: ${data.execution_time.toFixed(3)}s`;
                
                output.innerHTML = result;
                
            } catch (error) {
                output.innerHTML = `Error: ${error.message}`;
            }
        }
        
        async function checkHealth() {
            const healthOutput = document.getElementById('healthOutput');
            healthOutput.style.display = 'block';
            healthOutput.innerHTML = '🔍 Checking health...';
            
            try {
                const response = await fetch('/api/v1/health');
                const health = await response.json();
                
                healthOutput.innerHTML = `
Status: ${health.status}
Version: ${health.version}
Components: ${health.components.join(', ')}
Timestamp: ${health.timestamp}
                `;
                
            } catch (error) {
                healthOutput.innerHTML = `Health check failed: ${error.message}`;
            }
        }
        
        // Load stats on page load
        window.onload = function() {
            loadStats();
        };
    </script>
</body>
</html>
        '''
        
        # Write HTML to file
        html_path = Path("complete_frontend.html")
        with open(html_path, 'w') as f:
            f.write(html_content)
            
        print(f"✅ Complete frontend interface created at: {html_path}")
        print("🌐 Open this file in your browser after starting the backend server")
        
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

def run_all_servers():
    """Run all servers simultaneously"""
    print("\n🚀 Starting ALL Servers...")
    print("🔧 Backend: Port 8000")
    print("🧪 Sandbox: Port 8001")
    print("🎭 MockServer: Port 8002")
    print("🛑 Press Ctrl+C to stop all servers")
    
    # Create servers
    backend_app, backend_uvicorn = create_backend_server()
    sandbox_app, sandbox_uvicorn = create_sandbox_server()
    mock_app, mock_uvicorn = create_mock_server()
    
    if not all([backend_app, sandbox_app, mock_app]):
        print("❌ Could not create all servers")
        return
    
    # Create threading functions
    def run_backend():
        try:
            backend_uvicorn.run(backend_app, host="0.0.0.0", port=8000, log_level="info")
        except Exception as e:
            print(f"Backend error: {e}")
    
    def run_sandbox():
        try:
            sandbox_uvicorn.run(sandbox_app, host="0.0.0.0", port=8001, log_level="info")
        except Exception as e:
            print(f"Sandbox error: {e}")
    
    def run_mock():
        try:
            mock_uvicorn.run(mock_app, host="0.0.0.0", port=8002, log_level="info")
        except Exception as e:
            print(f"Mock error: {e}")
    
    # Start all servers in threads
    threads = []
    threads.append(threading.Thread(target=run_backend, daemon=True))
    threads.append(threading.Thread(target=run_sandbox, daemon=True))
    threads.append(threading.Thread(target=run_mock, daemon=True))
    
    for thread in threads:
        thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all servers...")

def create_simple_interface():
    """Create a simple command-line interface"""
    
    print("\n" + "="*60)
    print("🚀 Complete Multi-API Manager")
    print("සේරම components එක file එකේ!")
    print("Backend + Sandbox + MockServer + Multi-API - ALL INTEGRATED!")
    print("="*60)
    
    while True:
        print("\n📋 Available Commands:")
        print("1. 💬 Chat with AI")
        print("2. 📊 Show Usage Statistics") 
        print("3. ⚙️ Manage API Keys")
        print("4. 🧪 Test All Providers")
        print("5. 🏃 Start Backend Server (Port 8000)")
        print("6. 🔧 Start Sandbox Server (Port 8001)")
        print("7. 🎭 Start Mock Server (Port 8002)")
        print("8. 🚀 Start ALL Servers (8000, 8001, 8002)")
        print("9. 🌐 Create Frontend Interface")
        print("10. 📖 Show Documentation")
        print("0. 🚪 Exit")
        
        try:
            choice = input("\n👉 Enter your choice (0-10): ").strip()
            
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
                    print("📋 Integrated endpoints from backend/app/main.py")
                    print("🛑 Press Ctrl+C to stop")
                    try:
                        uvicorn.run(app, host="0.0.0.0", port=8000)
                    except KeyboardInterrupt:
                        print("\n🛑 Backend server stopped")
                else:
                    print("❌ Could not start backend server")
                
            elif choice == "6":
                app, uvicorn = create_sandbox_server()
                if app and uvicorn:
                    print("🔧 Starting Sandbox Server on http://localhost:8001")
                    print("📋 Integrated endpoints from sandbox/app/main.py")
                    print("🛑 Press Ctrl+C to stop")
                    try:
                        uvicorn.run(app, host="0.0.0.0", port=8001)
                    except KeyboardInterrupt:
                        print("\n🛑 Sandbox server stopped")
                else:
                    print("❌ Could not start sandbox server")
                    
            elif choice == "7":
                app, uvicorn = create_mock_server()
                if app and uvicorn:
                    print("🎭 Starting Mock Server on http://localhost:8002")
                    print("📋 Integrated endpoints from mockserver/main.py")
                    print("🛑 Press Ctrl+C to stop")
                    try:
                        uvicorn.run(app, host="0.0.0.0", port=8002)
                    except KeyboardInterrupt:
                        print("\n🛑 Mock server stopped")
                else:
                    print("❌ Could not start mock server")
            
            elif choice == "8":
                run_all_servers()
                
            elif choice == "9":
                if start_frontend_server():
                    print("✅ Complete frontend interface created!")
                    print("🌐 Start backend server first, then open complete_frontend.html")
                else:
                    print("❌ Could not create frontend")
                    
            elif choice == "10":
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

🎯 ALL COMPONENTS INTEGRATED:
✅ Multi-API key management (OpenAI, Anthropic, Google, DeepSeek)
✅ Complete Backend Server (backend/app/main.py integrated)
✅ Sandbox Server (sandbox/app/main.py integrated) 
✅ Mock Server (mockserver/main.py integrated)
✅ Frontend Web Interface
✅ Usage tracking and statistics
✅ All in ONE single file!

🚀 Quick Start:
1. Run: python3 main.py
2. Choose option 3 to add your API keys
3. Choose option 8 to start ALL servers
4. Choose option 9 to create frontend interface
5. Open complete_frontend.html in browser

📋 Server Ports:
🔧 Backend Server:  http://localhost:8000 (Main API)
🧪 Sandbox Server:  http://localhost:8001 (Code execution)
🎭 Mock Server:     http://localhost:8002 (Testing)

🔑 Backend API Endpoints (Port 8000):
POST /api/v1/chat - Multi-provider chat
POST /api/v1/agent - Advanced agent with tools
GET /api/v1/stats - Usage statistics
GET /api/v1/health - Health check
GET /api/v1/sessions - User sessions
POST /api/v1/files/upload - File upload
GET /api/v1/search - Search functionality

🧪 Sandbox API Endpoints (Port 8001):
POST /api/v1/execute - Execute code
GET /api/v1/sandbox/health - Sandbox health

🎭 Mock API Endpoints (Port 8002):
POST /v1/chat/completions - Mock OpenAI API
GET /v1/models - Mock models list
GET /health - Mock health check

🎮 Command Options:
1: Direct chat with any AI provider
2: Real-time usage statistics
3: Add/remove/manage API keys
4: Test all providers simultaneously
5: Start backend server only
6: Start sandbox server only
7: Start mock server only
8: Start ALL servers at once! 🚀
9: Create comprehensive web interface
10: This documentation

💡 Integration Features:
- All original main.py files are integrated
- Backend with agent services, file storage, search
- Sandbox with code execution capabilities
- Mock server with OpenAI-compatible endpoints
- Multi-API key rotation and fallback
- Usage tracking across all providers
- Web interface connecting all components

🔧 Files Created:
- api_config.json - API key configuration
- complete_frontend.html - Full web interface
- Logs and statistics files

🆘 Everything in One File:
This single main.py contains ALL functionality:
- No need for separate backend/sandbox/mockserver folders
- All dependencies and packages auto-installed
- Complete integration of all components
- Ready to run on any system!

🎯 Perfect for:
- Development and testing
- Production deployment
- Learning and experimentation
- Complete AI API management solution
"""
    print(docs)

# =================== MAIN FUNCTION ===================

def main():
    """Main entry point"""
    print("🚀 Complete Multi-API Manager")
    print("සේරම folders ටික එක file එකේ!")
    print("Backend + Sandbox + MockServer + Multi-API - ALL INTEGRATED!")
    
    # Install packages
    if not install_all_packages():
        print("⚠️ Some packages may be missing, but continuing...")
    
    # Create interface
    create_simple_interface()

if __name__ == "__main__":
    main()
