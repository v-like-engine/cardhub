# CardHub - Quick Start Guide

Welcome to CardHub! This guide will help you get started in just a few steps.

## 🚀 One-Click Launch

CardHub now has a unified launcher that handles everything for you!

### Windows Users
1. Double-click `run.bat`
2. The application will automatically open in your browser
3. Start playing!

### Linux/Mac Users
1. Double-click `run.sh` OR run in terminal: `./run.sh`
2. The application will automatically open in your browser
3. Start playing!

### Alternative: Direct Python Launch
```bash
python run.py
```

## 📋 First Time Setup

If this is your first time running CardHub, install dependencies:

### Windows
```cmd
python run.py --install-deps
```

### Linux/Mac
```bash
python3 run.py --install-deps
```

## 🎮 How to Play

Once the server starts:

1. Your web browser will automatically open to `http://localhost:5000`
2. If it doesn't open automatically, manually navigate to that URL
3. You'll see the CardHub web interface with 4 games:
   - **Fool (Durak)** - Classic Russian card game
   - **101** - Point accumulation game
   - **BlackJack** - Casino card game
   - **Uno** - Colorful strategy game
4. Click any "Play" button to start a game against AI

## 🔧 Troubleshooting

### Dependencies Not Installed
```bash
python run.py --install-deps
```

### Port 5000 Already in Use
Edit `run.py` and change the port number in the `app.run()` call

### Can't Access the Web Interface
1. Make sure the server is running (you should see "Running on http://127.0.0.1:5000")
2. Try accessing http://127.0.0.1:5000 instead of localhost:5000
3. Check if your firewall is blocking port 5000

### Python Not Found
Make sure Python 3.8+ is installed:
- Windows: Download from https://www.python.org/downloads/
- Linux: `sudo apt install python3`
- Mac: `brew install python3`

## 📱 Advanced: Flutter Frontend

This quick launcher uses a web-based interface. For the full Flutter experience:

1. Install Flutter SDK from https://flutter.dev/docs/get-started/install
2. Navigate to `frontend/` directory
3. Run `flutter pub get`
4. Run `flutter run -d chrome` (for web) or `flutter run` (for mobile)

## 🛑 Stopping the Server

Press `CTRL+C` in the terminal window where the server is running

## 📊 Features

- **4 Different Card Games** with AI opponents
- **Multiple AI Difficulty Levels** (Easy, Medium, Hard)
- **User Statistics** tracking wins, losses, and achievements
- **Guest Mode** - Start playing immediately without registration
- **RESTful API** for developers

## 🐛 Found a Bug?

Please report issues at: https://github.com/v-like-engine/cardhub/issues

## 💡 Tips

- The web interface is perfect for quick games
- All games support guest users - no registration required
- Your statistics are saved in the local database
- The server runs locally - no internet required

---

**Enjoy playing CardHub!** 🎴
