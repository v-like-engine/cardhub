@echo off
REM Flutter launcher script for Yandex Browser (Windows)
REM This script sets up Flutter to use Yandex Browser instead of Chrome

echo 🎮 CardHub Flutter Launcher (Yandex Browser)
echo ==============================================
echo.

REM Common Yandex Browser paths on Windows
set "YANDEX_BROWSER="

if exist "%LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe" (
    set "YANDEX_BROWSER=%LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe"
)
if exist "%ProgramFiles%\Yandex\YandexBrowser\Application\browser.exe" (
    set "YANDEX_BROWSER=%ProgramFiles%\Yandex\YandexBrowser\Application\browser.exe"
)
if exist "%ProgramFiles(x86)%\Yandex\YandexBrowser\Application\browser.exe" (
    set "YANDEX_BROWSER=%ProgramFiles(x86)%\Yandex\YandexBrowser\Application\browser.exe"
)

if "%YANDEX_BROWSER%"=="" (
    echo ❌ Yandex Browser not found in standard locations.
    echo.
    echo Please install Yandex Browser or specify the path manually:
    echo   set CHROME_EXECUTABLE=C:\path\to\browser.exe
    echo   run_flutter_yandex.bat
    echo.
    echo Common locations to check:
    echo   - %%LOCALAPPDATA%%\Yandex\YandexBrowser\Application\browser.exe
    echo   - %%ProgramFiles%%\Yandex\YandexBrowser\Application\browser.exe
    echo   - %%ProgramFiles(x86)%%\Yandex\YandexBrowser\Application\browser.exe
    pause
    exit /b 1
)

echo ✓ Found Yandex Browser: %YANDEX_BROWSER%

REM Check if Flutter is installed
where flutter >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Flutter is not installed or not in PATH
    echo.
    echo Please install Flutter first. See FLUTTER_SETUP.md for instructions.
    pause
    exit /b 1
)

echo ✓ Flutter is installed
echo.

REM Navigate to frontend directory
cd /d "%~dp0\frontend"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Frontend directory not found
    pause
    exit /b 1
)

echo 📦 Installing Flutter dependencies...
flutter pub get

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install Flutter dependencies
    pause
    exit /b 1
)

echo.
echo ✓ Dependencies installed
echo.
echo 🚀 Starting Flutter app with Yandex Browser...
echo    Browser: %YANDEX_BROWSER%
echo.
echo 💡 Press Ctrl+C to stop the app
echo.

REM Set Chrome executable to Yandex Browser and run Flutter
set "CHROME_EXECUTABLE=%YANDEX_BROWSER%"
flutter run -d web-server --web-port=8080 --web-browser-flag="--disable-web-security"

echo.
echo 👋 Flutter app stopped
pause
