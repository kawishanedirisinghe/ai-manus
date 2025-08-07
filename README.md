# AI Manus

**A general-purpose AI Agent system with modular architecture**

English | [中文](README_zh.md) | [Documents](https://docs.ai-manus.com/#/en/)

[![GitHub stars](https://img.shields.io/github/stars/simpleyyt/ai-manus?style=social)](https://github.com/simpleyyt/ai-manus/stargazers)
&ensp;
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI Manus is a general-purpose AI Agent system that supports running various tools and operations in a sandbox environment with multi-API key management and automatic rotation.

🏗️ **Recently Organized** - Project structure has been cleaned and organized for better maintainability!

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/simpleyyt/ai-manus.git
cd ai-manus

# Copy environment template and configure your API keys
cp .env.example .env
# Edit .env file with your actual API keys

# Run setup
python main.py setup
```

### 2. Choose Your Deployment Method

**Option A: Docker Compose (Recommended)**
```bash
python main.py docker prod
```

**Option B: Development Mode**
```bash
# Start backend
python main.py backend

# In another terminal, start frontend
python main.py frontend
```

**Option C: Individual Components**
```bash
python main.py api        # API manager tool
python main.py status     # Check system status
```

## 📁 Project Structure

```
ai-manus/
├── 📂 backend/           # FastAPI backend service
├── 📂 frontend/          # Vue.js frontend application  
├── 📂 sandbox/           # Docker sandbox environment
├── 📂 mockserver/        # Mock API server for testing
├── 📂 docs/              # Documentation
├── 📂 scripts/           # Organized scripts
│   ├── 📂 setup/         # Setup and installation scripts
│   ├── 📂 docker/        # Docker management scripts
│   └── 📂 dev/           # Development tools
├── 📂 tools/             # Utility tools
│   └── multi_api_manager.py  # Multi-API key manager
├── 📂 config/            # Configuration files
│   └── 📂 examples/      # Example configurations
├── main.py               # Main entry point
├── requirements.txt      # Consolidated dependencies
└── .env.example          # Environment template
```

## 🔑 API Key Configuration

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your API keys:**
   ```env
   # Google API Keys (Gemini)
   GOOGLE_API_KEY_1=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   GOOGLE_API_KEY_2=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   
   # OpenAI API Keys  
   OPENAI_API_KEY_1=sk-your-openai-key-1
   
   # Anthropic API Keys
   ANTHROPIC_API_KEY_1=sk-ant-your-anthropic-key-1
   ```

3. **Configure API limits and settings in `config/examples/` (optional)**

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **🔐 Multi-API Management** | Support for OpenAI, Anthropic, Google (Gemini), and DeepSeek with automatic key rotation |
| **⚙️ Modular Architecture** | Clean separation between backend, frontend, sandbox, and tools |
| **🐳 Docker Support** | Complete Docker Compose setup for development and production |
| **🛡️ Sandbox Environment** | Secure code execution environment with Docker isolation |
| **📊 Usage Tracking** | Real-time API usage monitoring and statistics |
| **🌐 Web Interface** | Modern Vue.js frontend with real-time updates |
| **🔧 Developer Tools** | Comprehensive tooling for development and debugging |

## 🖥️ Available Commands

```bash
python main.py setup          # Run initial setup
python main.py backend        # Start backend service  
python main.py frontend       # Start frontend dev server
python main.py docker dev     # Start with Docker (development)
python main.py docker prod    # Start with Docker (production)
python main.py api            # Run API manager tool
python main.py status         # Show system status
```

## 🐳 Docker Deployment

### Development
```bash
python main.py docker dev
```

### Production  
```bash
python main.py docker prod
```

The system will be available at:
- 🌐 Frontend: http://localhost:5173
- 🔧 Backend API: http://localhost:8000
- 📊 API Documentation: http://localhost:8000/docs

## 🛠️ Development

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend development)
- Docker & Docker Compose (for containerized deployment)

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start backend in development mode
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend in development mode  
cd frontend
npm install
npm run dev
```

## 📊 API Usage Monitoring

The system provides comprehensive API usage tracking:

- **Real-time Statistics** - Monitor API calls, success rates, and response times
- **Key Rotation** - Automatic rotation when limits are reached
- **Usage Limits** - Configurable daily/hourly limits per API key
- **Fallback Support** - Automatic failover to backup keys/providers

## 🔧 Tools & Scripts

### Setup Scripts (`scripts/setup/`)
- `setup.py` - Main setup script
- `simple_setup.py` - Simplified setup with environment variables
- `setup_and_run.py` - One-click setup and run

### Docker Scripts (`scripts/docker/`)
- `docker_manager.py` - Docker management utility

### Development Scripts (`scripts/dev/`)
- Development and maintenance tools

### API Manager (`tools/`)
- `multi_api_manager.py` - Standalone API key management tool

## 🔒 Security

- **🚫 No Hardcoded Keys** - All API keys loaded from environment variables
- **🛡️ Sandbox Isolation** - Code execution in isolated Docker containers
- **🔐 Secure Configuration** - Example configs with placeholder values
- **📝 Environment Templates** - Safe `.env.example` for sharing

## 📝 Recent Changes

### ✨ Organization & Cleanup (Latest)
- **🗂️ Structured Directories** - Organized scripts, tools, and configs
- **🧹 Removed Duplicates** - Consolidated multiple setup scripts
- **🔒 Security Fix** - Removed hardcoded API keys, added environment variables
- **📦 Consolidated Dependencies** - Single `requirements.txt` for entire project
- **🚀 Improved Entry Point** - Clean `main.py` with clear command structure

### 🎯 Previous Features
- Multi-API key management with automatic rotation
- FastAPI backend with agent services
- Vue.js frontend with real-time updates
- Docker sandbox environment
- MongoDB/Redis session management
- Multi-language support (English/Chinese)

## 📖 Documentation

- [📚 Full Documentation](https://docs.ai-manus.com/#/en/)
- [🚀 Quick Start Guide](docs/quick_start.md)
- [🏗️ Architecture Overview](docs/architecture.md)
- [🛠️ Development Guide](docs/development.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [🌟 GitHub Repository](https://github.com/simpleyyt/ai-manus)
- [📖 Documentation](https://docs.ai-manus.com)
- [💬 QQ Group (1005477581)](https://qun.qq.com/universal-share/share?ac=1&authKey=p4X3Da5iMpR4liAenxwvhs7IValPKiCFtUevRlJouz9qSTSZsMnPJc3hzsJjgQYv&busi_data=eyJncm91cENvZGUiOiIxMDA1NDc3NTgxIiwidG9rZW4iOiJNZmUrTmQ0UzNDZDNqNDFVdjVPS1VCRkJGRWVlV0R3RFJSRVFoZDAwRjFDeUdUM0t6aUIyczlVdzRjV1BYN09IIiwidWluIjoiMzQyMjExODE1In0%3D&data=C3B-E6BlEbailV32co77iXL5vxPIhtD9y_itWLSq50hKqosO_55_isOZym2Faaq4hs9-517tUY8GSWaDwPom-A&svctype=4&tempid=h5_group_info)

---

**✨ AI Manus - Your Complete AI Agent Solution!** 
