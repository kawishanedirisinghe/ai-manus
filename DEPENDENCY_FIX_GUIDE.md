# AI Manus - Dependency Fix Guide

## Problem Fixed

The original error was:
```
❌ Failed to install dependencies: Command '['/home/runner/workspace/.pythonlibs/bin/python3', '-m', 'pip', 'install', '--user', 'requests>=2.31.0']' returned non-zero exit status 1.
```

This was caused by an **externally-managed Python environment** that prevents standard pip installations for security reasons.

## Root Cause

Modern Python environments (especially in containers, Nix, or managed systems) implement PEP 668, which prevents pip from installing packages directly to avoid conflicts with system package managers.

The error occurs when trying to install packages with:
```bash
pip install --user package_name
```

In externally-managed environments, this fails with:
```
error: externally-managed-environment
```

## Solutions Implemented

### 1. Updated `simple_setup.py`

The setup script now tries multiple installation methods in order:

1. **Standard user installation** (`--user`)
2. **User installation with system override** (`--user --break-system-packages`)
3. **System installation with override** (`--break-system-packages`)

### 2. Created `fix_dependencies.py`

A standalone script that:
- Detects the Python environment type
- Checks existing packages
- Tries multiple installation methods
- Provides fallback options
- Verifies installations work correctly

## How to Use

### Option 1: Run the Simple Setup (Recommended)
```bash
python3 simple_setup.py
```

### Option 2: Use the Dependency Fix Script
```bash
python3 fix_dependencies.py
```

### Option 3: Manual Installation
```bash
# For externally-managed environments
pip install --break-system-packages requests>=2.31.0 aiohttp>=3.8.0 python-dotenv>=1.0.0 rich>=13.0.0

# Or with user flag
pip install --user --break-system-packages requests>=2.31.0 aiohttp>=3.8.0 python-dotenv>=1.0.0 rich>=13.0.0
```

## Verification

After installation, verify packages work:

```bash
python3 -c "import requests; print('✅ requests version:', requests.__version__)"
python3 -c "import aiohttp; print('✅ aiohttp version:', aiohttp.__version__)"
python3 -c "import dotenv; print('✅ python-dotenv available')"
python3 -c "from rich.console import Console; Console().print('✅ rich working', style='bold green')"
```

## Key Changes Made

### 1. Enhanced Error Handling
- Multiple fallback installation methods
- Better error detection and reporting
- Graceful degradation when installations fail

### 2. Environment Detection
- Automatic detection of externally-managed environments
- Appropriate installation method selection
- Clear user feedback about environment type

### 3. Improved Verification
- Uses subprocess calls to avoid import cache issues
- Tests actual package functionality
- Provides clear success/failure feedback

## Files Modified

1. **`simple_setup.py`** - Updated `install_dependencies_nix()` function
2. **`fix_dependencies.py`** - New standalone dependency fix script
3. **`DEPENDENCY_FIX_GUIDE.md`** - This documentation

## Common Issues and Solutions

### Issue: "externally-managed-environment"
**Solution:** Use `--break-system-packages` flag

### Issue: Packages install but can't be imported
**Solution:** Check Python path and user site-packages directory

### Issue: Permission denied
**Solution:** Use `--user` flag or run with appropriate permissions

### Issue: Network/timeout errors
**Solution:** Check internet connection and try again

## Prevention

To avoid similar issues in the future:

1. **Always test in the target environment** before deployment
2. **Use virtual environments** when possible
3. **Document environment requirements** clearly
4. **Provide multiple installation methods** as fallbacks
5. **Test package imports** after installation

## Success Indicators

When everything is working correctly, you should see:
```
🎉 SUCCESS: All dependencies are now available!
✅ You can now run your AI Manus application
```

And be able to run:
```bash
python3 start.py status
```

Without dependency-related errors (Docker errors are separate and expected if Docker isn't installed).