#!/usr/bin/env python3
"""
AI Manus - Main Entry Point
A general-purpose AI Agent system with modular architecture
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Optional

def print_banner():
    """Print AI Manus banner"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                    🤖 AI Manus                          ║
║           General-purpose AI Agent System               ║
║                                                          ║
║  Run with --help for available commands                 ║
╚══════════════════════════════════════════════════════════╝
""")

def run_setup():
    """Run the setup process"""
    setup_script = Path("scripts/setup/setup.py")
    if setup_script.exists():
        subprocess.run([sys.executable, str(setup_script)])
    else:
        print("❌ Setup script not found. Please run from project root.")
        sys.exit(1)

def run_backend():
    """Start the backend service"""
    backend_dir = Path("backend")
    if backend_dir.exists():
        os.chdir(backend_dir)
        subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    else:
        print("❌ Backend directory not found.")
        sys.exit(1)

def run_frontend():
    """Start the frontend development server"""
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        os.chdir(frontend_dir)
        subprocess.run(["npm", "run", "dev"])
    else:
        print("❌ Frontend directory not found.")
        sys.exit(1)

def run_docker(mode: str = "development"):
    """Run using Docker Compose"""
    docker_script = Path("scripts/docker/docker_manager.py")
    if docker_script.exists():
        subprocess.run([sys.executable, str(docker_script), mode])
    else:
        print("❌ Docker manager script not found.")
        sys.exit(1)

def run_api_manager():
    """Run the API manager tool"""
    api_manager = Path("tools/multi_api_manager.py")
    if api_manager.exists():
        subprocess.run([sys.executable, str(api_manager)])
    else:
        print("❌ API manager tool not found.")
        sys.exit(1)

def show_status():
    """Show system status"""
    print("🔍 System Status:")
    
    # Check if setup files exist
    config_files = [
        Path(".env"),
        Path("config.toml"),
        Path("api_config.json")
    ]
    
    for config_file in config_files:
        status = "✅" if config_file.exists() else "❌"
        print(f"  {status} {config_file}")
    
    # Check Docker
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Docker: {result.stdout.strip()}")
        else:
            print("  ❌ Docker: Not available")
    except FileNotFoundError:
        print("  ❌ Docker: Not installed")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Node.js: {result.stdout.strip()}")
        else:
            print("  ❌ Node.js: Not available")
    except FileNotFoundError:
        print("  ❌ Node.js: Not installed")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Manus - General-purpose AI Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py setup          # Run initial setup
  python main.py backend        # Start backend service  
  python main.py frontend       # Start frontend dev server
  python main.py docker dev     # Start with Docker (development)
  python main.py docker prod    # Start with Docker (production)
  python main.py api            # Run API manager tool
  python main.py status         # Show system status

For Docker Compose deployment, see README.md
        """
    )
    
    parser.add_argument(
        "command",
        choices=["setup", "backend", "frontend", "docker", "api", "status"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "mode",
        nargs="?",
        default="development",
        choices=["dev", "development", "prod", "production"],
        help="Mode for docker command (default: development)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Execute command
    if args.command == "setup":
        run_setup()
    elif args.command == "backend":
        run_backend()
    elif args.command == "frontend":
        run_frontend()
    elif args.command == "docker":
        mode_map = {"dev": "development", "prod": "production"}
        mode = mode_map.get(args.mode, args.mode)
        run_docker(mode)
    elif args.command == "api":
        run_api_manager()
    elif args.command == "status":
        show_status()

if __name__ == "__main__":
    main()
