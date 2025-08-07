from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Dict, Any, Optional
import json
from pathlib import Path


class Settings(BaseSettings):
    
    # Multi-API Key configuration
    api_config_path: str = "api_config.json"
    use_multi_api_manager: bool = True
    
    # Legacy single API key configuration (for backward compatibility)
    api_key: str | None = None
    api_base: str = "https://api.deepseek.com/v1"
    
    # Model configuration
    model_name: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    # MongoDB configuration
    mongodb_uri: str = "mongodb://mongodb:27017"
    mongodb_database: str = "manus"
    mongodb_username: str | None = None
    mongodb_password: str | None = None
    
    # Redis configuration
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    
    # Sandbox configuration
    sandbox_address: str | None = None
    sandbox_image: str | None = None
    sandbox_name_prefix: str | None = None
    sandbox_ttl_minutes: int | None = 30
    sandbox_network: str | None = None  # Docker network bridge name
    sandbox_chrome_args: str | None = ""
    sandbox_https_proxy: str | None = None
    sandbox_http_proxy: str | None = None
    sandbox_no_proxy: str | None = None
    
    # Search engine configuration
    search_provider: str | None = None  # "google", "baidu"
    google_search_api_key: str | None = None
    google_search_engine_id: str | None = None
    
    # MCP configuration
    mcp_config_path: str = "/etc/mcp.json"
    
    # Logging configuration
    log_level: str = "INFO"
    
    # Multi-API provider preferences
    preferred_provider: str = "openai"  # Default provider to use
    fallback_providers: List[str] = ["deepseek", "anthropic", "google"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    def validate(self):
        """Validate configuration"""
        if self.use_multi_api_manager:
            # Check if API config file exists
            api_config_path = Path(self.api_config_path)
            if not api_config_path.exists():
                print(f"Warning: API config file not found at {api_config_path}")
                print("Multi-API manager will create a default configuration.")
                return
                
            try:
                with open(api_config_path, 'r') as f:
                    config = json.load(f)
                    
                # Check if at least one provider has valid keys
                api_keys = config.get('api_keys', {})
                has_valid_keys = False
                
                for provider, keys in api_keys.items():
                    if keys and any(
                        key.get('key', '').startswith(('sk-', 'your-')) and 
                        not key.get('key', '').endswith('key-1') 
                        for key in keys
                    ):
                        has_valid_keys = True
                        break
                        
                if not has_valid_keys:
                    print("Warning: No valid API keys found in configuration.")
                    print("Please edit api_config.json and add your real API keys.")
                    
            except Exception as e:
                print(f"Warning: Error reading API config: {e}")
        else:
            # Legacy validation
            if not self.api_key:
                raise ValueError("API key is required when not using multi-API manager")
                
    def get_api_keys_config(self) -> Dict[str, Any]:
        """Get API keys configuration for multi-API manager"""
        if not self.use_multi_api_manager:
            return {}
            
        api_config_path = Path(self.api_config_path)
        if not api_config_path.exists():
            return {}
            
        try:
            with open(api_config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading API config: {e}")
            return {}
            
    def get_preferred_providers(self) -> List[str]:
        """Get list of providers in order of preference"""
        providers = [self.preferred_provider]
        providers.extend([p for p in self.fallback_providers if p not in providers])
        return providers


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings 
