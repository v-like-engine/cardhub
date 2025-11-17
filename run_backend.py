"""
Run script for SoundWound backend API server.

This script properly initializes the Python path and starts the Flask server.
Run from the project root directory.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now we can import with absolute imports
from backend.api.app import app

if __name__ == '__main__':
    print("Starting SoundWound Backend API Server...")
    print("Server will be available at: http://localhost:5000")
    print("API Info: http://localhost:5000/api/info")
    print("Health Check: http://localhost:5000/api/health")
    print("\nPress CTRL+C to stop the server\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
