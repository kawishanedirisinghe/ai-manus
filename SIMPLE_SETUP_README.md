# 🚀 AI Manus - Simplified Setup

## ✨ One-Click Setup

This project has been simplified for easy setup in Nix environments (like Replit). Everything is pre-configured with your API keys.

### 🎯 Quick Start

#### ⚡ Ultimate One-Button (Recommended)
```bash
python3 setup_and_run.py
```
**This single command does everything**: setup + configuration + start! 🎉

#### 📋 Or Step-by-Step
1. **Run Setup** (One-time only):
   ```bash
   python3 simple_setup.py
   ```

2. **Start Application**:
   ```bash
   python3 start.py
   ```

### 📋 Available Commands

```bash
python3 start.py         # Start in production mode
python3 start.py dev     # Start in development mode
python3 start.py docs    # Update documentation
python3 start.py status  # Check status
```

### 🔑 Pre-configured API Keys

The setup automatically configures **5 Gemini API keys** with:
- **Key 1**: `AIzaSyAwd6PcBM-07xBbbuBqBPc3svJsUMvyc1E`
- **Key 2**: `AIzaSyDwDj4i9tptBolcKGHMlqxMOi_CjisQdJE`
- **Key 3**: `AIzaSyClSfseWKkublCjdZBIq-aYqPoB3jEWj28`
- **Key 4**: `AIzaSyD_ElDcTSosqzd4Dy9L-4ygL3fP2zsWtq0`
- **Key 5**: `AIzaSyAf__tW7KcUD1-uh9RzGg6Y5eS6e3_PNB0`

### 📁 Configuration Files Created

- `config.toml` - Main LLM configuration with all API keys
- `api_config.json` - JSON format API configuration  
- `.env` - Environment variables
- `start.py` - Simple application runner

### 🔄 Rate Limiting & Rotation

Each API key is configured with:
- **5 requests per minute**
- **100 requests per hour** 
- **100 requests per day**
- **Automatic key rotation** when limits are reached

### 🛠️ What the Setup Does

1. ✅ Installs essential Python packages (works with Nix)
2. ✅ Creates configuration files with your API keys
3. ✅ Sets up environment variables
4. ✅ Creates a simple start script
5. ✅ Removes old complex setup files

### 🆘 Troubleshooting

- **Docker errors**: Normal in Nix environments - the app will work without Docker
- **Permission errors**: Run with `python3` instead of `python`
- **Package errors**: The setup installs only essential packages to avoid conflicts

### 🎨 Features

- **Multi-API key support** with automatic rotation
- **Rate limiting** per key
- **Fallback strategy** when keys hit limits
- **Simple one-command startup**
- **Works in Nix/Replit environments**

---

**Previous complex setup files have been removed.** Use this simplified version instead! 🚀