@echo off
REM Debug script to check Yandex Browser and Flutter setup
REM Run this to diagnose any issues

echo.
echo =========================================================
echo   CardHub Setup Diagnostic Tool
echo =========================================================
echo.

echo [TEST 1] Checking script location...
echo Current directory: %CD%
echo Script directory: %~dp0
if exist "%~dp0frontend" (
    echo Frontend directory: FOUND
) else (
    echo Frontend directory: NOT FOUND
    echo ERROR: This script must be in the CardHub root directory!
)
echo.

echo [TEST 2] Checking Yandex Browser...
echo.
set "FOUND=NO"

echo Checking: %LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe
if exist "%LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe" (
    echo Status: FOUND
    echo Path: %LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe
    set "FOUND=YES"
) else (
    echo Status: NOT FOUND
)
echo.

echo Checking: %ProgramFiles%\Yandex\YandexBrowser\Application\browser.exe
if exist "%ProgramFiles%\Yandex\YandexBrowser\Application\browser.exe" (
    echo Status: FOUND
    echo Path: %ProgramFiles%\Yandex\YandexBrowser\Application\browser.exe
    set "FOUND=YES"
) else (
    echo Status: NOT FOUND
)
echo.

echo Checking: %ProgramFiles(x86)%\Yandex\YandexBrowser\Application\browser.exe
if exist "%ProgramFiles(x86)%\Yandex\YandexBrowser\Application\browser.exe" (
    echo Status: FOUND
    echo Path: %ProgramFiles(x86)%\Yandex\YandexBrowser\Application\browser.exe
    set "FOUND=YES"
) else (
    echo Status: NOT FOUND
)
echo.

if "%FOUND%"=="YES" (
    echo RESULT: Yandex Browser is installed
) else (
    echo RESULT: Yandex Browser NOT found!
    echo.
    echo Please install from: https://browser.yandex.com/
    echo.
    echo If already installed, please find browser.exe and note its location.
)
echo.

echo [TEST 3] Checking Flutter...
where flutter >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Status: FOUND
    echo.
    flutter --version
) else (
    echo Status: NOT FOUND
    echo.
    echo Flutter is not in your PATH.
    echo.
    echo Please install Flutter from:
    echo   https://docs.flutter.dev/get-started/install/windows
    echo.
    echo After installation, add C:\src\flutter\bin to your PATH
)
echo.

echo [TEST 4] Checking Python...
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Status: FOUND
    echo.
    python --version
) else (
    echo Status: NOT FOUND
)
echo.

echo [TEST 5] Checking backend status...
curl -s http://localhost:5000/api/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Status: Backend is RUNNING
    echo URL: http://localhost:5000
) else (
    echo Status: Backend is NOT running
    echo.
    echo Start it with: python run.py
)
echo.

echo =========================================================
echo   Diagnostic Complete
echo =========================================================
echo.
echo Summary:
echo   - Script location: %~dp0
if exist "%~dp0frontend" (
    echo   - Frontend: OK
) else (
    echo   - Frontend: MISSING
)
if "%FOUND%"=="YES" (
    echo   - Yandex Browser: OK
) else (
    echo   - Yandex Browser: NOT FOUND
)
where flutter >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   - Flutter: OK
) else (
    echo   - Flutter: NOT FOUND
)
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   - Python: OK
) else (
    echo   - Python: NOT FOUND
)
echo.

pause
