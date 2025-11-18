# 🎮 CardHub with Yandex Browser - Quick Setup

No Chrome needed! Use Yandex Browser for the full Flutter experience.

## ✅ What You Need

1. **Yandex Browser** - Download from https://browser.yandex.com/ if not installed
2. **Flutter SDK** - One-time installation (~20 minutes)
3. **Python** - Already have it for the backend

---

## 🚀 Super Quick Start

### Step 1: Install Yandex Browser (if not installed)

**Windows:**
- Download: https://browser.yandex.com/
- Install normally
- Default location: `%LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe`

**Linux:**
```bash
# Ubuntu/Debian
wget https://browser.yandex.ru/download/?os=linux
sudo dpkg -i yandex-browser-stable_*.deb
sudo apt-get install -f

# Or add repository
wget -q -O - https://repo.yandex.ru/yandex-browser/YANDEX-BROWSER-KEY.GPG | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] http://repo.yandex.ru/yandex-browser/deb stable main"
sudo apt-get update
sudo apt-get install yandex-browser-stable
```

### Step 2: Install Flutter SDK

**Windows:**
1. Download: https://docs.flutter.dev/get-started/install/windows
2. Extract to `C:\src\flutter`
3. Add `C:\src\flutter\bin` to PATH
4. Open CMD and run: `flutter doctor`

**Linux:**
```bash
cd ~
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.16.0-stable.tar.xz
tar xf flutter_linux_3.16.0-stable.tar.xz

# Add to PATH
echo 'export PATH="$HOME/flutter/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

flutter doctor
```

### Step 3: Run CardHub with Yandex Browser

**Easy Method (Recommended):**
```bash
# Terminal 1: Start backend
python run.py

# Terminal 2: Start Flutter with Yandex
./run_flutter_yandex.sh      # Linux/Mac
run_flutter_yandex.bat        # Windows (just double-click!)
```

**Manual Method:**
```bash
# Terminal 1: Start backend
python run.py

# Terminal 2: Run Flutter
export CHROME_EXECUTABLE=/usr/bin/yandex-browser    # Linux
# or
set CHROME_EXECUTABLE=%LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe  # Windows

cd frontend
flutter pub get
flutter run -d web-server --web-port=8080
```

---

## 📁 What the Scripts Do

The `run_flutter_yandex` scripts:
1. ✅ Auto-detect Yandex Browser location
2. ✅ Install Flutter dependencies
3. ✅ Configure Flutter to use Yandex Browser
4. ✅ Start the Flutter app
5. ✅ Open Yandex Browser automatically

---

## 🔧 Troubleshooting

### "Yandex Browser not found"

**Windows - Check these locations:**
```
%LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe
%ProgramFiles%\Yandex\YandexBrowser\Application\browser.exe
%ProgramFiles(x86)%\Yandex\YandexBrowser\Application\browser.exe
```

**Linux - Check these locations:**
```
/usr/bin/yandex-browser
/usr/bin/yandex-browser-stable
~/.local/share/yandex/browser/yandex-browser
/opt/yandex/browser/yandex-browser
```

**Manual Override:**
```bash
# Linux/Mac
export CHROME_EXECUTABLE=/path/to/yandex-browser
./run_flutter_yandex.sh

# Windows
set CHROME_EXECUTABLE=C:\path\to\browser.exe
run_flutter_yandex.bat
```

### "Flutter not found"

Make sure Flutter is in your PATH:
```bash
# Check if Flutter is installed
flutter --version

# If not found, add to PATH
# Linux/Mac: Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/flutter/bin:$PATH"

# Windows: Add C:\src\flutter\bin to System Environment Variables
```

### "Backend connection failed"

Make sure the backend is running first:
```bash
# In terminal 1
python run.py
# Wait for "Running on http://127.0.0.1:5000"

# Then in terminal 2
./run_flutter_yandex.sh
```

### "Dependencies failed to install"

```bash
cd frontend
flutter clean
flutter pub get
```

---

## 🎯 Common Yandex Browser Locations

### Windows
```
C:\Users\[YourName]\AppData\Local\Yandex\YandexBrowser\Application\browser.exe
C:\Program Files\Yandex\YandexBrowser\Application\browser.exe
C:\Program Files (x86)\Yandex\YandexBrowser\Application\browser.exe
```

### Linux
```
/usr/bin/yandex-browser
/usr/bin/yandex-browser-stable
/opt/yandex/browser/yandex-browser
~/.local/share/yandex/browser/yandex-browser
```

---

## ✨ What You Get

With the Flutter frontend in Yandex Browser:
- 🎨 Beautiful card animations
- 🔊 Sound effects and music
- 🖱️ Drag & drop cards
- 📊 Advanced statistics with charts
- 🏆 Achievement system
- 🎯 Better game UI than the basic web interface

---

## 📝 Summary

1. Install Yandex Browser (if not already installed)
2. Install Flutter SDK (one-time setup)
3. Run the Yandex launcher script
4. Enjoy the full game experience!

**No Chrome required!** ✅

---

## 🆘 Need Help?

- **Flutter Setup**: See `FLUTTER_SETUP.md`
- **General Help**: See `QUICKSTART.md`
- **Backend Issues**: See `README.md`

**Quick test to verify everything works:**
```bash
# Check Yandex Browser
yandex-browser --version          # Linux
"%LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe" --version  # Windows

# Check Flutter
flutter --version

# Check Python backend
python run.py --help
```

If all three work, you're ready to go! 🎉
