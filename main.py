#!/usr/bin/env python3
"""
Main runner for Replit deployment
Provides a unified interface for all operations
"""

import sys
import os
from docker_manager import DockerManager, ReplitManager
from update_doc import DocumentUpdater

def main():
    """Main entry point for Replit"""
    if len(sys.argv) < 2:
        print("Usage: python main.py [command] [options]")
        print("Commands:")
        print("  update-docs    - Update documentation")
        print("  run [env]      - Run docker compose (env: prod, dev, example)")
        print("  build          - Build with docker buildx")
        print("  status [env]   - Show container status")
        print("  logs [env]     - Show logs")
        print("  stop [env]     - Stop containers")
        print("  setup-replit   - Setup Replit configuration")
        return
    
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if command == "update-docs":
        updater = DocumentUpdater()
        updater.update_documents()
    
    elif command == "run":
        env = args[0] if args else "production"
        env_map = {"prod": "production", "dev": "development", "example": "example"}
        env = env_map.get(env, env)
        
        manager = DockerManager()
        remaining_args = args[1:] if len(args) > 1 else ["up", "-d"]
        sys.exit(manager.run_compose(env, remaining_args))
    
    elif command == "build":
        manager = DockerManager()
        sys.exit(manager.build_with_buildx(args))
    
    elif command == "status":
        env = args[0] if args else "production"
        env_map = {"prod": "production", "dev": "development", "example": "example"}
        env = env_map.get(env, env)
        
        manager = DockerManager()
        sys.exit(manager.status(env))
    
    elif command == "logs":
        env = args[0] if args else "production"
        env_map = {"prod": "production", "dev": "development", "example": "example"}
        env = env_map.get(env, env)
        
        manager = DockerManager()
        service = args[1] if len(args) > 1 else None
        follow = "-f" in args or "--follow" in args
        sys.exit(manager.logs(env, service, follow))
    
    elif command == "stop":
        env = args[0] if args else "production"
        env_map = {"prod": "production", "dev": "development", "example": "example"}
        env = env_map.get(env, env)
        
        manager = DockerManager()
        sys.exit(manager.stop_all(env))
    
    elif command == "setup-replit":
        replit_manager = ReplitManager()
        replit_manager.create_replit_config()
        replit_manager.create_nix_config()
        replit_manager.create_main_runner()
        print("Replit configuration created successfully!")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
