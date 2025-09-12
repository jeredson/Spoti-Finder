#!/usr/bin/env python3
"""
Setup script for Spotify Music Recommender Based on Human Emotion
This script helps set up the project environment and dependencies
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 70)
    print("🎵 SPOTIFY MUSIC RECOMMENDER SETUP 🎵")
    print("=" * 70)
    print("Setting up your emotion-based music recommendation system...")
    print()

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("⚠️  This project requires Python 3.8 or higher")
        print("Please upgrade your Python installation")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_virtual_environment():
    """Create virtual environment"""
    print("\n🏗️  Setting up virtual environment...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        
        # Print activation instructions
        if platform.system() == "Windows":
            activate_cmd = "venv\\Scripts\\activate"
        else:
            activate_cmd = "source venv/bin/activate"
        
        print(f"💡 To activate: {activate_cmd}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    try:
        pip_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        subprocess.run(pip_cmd, check=True)
        print("✅ All packages installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating project directories...")
    
    directories = [
        "data",
        "models", 
        "uploads",
        "src/web_app/static",
        "src/web_app/templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

def create_env_file():
    """Create .env file template"""
    print("\n⚙️  Setting up environment configuration...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    env_template = """# Spotify API Credentials
# Get these from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-for-flask-sessions-change-this

# Development Settings
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_template)
        
        print("✅ .env file created")
        print("⚠️  IMPORTANT: Edit .env file with your Spotify API credentials!")
        print("   Get credentials from: https://developer.spotify.com/dashboard")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing module imports...")
    
    test_modules = [
        ("flask", "Flask web framework"),
        ("cv2", "OpenCV for computer vision"), 
        ("tensorflow", "TensorFlow for deep learning"),
        ("sklearn", "Scikit-learn for ML algorithms"),
        ("spotipy", "Spotify Web API client"),
        ("pandas", "Data manipulation library"),
        ("numpy", "Numerical computing library")
    ]
    
    failed_imports = []
    
    for module, description in test_modules:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError:
            print(f"❌ {module} - {description}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️  Failed to import: {', '.join(failed_imports)}")
        print("Please install missing packages:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All required modules imported successfully!")
    return True

def setup_spotify_instructions():
    """Provide Spotify API setup instructions"""
    print("\n🎵 SPOTIFY API SETUP INSTRUCTIONS:")
    print("-" * 40)
    print("1. Go to https://developer.spotify.com/dashboard")
    print("2. Log in with your Spotify account")
    print("3. Click 'Create App'")
    print("4. Fill in app details:")
    print("   - App Name: 'Emotion Music Recommender'")
    print("   - App Description: 'Music recommendations based on emotions'")
    print("   - Redirect URI: 'http://localhost:5000'")
    print("5. Copy your Client ID and Client Secret")
    print("6. Update the .env file with these credentials")
    print()

def print_next_steps():
    """Print next steps after setup"""
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("Next steps:")
    print()
    print("1. 📝 Edit .env file with your Spotify API credentials")
    print("2. 🧪 Test the setup:")
    print("   python main.py --setup")
    print()
    print("3. 🚀 Run the application:")
    print("   python main.py --web")
    print()
    print("4. 🎯 Or try interactive mode:")
    print("   python main.py --interactive")
    print()
    print("📚 For more information, see README.md")
    print()

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create virtual environment
    if not create_virtual_environment():
        print("⚠️  Continuing without virtual environment...")
    
    # Install requirements
    if not install_requirements():
        print("⚠️  Some packages may not be installed correctly")
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Test imports
    if not test_imports():
        print("⚠️  Some modules failed to import. Please check your installation.")
    
    # Setup instructions
    setup_spotify_instructions()
    
    # Next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)