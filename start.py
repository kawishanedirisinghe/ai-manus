#!/usr/bin/env python3
"""
Simple runner for AI Manus
"""

import os
import sys
import subprocess
from pathlib import Path

def get_python():
    """Get Python executable"""
    return sys.executable

def main():
    """Main runner"""
    print("🚀 Starting AI Manus...")
    
    # Get Python executable
    python_exe = get_python()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        args = sys.argv[2:]
        
        if command == "dev":
            # Development mode
            subprocess.run([python_exe, "docker_manager.py", "dev"] + args)
        elif command == "docs":
            # Update documentation
            subprocess.run([python_exe, "update_doc.py"] + args)
        elif command == "status":
            # Check status
            subprocess.run([python_exe, "main.py", "status"] + args)
        else:
            # Pass through to main.py
            subprocess.run([python_exe, "main.py", command] + args)
    else:
        # Default: start in production mode
        subprocess.run([python_exe, "main.py", "run", "prod"])

if __name__ == "__main__":
    main()