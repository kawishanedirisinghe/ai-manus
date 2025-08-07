#!/usr/bin/env python3
"""
Dependency Fix Script for AI Manus
Handles various Python environment scenarios including externally-managed environments
"""

import os
import sys
import subprocess
import importlib.util

def print_header():
    """Print fix header"""
    print("🔧 AI Manus - Dependency Fix Script")
    print("=" * 50)
    print("🐍 Fixing Python dependency installation issues")
    print()

def check_python():
    """Check Python version and environment"""
    version = sys.version_info
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    print(f"✅ Python executable: {sys.executable}")
    print(f"✅ Python path: {sys.path[0] if sys.path else 'Not available'}")
    
    # Check if environment is externally managed
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "list"
        ], capture_output=True, text=True, timeout=10)
        
        if "externally-managed-environment" in result.stderr:
            print("⚠️  Environment is externally managed")
            return "externally-managed"
        else:
            print("✅ Environment allows pip installations")
            return "normal"
    except Exception as e:
        print(f"⚠️  Could not determine environment type: {e}")
        return "unknown"

def check_existing_packages():
    """Check which packages are already available"""
    print("🔍 Checking existing packages...")
    
    required_packages = {
        "requests": "requests",
        "aiohttp": "aiohttp", 
        "dotenv": "python-dotenv",
        "rich": "rich"
    }
    
    available = {}
    for import_name, package_name in required_packages.items():
        try:
            # Use a fresh Python process to avoid import cache issues
            test_code = f"import {import_name}; print('OK')"
            result = subprocess.run([
                sys.executable, "-c", test_code
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and "OK" in result.stdout:
                print(f"   ✅ {package_name} is available")
                available[package_name] = True
            else:
                print(f"   ❌ {package_name} is missing")
                available[package_name] = False
        except Exception as e:
            print(f"   ❌ {package_name} is missing (error: {e})")
            available[package_name] = False
    
    return available

def install_with_method(packages, method_args, method_name):
    """Try to install packages with a specific method"""
    print(f"   Trying {method_name}...")
    
    for package in packages:
        try:
            cmd = method_args + [package]
            print(f"   Installing {package}...")
            result = subprocess.run(
                cmd,
                check=True, 
                capture_output=True, 
                text=True,
                timeout=60
            )
            print(f"   ✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            if "externally-managed-environment" in str(e.stderr):
                print(f"   Environment is externally managed, trying next method...")
                return False
            raise e
        except subprocess.TimeoutExpired:
            print(f"   ❌ Installation of {package} timed out")
            return False
    
    return True

def fix_dependencies():
    """Fix dependency installation issues"""
    print("📦 Attempting to fix dependencies...")
    
    # Essential packages
    essential_packages = [
        "requests>=2.31.0",
        "aiohttp>=3.8.0", 
        "python-dotenv>=1.0.0",
        "rich>=13.0.0"
    ]
    
    # Check what's already available
    available = check_existing_packages()
    missing_packages = [pkg for pkg in essential_packages 
                       if not any(avail for name, avail in available.items() 
                                 if name.split('>=')[0] in pkg)]
    
    if not missing_packages:
        print("   ✅ All required packages are already available!")
        return True
    
    print(f"   Need to install: {missing_packages}")
    
    # Installation methods in order of preference
    installation_methods = [
        {
            "name": "standard user installation",
            "args": [sys.executable, "-m", "pip", "install", "--user"]
        },
        {
            "name": "user installation with --break-system-packages",
            "args": [sys.executable, "-m", "pip", "install", "--user", "--break-system-packages"]
        },
        {
            "name": "system installation with --break-system-packages", 
            "args": [sys.executable, "-m", "pip", "install", "--break-system-packages"]
        },
        {
            "name": "force installation with --break-system-packages --force-reinstall",
            "args": [sys.executable, "-m", "pip", "install", "--break-system-packages", "--force-reinstall"]
        }
    ]
    
    # Try each installation method
    for method in installation_methods:
        try:
            if install_with_method(missing_packages, method["args"], method["name"]):
                print(f"   ✅ Dependencies installed successfully using {method['name']}")
                return True
        except subprocess.CalledProcessError:
            continue
    
    print("   ⚠️  All installation methods failed")
    return False

def create_requirements_fallback():
    """Create a requirements.txt with only essential packages"""
    print("📝 Creating minimal requirements.txt...")
    
    minimal_requirements = """# Minimal requirements for AI Manus
requests>=2.31.0
aiohttp>=3.8.0
python-dotenv>=1.0.0
rich>=13.0.0
"""
    
    try:
        with open("requirements-minimal.txt", "w") as f:
            f.write(minimal_requirements)
        print("   ✅ Created requirements-minimal.txt")
        
        print("   💡 You can try installing manually with:")
        print("   pip install --break-system-packages -r requirements-minimal.txt")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create requirements file: {e}")
        return False

def main():
    """Main fix function"""
    print_header()
    
    # Check Python environment
    env_type = check_python()
    print()
    
    # Try to fix dependencies
    success = fix_dependencies()
    print()
    
    if not success:
        print("🔧 Creating fallback options...")
        create_requirements_fallback()
        print()
    
    # Final verification
    print("🔍 Final verification...")
    available = check_existing_packages()
    all_available = all(available.values())
    
    print()
    if all_available:
        print("🎉 SUCCESS: All dependencies are now available!")
        print("✅ You can now run your AI Manus application")
    else:
        print("⚠️  Some dependencies are still missing")
        print("💡 Try running the application anyway - it might work with system packages")
        print("💡 Or try manual installation with --break-system-packages flag")
    
    return all_available

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)