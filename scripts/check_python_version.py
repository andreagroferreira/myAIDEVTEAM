#!/usr/bin/env python3
"""
Check Python version and provide guidance for CFTeam setup
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version meets requirements"""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"🐍 Current Python version: {version_str}")
    print(f"📍 Python executable: {sys.executable}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("\n⚠️  WARNING: Python 3.10+ is required for latest CrewAI")
        print("\n🔧 Options to resolve this:")
        print("\n1. OPTION A - Upgrade Python (Recommended):")
        print("   brew install python@3.12")
        print("   python3.12 -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        
        print("\n2. OPTION B - Use CrewAI for Python 3.9:")
        print("   pip install -r requirements-py39.txt")
        print("   Note: This uses older CrewAI version with limited features")
        
        print("\n3. OPTION C - Use pyenv to manage Python versions:")
        print("   brew install pyenv")
        print("   pyenv install 3.12.0")
        print("   pyenv local 3.12.0")
        print("   python -m venv venv")
        print("   source venv/bin/activate")
        
        return False
    else:
        print("✅ Python version is compatible!")
        return True


def check_brew_python():
    """Check available Python versions via Homebrew"""
    try:
        result = subprocess.run(['brew', 'list', '--versions'], 
                              capture_output=True, text=True)
        pythons = [line for line in result.stdout.split('\n') 
                  if line.startswith('python@')]
        
        if pythons:
            print("\n📦 Available Python versions via Homebrew:")
            for python in pythons:
                print(f"   {python}")
    except:
        pass


if __name__ == "__main__":
    compatible = check_python_version()
    check_brew_python()
    
    if not compatible:
        sys.exit(1)