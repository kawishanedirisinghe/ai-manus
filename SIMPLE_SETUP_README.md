# 🚀 Multi-API Key Manager - Simple Setup

A powerful, easy-to-use system for managing multiple API keys across different AI providers with automatic rotation, usage tracking, and intelligent fallback.

## ✨ Features

- **🔄 Automatic Key Rotation**: Distribute load across multiple API keys
- **📊 Usage Tracking**: Monitor daily usage with automatic reset
- **🛡️ Intelligent Fallback**: Automatically switch providers if one fails  
- **🎯 Multiple Providers**: OpenAI, Anthropic, Google Gemini, and DeepSeek
- **⚙️ Easy Configuration**: JSON-based configuration with sensible defaults
- **🔒 Rate Limiting**: Built-in protection against hitting API limits
- **📈 Statistics**: Real-time usage statistics and logging

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)

```bash
python setup.py
```

### Option 2: Manual Setup

```bash
# Install packages
pip install -r requirements.txt

# Run main application
python main.py
```

That's it! The system will:
1. ✅ Check and install required packages
2. ⚙️ Create default configuration files
3. 🎯 Launch the interactive interface

## 📝 Configuration

After setup, edit `api_config.json` with your real API keys:

```json
{
  "api_keys": {
    "openai": [
      {
        "key": "sk-proj-your-real-openai-key",
        "provider": "openai",
        "base_url": "https://api.openai.com/v1",
        "daily_limit": 1000,
        "current_usage": 0,
        "last_reset": "2024-01-15",
        "is_active": true,
        "priority": 1
      }
    ],
    "anthropic": [
      {
        "key": "sk-ant-your-real-anthropic-key",
        "provider": "anthropic",
        "base_url": "https://api.anthropic.com",
        "daily_limit": 1000,
        "current_usage": 0,
        "last_reset": "2024-01-15",
        "is_active": true,
        "priority": 1
      }
    ],
    "google": [
      {
        "key": "AIza-your-real-google-key",
        "provider": "google",
        "base_url": null,
        "daily_limit": 1000,
        "current_usage": 0,
        "last_reset": "2024-01-15",
        "is_active": true,
        "priority": 1
      }
    ],
    "deepseek": [
      {
        "key": "sk-your-real-deepseek-key",
        "provider": "deepseek",
        "base_url": "https://api.deepseek.com/v1",
        "daily_limit": 1000,
        "current_usage": 0,
        "last_reset": "2024-01-15",
        "is_active": true,
        "priority": 1
      }
    ]
  },
  "settings": {
    "auto_rotate": true,
    "rotation_strategy": "round_robin",
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "enable_usage_tracking": true,
    "daily_reset_hour": 0
  }
}
```

## 🎮 Usage

### Interactive Interface

```bash
python main.py
```

The interactive menu provides:
- 💬 **Chat with AI**: Direct conversation with any provider
- 📊 **Usage Statistics**: Real-time usage tracking
- ⚙️ **Key Management**: Add, remove, enable/disable keys
- 🧪 **Provider Testing**: Test all providers at once
- 🏃 **Backend Server**: Launch the full backend
- 🌐 **Frontend Server**: Start the web interface

### Programmatic Usage

```python
import asyncio
from multi_api_manager import chat_completion, print_usage_stats

async def main():
    # Simple chat
    response = await chat_completion("Hello!", provider='openai')
    print(response)
    
    # Show statistics
    print_usage_stats()

asyncio.run(main())
```

### Backend Integration

The system automatically integrates with the existing backend. The LLM service will:
1. 🔄 Try the preferred provider first
2. 🛡️ Automatically fallback to other providers if needed
3. 📊 Track usage across all keys
4. ⚖️ Load balance requests

## 🔧 Configuration Options

### Rotation Strategies

- **`round_robin`**: Evenly distribute requests across keys
- **`priority`**: Use high-priority keys first
- **`usage_based`**: Prefer keys with lowest usage

### Provider Settings

- **`daily_limit`**: Maximum requests per day per key
- **`priority`**: Higher numbers = higher priority
- **`is_active`**: Enable/disable individual keys

### Global Settings

- **`auto_rotate`**: Enable automatic key rotation
- **`retry_attempts`**: Number of retries on failure
- **`retry_delay`**: Delay between retries (seconds)
- **`enable_usage_tracking`**: Track daily usage statistics

## 📊 Monitoring

### Usage Statistics

View real-time statistics:
```bash
python main.py
# Choose option 2: Show Usage Statistics
```

### Log Files

- **`api_usage.log`**: Detailed API usage logs
- **`usage_stats.json`**: Daily usage statistics

## 🛠️ Advanced Usage

### Adding Multiple Keys

You can add multiple keys for the same provider:

```json
"openai": [
  {
    "key": "sk-proj-key-1",
    "daily_limit": 1000,
    "priority": 1
  },
  {
    "key": "sk-proj-key-2", 
    "daily_limit": 500,
    "priority": 2
  }
]
```

### Custom Base URLs

For OpenAI-compatible APIs:

```json
{
  "key": "your-custom-key",
  "provider": "openai",
  "base_url": "https://custom-api.example.com/v1"
}
```

### Environment Variables

Override settings with environment variables:
```bash
export PREFERRED_PROVIDER=anthropic
export USE_MULTI_API_MANAGER=true
python main.py
```

## 🔄 Running Different Components

### Full Backend Server
```bash
python main.py
# Choose option 5: Run Backend Server
```

### Frontend Development Server
```bash
python main.py
# Choose option 6: Run Frontend Server
```

### Standalone API Manager
```bash
python multi_api_manager.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Error**: Make sure all packages are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Issues**: Check that keys are valid and properly formatted

3. **Provider Failures**: The system will automatically try other providers

4. **Permission Issues**: Make sure Python has write access for config files

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📁 File Structure

```
project/
├── main.py                    # Main interface
├── multi_api_manager.py       # API management core
├── setup.py                   # Setup script
├── requirements.txt           # Dependencies
├── api_config.json           # API configuration
├── api_usage.log             # Usage logs
├── usage_stats.json          # Statistics
├── backend/                  # Backend server
├── frontend/                 # Frontend interface
└── docs/                     # Documentation
```

## 🎯 Benefits

- **💰 Cost Optimization**: Distribute usage across multiple keys
- **🚀 High Availability**: Automatic fallback ensures uptime
- **📊 Usage Control**: Monitor and limit daily usage
- **🔧 Easy Management**: Simple configuration and monitoring
- **🎮 User Friendly**: Interactive interface for all operations

## 🆘 Support

1. Check the logs in `api_usage.log`
2. Run the test function: `python multi_api_manager.py`
3. Use the built-in documentation: `python main.py` → option 7

## 🚀 Ready to Start?

```bash
python setup.py
# Follow the prompts
# Edit api_config.json with your keys
python main.py
# Start chatting!
```

That's it! You now have a powerful multi-API system that automatically handles key rotation, usage tracking, and provider fallback. Perfect for production use or development! 🎉