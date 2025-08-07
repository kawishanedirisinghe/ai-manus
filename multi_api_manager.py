#!/usr/bin/env python3
"""
Multi-API Key Manager
Handles multiple API keys with rotation, rate limiting, and usage tracking
"""

import json
import os
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import aiohttp
import openai
import anthropic
import google.generativeai as genai
from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_usage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class APIKeyConfig:
    """Configuration for a single API key"""
    key: str
    provider: str  # 'openai', 'anthropic', 'google', 'deepseek'
    base_url: Optional[str] = None
    daily_limit: int = 1000  # requests per day
    current_usage: int = 0
    last_reset: str = ""
    is_active: bool = True
    priority: int = 1  # Higher priority keys are used first

@dataclass 
class UsageStats:
    """Daily usage statistics"""
    date: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    providers_used: Dict[str, int] = None
    
    def __post_init__(self):
        if self.providers_used is None:
            self.providers_used = {}

class MultiAPIManager:
    """Multi-API key manager with automatic rotation and usage tracking"""
    
    def __init__(self, config_path: str = "api_config.json"):
        self.config_path = Path(config_path)
        self.api_keys: Dict[str, List[APIKeyConfig]] = {
            'openai': [],
            'anthropic': [],
            'google': [],
            'deepseek': []
        }
        self.current_indices: Dict[str, int] = {
            'openai': 0,
            'anthropic': 0, 
            'google': 0,
            'deepseek': 0
        }
        self.usage_stats_path = Path("usage_stats.json")
        self.daily_stats: Dict[str, UsageStats] = {}
        
        # Initialize clients
        self.clients: Dict[str, Any] = {}
        
        # Load configuration
        self.load_config()
        self.init_clients()
        
    def create_default_config(self):
        """Create a default configuration file"""
        default_config = {
            "api_keys": {
                "openai": [
                    {
                        "key": "sk-your-openai-key-1",
                        "provider": "openai",
                        "base_url": "https://api.openai.com/v1",
                        "daily_limit": 1000,
                        "current_usage": 0,
                        "last_reset": datetime.now().strftime("%Y-%m-%d"),
                        "is_active": True,
                        "priority": 1
                    }
                ],
                "anthropic": [
                    {
                        "key": "sk-ant-your-anthropic-key-1", 
                        "provider": "anthropic",
                        "base_url": "https://api.anthropic.com",
                        "daily_limit": 1000,
                        "current_usage": 0,
                        "last_reset": datetime.now().strftime("%Y-%m-%d"),
                        "is_active": True,
                        "priority": 1
                    }
                ],
                "google": [
                    {
                        "key": "your-google-api-key-1",
                        "provider": "google", 
                        "base_url": None,
                        "daily_limit": 1000,
                        "current_usage": 0,
                        "last_reset": datetime.now().strftime("%Y-%m-%d"),
                        "is_active": True,
                        "priority": 1
                    }
                ],
                "deepseek": [
                    {
                        "key": "sk-your-deepseek-key-1",
                        "provider": "deepseek",
                        "base_url": "https://api.deepseek.com/v1", 
                        "daily_limit": 1000,
                        "current_usage": 0,
                        "last_reset": datetime.now().strftime("%Y-%m-%d"),
                        "is_active": True,
                        "priority": 1
                    }
                ]
            },
            "settings": {
                "auto_rotate": True,
                "rotation_strategy": "round_robin",  # 'round_robin', 'priority', 'usage_based'
                "retry_attempts": 3,
                "retry_delay": 1.0,
                "enable_usage_tracking": True,
                "daily_reset_hour": 0  # Reset usage at midnight
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"Created default config file: {self.config_path}")
        print(f"\n🔧 Default configuration created at {self.config_path}")
        print("📝 Please edit this file and add your real API keys!")
        print("🚀 Then run 'python main.py' again to start using the system.")
        
    def load_config(self):
        """Load configuration from file"""
        if not self.config_path.exists():
            self.create_default_config()
            return
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Load API keys
            for provider, keys in config.get('api_keys', {}).items():
                self.api_keys[provider] = [
                    APIKeyConfig(**key_config) for key_config in keys
                ]
                
            # Load settings
            self.settings = config.get('settings', {})
            
            # Reset daily usage if needed
            self.reset_daily_usage_if_needed()
            
            logger.info(f"Loaded configuration with {sum(len(keys) for keys in self.api_keys.values())} API keys")
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
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
                    logger.info(f"Reset daily usage for {provider} key ending in ...{key.key[-8:]}")
                    
    def init_clients(self):
        """Initialize API clients"""
        try:
            # Initialize clients will be done on-demand to avoid errors with invalid keys
            logger.info("API clients will be initialized on-demand")
        except Exception as e:
            logger.error(f"Error initializing clients: {e}")
            
    def get_available_key(self, provider: str) -> Optional[APIKeyConfig]:
        """Get an available API key for the provider"""
        if provider not in self.api_keys:
            logger.error(f"Unknown provider: {provider}")
            return None
            
        keys = self.api_keys[provider]
        if not keys:
            logger.error(f"No API keys configured for {provider}")
            return None
            
        # Sort by priority and usage
        available_keys = [
            key for key in keys 
            if key.is_active and key.current_usage < key.daily_limit
        ]
        
        if not available_keys:
            logger.warning(f"No available keys for {provider} (all at daily limit)")
            return None
            
        # Use rotation strategy
        strategy = self.settings.get('rotation_strategy', 'round_robin')
        
        if strategy == 'priority':
            available_keys.sort(key=lambda x: (-x.priority, x.current_usage))
            return available_keys[0]
        elif strategy == 'usage_based':
            available_keys.sort(key=lambda x: x.current_usage)
            return available_keys[0]
        else:  # round_robin
            current_idx = self.current_indices[provider]
            # Find next available key starting from current index
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
            
        # Track usage
        key_config.current_usage += 1
        self.save_config()
        
        try:
            if provider == 'openai':
                return await self._make_openai_request(key_config, **kwargs)
            elif provider == 'anthropic':
                return await self._make_anthropic_request(key_config, **kwargs)
            elif provider == 'google':
                return await self._make_google_request(key_config, **kwargs)
            elif provider == 'deepseek':
                return await self._make_deepseek_request(key_config, **kwargs)
            else:
                raise Exception(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Request failed for {provider}: {e}")
            # Try next available key
            key_config.current_usage -= 1  # Revert usage increment
            raise e
            
    async def _make_openai_request(self, key_config: APIKeyConfig, **kwargs) -> Dict[str, Any]:
        """Make OpenAI API request"""
        client = AsyncOpenAI(
            api_key=key_config.key,
            base_url=key_config.base_url
        )
        
        messages = kwargs.get('messages', [])
        model = kwargs.get('model', 'gpt-3.5-turbo')
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            **{k: v for k, v in kwargs.items() if k not in ['messages', 'model']}
        )
        
        return {
            'provider': 'openai',
            'model': model,
            'response': response,
            'key_used': f"...{key_config.key[-8:]}"
        }
        
    async def _make_anthropic_request(self, key_config: APIKeyConfig, **kwargs) -> Dict[str, Any]:
        """Make Anthropic API request"""
        client = anthropic.AsyncAnthropic(api_key=key_config.key)
        
        messages = kwargs.get('messages', [])
        model = kwargs.get('model', 'claude-3-sonnet-20240229')
        
        response = await client.messages.create(
            model=model,
            messages=messages,
            **{k: v for k, v in kwargs.items() if k not in ['messages', 'model']}
        )
        
        return {
            'provider': 'anthropic',
            'model': model, 
            'response': response,
            'key_used': f"...{key_config.key[-8:]}"
        }
        
    async def _make_google_request(self, key_config: APIKeyConfig, **kwargs) -> Dict[str, Any]:
        """Make Google Gemini API request"""
        genai.configure(api_key=key_config.key)
        
        model_name = kwargs.get('model', 'gemini-pro')
        model = genai.GenerativeModel(model_name)
        
        messages = kwargs.get('messages', [])
        # Convert messages to Google format
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        response = await model.generate_content_async(prompt)
        
        return {
            'provider': 'google',
            'model': model_name,
            'response': response,
            'key_used': f"...{key_config.key[-8:]}"
        }
        
    async def _make_deepseek_request(self, key_config: APIKeyConfig, **kwargs) -> Dict[str, Any]:
        """Make DeepSeek API request"""
        client = AsyncOpenAI(
            api_key=key_config.key,
            base_url=key_config.base_url
        )
        
        messages = kwargs.get('messages', [])
        model = kwargs.get('model', 'deepseek-chat')
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            **{k: v for k, v in kwargs.items() if k not in ['messages', 'model']}
        )
        
        return {
            'provider': 'deepseek',
            'model': model,
            'response': response, 
            'key_used': f"...{key_config.key[-8:]}"
        }
        
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
        
    def add_api_key(self, provider: str, key: str, **kwargs):
        """Add a new API key"""
        if provider not in self.api_keys:
            logger.error(f"Unknown provider: {provider}")
            return False
            
        key_config = APIKeyConfig(
            key=key,
            provider=provider,
            base_url=kwargs.get('base_url'),
            daily_limit=kwargs.get('daily_limit', 1000),
            current_usage=0,
            last_reset=datetime.now().strftime("%Y-%m-%d"),
            is_active=True,
            priority=kwargs.get('priority', 1)
        )
        
        self.api_keys[provider].append(key_config)
        self.save_config()
        
        logger.info(f"Added new {provider} API key ending in ...{key[-8:]}")
        return True
        
    def remove_api_key(self, provider: str, key_suffix: str):
        """Remove an API key by its suffix"""
        if provider not in self.api_keys:
            return False
            
        for i, key in enumerate(self.api_keys[provider]):
            if key.key.endswith(key_suffix):
                removed_key = self.api_keys[provider].pop(i)
                self.save_config()
                logger.info(f"Removed {provider} API key ending in ...{key_suffix}")
                return True
                
        return False
        
    def toggle_key_status(self, provider: str, key_suffix: str):
        """Toggle active status of an API key"""
        if provider not in self.api_keys:
            return False
            
        for key in self.api_keys[provider]:
            if key.key.endswith(key_suffix):
                key.is_active = not key.is_active
                self.save_config()
                status = "activated" if key.is_active else "deactivated"
                logger.info(f"{status.capitalize()} {provider} API key ending in ...{key_suffix}")
                return True
                
        return False


# Simplified interface functions
def init_api_manager() -> MultiAPIManager:
    """Initialize the API manager"""
    return MultiAPIManager()

async def chat_completion(prompt: str, provider: str = 'openai', model: str = None) -> str:
    """Simple chat completion function"""
    manager = init_api_manager()
    
    messages = [{"role": "user", "content": prompt}]
    
    # Set default models
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
        if provider == 'openai' or provider == 'deepseek':
            return result['response'].choices[0].message.content
        elif provider == 'anthropic':
            return result['response'].content[0].text
        elif provider == 'google':
            return result['response'].text
        else:
            return str(result['response'])
            
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
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

if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize manager
        manager = init_api_manager()
        
        # Show usage stats
        print_usage_stats()
        
        # Test a simple request
        print("\n🧪 Testing API request...")
        try:
            response = await chat_completion("Hello, how are you?", provider='openai')
            print(f"Response: {response}")
        except Exception as e:
            print(f"Test failed: {e}")
    
    asyncio.run(main())