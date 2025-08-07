#!/bin/bash
# AI Manus Setup Script

echo "🚀 AI Manus Environment Setup"
echo "============================"

# Activate virtual environment
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run fix_and_update_all.py first."
    exit 1
fi

# Check if Docker is available
if command -v docker >/dev/null 2>&1; then
    echo "🐳 Docker is available"
    
    # Try to check Docker daemon
    if sudo docker ps >/dev/null 2>&1; then
        echo "✅ Docker daemon is running"
    else
        echo "⚠️ Docker daemon may not be running"
    fi
    
    # Check Docker Compose
    if docker compose version >/dev/null 2>&1; then
        echo "✅ docker compose is available"
    elif docker-compose --version >/dev/null 2>&1; then
        echo "✅ docker-compose is available"
    else
        echo "❌ Neither docker compose nor docker-compose found"
    fi
else
    echo "❌ Docker not found"
fi

echo ""
echo "🎯 Environment ready! You can now run your applications."
echo "📋 Common commands:"
echo "   • python main.py           - Run main application"
echo "   • sudo docker compose up  - Start Docker services"
echo "   • python setup_and_run.py - Run setup and start"
