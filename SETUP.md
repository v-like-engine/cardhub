# SoundWound Setup Guide

This guide provides detailed instructions for setting up and running the SoundWound card game platform.

## Quick Start

### 1. Prerequisites Check

Ensure you have the following installed:

**Python 3.8+**
```bash
python --version
# Should output Python 3.8.x or higher
```

**Flutter SDK 3.0+**
```bash
flutter --version
# Should output Flutter 3.x.x or higher
```

**Git**
```bash
git --version
```

### 2. Project Setup

**Clone or navigate to the project**:
```bash
cd /path/to/SoundWound
```

**Backend Setup**:
```bash
# Navigate to project root (where this file is located)
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Initialize database
python -c "from database.database import get_database_manager; get_database_manager().initialize_database()"

# Start the backend server
python api/app.py
```

The backend will start at `http://localhost:5000`

**Frontend Setup** (in a new terminal):
```bash
# Navigate to frontend directory
cd frontend

# Get Flutter dependencies
flutter pub get

# Run the application
flutter run -d chrome
```

## Detailed Setup Instructions

### Backend Configuration

#### Environment Variables (Optional)
Create a `.env` file in the backend directory:
```
FLASK_ENV=development
DATABASE_URL=sqlite:///soundwound.db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

#### Database Initialization
The database will be automatically created when you first run the initialization command. It includes:
- User management tables
- Game session tracking
- Statistics and achievements
- Default achievements data

#### Testing the Backend
```bash
# Test the health endpoint
curl http://localhost:5000/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "database": {
    "healthy": true,
    "stats": {...}
  }
}
```

### Frontend Configuration

#### Flutter Web Setup
For web development, ensure Flutter web is enabled:
```bash
flutter config --enable-web
```

#### Running on Different Platforms
```bash
# Web (Chrome)
flutter run -d chrome

# Mobile (if you have emulators/devices)
flutter run

# Desktop (if enabled)
flutter run -d windows  # or macos, linux
```

#### Hot Reload
During development, you can use hot reload:
- Press `r` in the terminal running Flutter
- Or save files in your IDE to trigger automatic reload

## Development Workflow

### Starting Development Session

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   python api/app.py
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd frontend
   flutter run -d chrome
   ```

3. **Open in Browser**: Navigate to the URL shown in Flutter terminal (usually `http://localhost:xxxxx`)

### Making Changes

**Backend Changes**:
- Python files are automatically reloaded when using Flask development server
- Database schema changes require re-initialization
- API route changes are immediately available

**Frontend Changes**:
- Dart files trigger hot reload automatically
- Widget changes appear immediately in the browser
- State changes may require hot restart (`R` in terminal)

## Project Structure Overview

```
SoundWound/
├── backend/                 # Python backend
│   ├── api/                # Flask API routes
│   ├── game_engine/        # Game logic
│   ├── ai/                 # AI algorithms
│   ├── database/           # Database models
│   └── models/             # Data structures
├── frontend/               # Flutter frontend
│   ├── lib/               # Dart source code
│   ├── assets/            # Images, fonts
│   └── web/               # Web-specific files
├── requirements.txt        # Python dependencies
└── README.md              # Main documentation
```

## Common Issues and Solutions

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'flask'`
**Solution**: Ensure virtual environment is activated and dependencies are installed
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**Issue**: Database errors on startup
**Solution**: Delete the database file and reinitialize
```bash
rm backend/soundwound.db
python -c "from database.database import get_database_manager; get_database_manager().initialize_database()"
```

**Issue**: Port 5000 already in use
**Solution**: Change the port in `backend/api/app.py`
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # Changed from 5000 to 5001
```

### Frontend Issues

**Issue**: `flutter: command not found`
**Solution**: Install Flutter SDK and add to PATH
- Download from https://flutter.dev/docs/get-started/install
- Add Flutter bin directory to system PATH

**Issue**: Web not enabled
**Solution**: Enable web support
```bash
flutter config --enable-web
flutter create . --platforms web
```

**Issue**: Dependencies not found
**Solution**: Clean and reinstall dependencies
```bash
flutter clean
flutter pub get
```

### CORS Issues

If you encounter CORS errors when the frontend tries to connect to the backend:

1. Ensure Flask-CORS is installed
2. Check that the frontend URL is in the allowed origins
3. Verify the backend is running on the correct port

## Testing the Setup

### Backend API Testing
```bash
# Health check
curl http://localhost:5000/api/health

# Create guest user
curl -X POST http://localhost:5000/api/auth/guest \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Test Player"}'

# Create game
curl -X POST http://localhost:5000/api/games/create \
  -H "Content-Type: application/json" \
  -d '{"game_type": "blackjack", "user_id": 1, "ai_difficulty": "medium"}'
```

### Frontend Functionality Testing
1. Open the application in browser
2. Navigate through menu cards (Play, Settings, Exit)
3. Select a game from the game selection screen
4. Verify that game menu loads with options
5. Check that statistics and rules screens display

## Production Deployment

### Backend Deployment
For production, consider:
- Using PostgreSQL instead of SQLite
- Setting up proper environment variables
- Using WSGI server like Gunicorn
- Configuring proper logging

### Frontend Deployment
Build for web deployment:
```bash
cd frontend
flutter build web
```

The built files will be in `frontend/build/web/` and can be served by any web server.

## Getting Help

1. **Check Logs**: Both Flask and Flutter provide detailed error logs
2. **API Documentation**: Visit `http://localhost:5000/api/info` for API details
3. **Flutter Debugging**: Use Flutter DevTools for frontend debugging
4. **Database Issues**: Check the SQLite database file is created and accessible

## Next Steps

Once you have the basic setup working:

1. **Explore the Games**: Try playing each of the four card games
2. **Test AI Difficulties**: Create games with different AI difficulty levels
3. **Check Statistics**: Play several games and view the statistics screens
4. **Customize UI**: Modify the Flutter widgets to customize appearance
5. **Extend Functionality**: Add new features using the existing architecture