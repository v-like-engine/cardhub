@echo off
REM Flutter launcher script for Yandex Browser (Windows)
REM This script sets up Flutter to use Yandex Browser instead of Chrome

echo.
echo =========================================================
echo   CardHub Flutter Launcher (Yandex Browser)
echo =========================================================
echo.

REM Check if script is in the correct directory
if not exist "%~dp0frontend" (
    echo ERROR: frontend directory not found!
    echo This script must be run from the CardHub root directory.
    echo Current directory: %CD%
    echo Script location: %~dp0
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking for Yandex Browser...
echo.

REM Common Yandex Browser paths on Windows
set "YANDEX_BROWSER="

echo Checking: %%LOCALAPPDATA%%\Yandex\YandexBrowser\Application\browser.exe
if exist "%LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe" (
    set "YANDEX_BROWSER=%LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe"
    echo   Found: YES
    goto :browser_found
)
echo   Found: NO

echo Checking: %%ProgramFiles%%\Yandex\YandexBrowser\Application\browser.exe
if exist "%ProgramFiles%\Yandex\YandexBrowser\Application\browser.exe" (
    set "YANDEX_BROWSER=%ProgramFiles%\Yandex\YandexBrowser\Application\browser.exe"
    echo   Found: YES
    goto :browser_found
)
echo   Found: NO

echo Checking: %%ProgramFiles(x86)%%\Yandex\YandexBrowser\Application\browser.exe
if exist "%ProgramFiles(x86)%\Yandex\YandexBrowser\Application\browser.exe" (
    set "YANDEX_BROWSER=%ProgramFiles(x86)%\Yandex\YandexBrowser\Application\browser.exe"
    echo   Found: YES
    goto :browser_found
)
echo   Found: NO

REM Check if user provided CHROME_EXECUTABLE
if defined CHROME_EXECUTABLE (
    echo Checking custom CHROME_EXECUTABLE...
    if exist "%CHROME_EXECUTABLE%" (
        set "YANDEX_BROWSER=%CHROME_EXECUTABLE%"
        echo   Found: YES
        goto :browser_found
    )
)

echo.
echo =========================================================
echo ERROR: Yandex Browser not found!
echo =========================================================
echo.
echo Please install Yandex Browser from: https://browser.yandex.com/
echo.
echo Or set the browser path manually:
echo   set CHROME_EXECUTABLE=C:\path\to\browser.exe
echo   run_flutter_yandex.bat
echo.
echo Locations checked:
echo   - %LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe
echo   - %ProgramFiles%\Yandex\YandexBrowser\Application\browser.exe
echo   - %ProgramFiles(x86)%\Yandex\YandexBrowser\Application\browser.exe
echo.
pause
exit /b 1

:browser_found
echo.
echo SUCCESS: Yandex Browser found!
echo Location: %YANDEX_BROWSER%
echo.

echo [2/5] Checking for Flutter...
echo.

where flutter >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo =========================================================
    echo ERROR: Flutter is not installed or not in PATH
    echo =========================================================
    echo.
    echo Please install Flutter first:
    echo   1. Download from: https://docs.flutter.dev/get-started/install/windows
    echo   2. Extract to C:\src\flutter
    echo   3. Add C:\src\flutter\bin to your PATH
    echo   4. Open new Command Prompt and try again
    echo.
    echo For detailed instructions, see FLUTTER_SETUP.md
    echo.
    pause
    exit /b 1
)

flutter --version
echo.
echo SUCCESS: Flutter is installed
echo.

echo [3/5] Checking backend status...
echo.
echo Checking if backend is running at http://localhost:5000...
curl -s http://localhost:5000/api/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Backend doesn't appear to be running!
    echo.
    echo Please start the backend first in another window:
    echo   python run.py
    echo.
    echo Then press any key to continue, or Ctrl+C to exit...
    pause
)

echo SUCCESS: Backend is running
echo.

echo [4/5] Installing Flutter dependencies...
echo.

cd /d "%~dp0frontend"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Cannot navigate to frontend directory
    echo Path: %~dp0frontend
    pause
    exit /b 1
)

flutter pub get
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo =========================================================
    echo ERROR: Failed to install Flutter dependencies
    echo =========================================================
    echo.
    echo Try these steps:
    echo   1. cd frontend
    echo   2. flutter clean
    echo   3. flutter pub get
    echo.
    pause
    exit /b 1
)

echo.
echo SUCCESS: Dependencies installed
echo.

echo [5/5] Starting Flutter app...
echo.
echo =========================================================
echo   Flutter app starting with Yandex Browser
echo =========================================================
echo.
echo Browser: %YANDEX_BROWSER%
echo Port: http://localhost:8080
echo.
echo The app will open in Yandex Browser automatically.
echo To stop the app, press Ctrl+C in this window.
echo.
echo =========================================================
echo.

REM Set Chrome executable to Yandex Browser and run Flutter
set "CHROME_EXECUTABLE=%YANDEX_BROWSER%"
flutter run -d web-server --web-port=8080 --web-browser-flag="--disable-web-security"

echo.
echo.
echo =========================================================
echo   Flutter app stopped
echo =========================================================
echo.
pause
