#!/usr/bin/env python3
"""
Docker Management Script - Python Version
Combines functionality of run.sh, dev.sh, and build.sh with enhanced features
"""

import os
import sys
import subprocess
import argparse
import logging
from typing import List, Optional
import shutil
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DockerManager:
    """Manages Docker operations with multiple compose file support"""
    
    def __init__(self):
        self.compose_cmd = self._detect_compose_command()
        self.compose_files = {
            'production': 'docker-compose.yml',
            'development': 'docker-compose-development.yml',
            'example': 'docker-compose-example.yml'
        }
    
    def _detect_compose_command(self) -> str:
        """Detect which Docker Compose command to use"""
        # Check for docker compose (newer version)
        try:
            result = subprocess.run(['docker', 'compose', 'version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Using 'docker compose' command")
                return 'docker compose'
        except FileNotFoundError:
            pass
        
        # Check for docker-compose (legacy version)
        try:
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Using 'docker-compose' command")
                return 'docker-compose'
        except FileNotFoundError:
            pass
        
        logger.error("Error: Neither 'docker compose' nor 'docker-compose' command found")
        sys.exit(1)
    
    def _check_file_exists(self, filepath: str) -> bool:
        """Check if compose file exists"""
        if not os.path.exists(filepath):
            logger.error(f"Error: Compose file {filepath} not found")
            return False
        return True
    
    def run_compose(self, environment: str = 'production', args: List[str] = None) -> int:
        """Run docker compose with specified environment"""
        compose_file = self.compose_files.get(environment)
        if not compose_file:
            logger.error(f"Unknown environment: {environment}")
            return 1
        
        if not self._check_file_exists(compose_file):
            return 1
        
        cmd = self.compose_cmd.split() + ['-f', compose_file]
        if args:
            cmd.extend(args)
        
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd)
            return result.returncode
        except KeyboardInterrupt:
            logger.info("Operation interrupted by user")
            return 130
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return 1
    
    def build_with_buildx(self, args: List[str] = None) -> int:
        """Build using docker buildx"""
        # Set environment variable for buildx
        env = os.environ.copy()
        env['BUILDX_NO_DEFAULT_ATTESTATIONS'] = '1'
        
        cmd = ['docker', 'buildx', 'bake']
        if args:
            cmd.extend(args)
        
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, env=env)
            return result.returncode
        except KeyboardInterrupt:
            logger.info("Build interrupted by user")
            return 130
        except Exception as e:
            logger.error(f"Error during build: {e}")
            return 1
    
    def status(self, environment: str = 'production') -> int:
        """Show status of containers"""
        return self.run_compose(environment, ['ps'])
    
    def logs(self, environment: str = 'production', service: str = None, follow: bool = False) -> int:
        """Show logs for services"""
        args = ['logs']
        if follow:
            args.append('-f')
        if service:
            args.append(service)
        
        return self.run_compose(environment, args)
    
    def stop_all(self, environment: str = 'production') -> int:
        """Stop all services"""
        return self.run_compose(environment, ['down'])
    
    def restart(self, environment: str = 'production', service: str = None) -> int:
        """Restart services"""
        args = ['restart']
        if service:
            args.append(service)
        
        return self.run_compose(environment, args)

class ReplitManager:
    """Manages Replit-specific configurations and deployments"""
    
    def __init__(self):
        self.replit_config = {
            "language": "python3",
            "run": "python main.py",
            "entrypoint": "main.py",
            "hidden": [".config", ".pythonlibs"],
            "compile": "",
            "modules": ["python3", "nodejs-18", "docker"]
        }
        
        self.nix_config = """
{ pkgs }: {
  deps = [
    pkgs.python310Full
    pkgs.replitPackages.prybar-python310
    pkgs.replitPackages.stderred
    pkgs.docker
    pkgs.docker-compose
    pkgs.nodejs-18_x
    pkgs.nodePackages.npm
    pkgs.git
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      # Needed for pandas / numpy
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      # Needed for pygame
      pkgs.glib
      # Needed for matplotlib
      pkgs.xorg.libX11
    ];
    PYTHONHOME = "${pkgs.python310Full}";
    PYTHONBIN = "${pkgs.python310Full}/bin/python3.10";
    LANG = "en_US.UTF-8";
    STDERREDBIN = "${pkgs.replitPackages.stderred}/bin/stderred";
    PRYBAR_PYTHON_BIN = "${pkgs.replitPackages.prybar-python310}/bin/prybar-python310";
  };
}
"""
    
    def create_replit_config(self):
        """Create .replit configuration file"""
        with open('.replit', 'w') as f:
            for key, value in self.replit_config.items():
                if isinstance(value, list):
                    f.write(f'{key} = {json.dumps(value)}\n')
                else:
                    f.write(f'{key} = "{value}"\n')
        
        logger.info("Created .replit configuration file")
    
    def create_nix_config(self):
        """Create replit.nix configuration file"""
        with open('replit.nix', 'w') as f:
            f.write(self.nix_config)
        
        logger.info("Created replit.nix configuration file")
    
    def create_main_runner(self):
        """Create main.py runner for Replit"""
        main_content = '''#!/usr/bin/env python3
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
'''
        
        with open('main.py', 'w') as f:
            f.write(main_content)
        
        logger.info("Created main.py runner file")

def main():
    """Main entry point for docker_manager.py"""
    parser = argparse.ArgumentParser(description='Docker Management Script')
    parser.add_argument('command', choices=['run', 'dev', 'build', 'status', 'logs', 'stop', 'setup-replit'],
                       help='Command to execute')
    parser.add_argument('--env', '-e', choices=['production', 'development', 'example'], 
                       default='production', help='Environment to use')
    parser.add_argument('--service', '-s', help='Specific service to target')
    parser.add_argument('--follow', '-f', action='store_true', help='Follow log output')
    parser.add_argument('args', nargs='*', help='Additional arguments to pass')
    
    args = parser.parse_args()
    
    if args.command == 'setup-replit':
        replit_manager = ReplitManager()
        replit_manager.create_replit_config()
        replit_manager.create_nix_config() 
        replit_manager.create_main_runner()
        logger.info("Replit setup completed!")
        return
    
    manager = DockerManager()
    
    if args.command == 'run':
        sys.exit(manager.run_compose(args.env, args.args or ['up', '-d']))
    elif args.command == 'dev':
        sys.exit(manager.run_compose('development', args.args or ['up', '-d']))
    elif args.command == 'build':
        sys.exit(manager.build_with_buildx(args.args))
    elif args.command == 'status':
        sys.exit(manager.status(args.env))
    elif args.command == 'logs':
        sys.exit(manager.logs(args.env, args.service, args.follow))
    elif args.command == 'stop':
        sys.exit(manager.stop_all(args.env))

if __name__ == "__main__":
    main()