#!/usr/bin/env python3
"""
CardHub - Unified Application Launcher

This script provides a simple one-click way to launch the CardHub application.
It handles dependency installation, database initialization, and server startup.

Usage:
    python run.py                 # Run normally
    python run.py --install-deps  # Install dependencies first
    python run.py --help          # Show help
"""

import sys
import subprocess
import os
from pathlib import Path
import time
import webbrowser
import argparse

# Add project root to Python path at the very beginning
# This ensures all backend imports work correctly
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║               🎴  CARDHUB  🎴                            ║
    ║          Premium Card Game Platform                       ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python version: {sys.version.split()[0]}")


def install_dependencies():
    """Install required Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    requirements_file = Path(__file__).parent / 'requirements.txt'

    if not requirements_file.exists():
        print("❌ Error: requirements.txt not found")
        return False

    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-q',
            '-r', str(requirements_file)
        ])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n🔍 Checking dependencies...")
    required_packages = ['flask', 'flask_cors', 'sqlalchemy']

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        return False

    print("✓ All required dependencies are installed")
    return True


def initialize_database():
    """Initialize the database if needed."""
    print("\n💾 Initializing database...")
    try:
        from backend.database.database import get_database_manager
        db_manager = get_database_manager()

        if db_manager.health_check():
            print("✓ Database initialized and healthy")
            return True
        else:
            print("❌ Database health check failed")
            return False
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        print(f"   Details: {traceback.format_exc()}")
        return False


def start_server(auto_open_browser=True):
    """Start the Flask server."""
    print("\n🚀 Starting CardHub server...\n")
    print("=" * 60)
    print("  Server URL: http://localhost:5000")
    print("  Open this URL in your browser to play!")
    print("=" * 60)
    print("\n💡 Press CTRL+C to stop the server\n")

    # Import and run the Flask app
    from backend.api.app import app

    # Open browser after a short delay (if enabled)
    if auto_open_browser:
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open('http://localhost:5000')
            except Exception as e:
                print(f"Could not open browser automatically: {e}")
                print("Please open http://localhost:5000 manually")

        import threading
        threading.Thread(target=open_browser, daemon=True).start()

    # Run the server
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error running server: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='CardHub - Premium Card Game Platform Launcher'
    )
    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='Install dependencies before starting'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not open browser automatically'
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Check Python version
    check_python_version()

    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)

    # Check dependencies
    if not check_dependencies():
        print("\n💡 Run with --install-deps to install missing dependencies:")
        print("   python run.py --install-deps")
        sys.exit(1)

    # Initialize database
    if not initialize_database():
        print("\n❌ Failed to initialize database")
        sys.exit(1)

    # Start server
    start_server(auto_open_browser=not args.no_browser)


if __name__ == '__main__':
    main()
