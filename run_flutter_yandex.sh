#!/bin/bash
# Flutter launcher script for Yandex Browser
# This script sets up Flutter to use Yandex Browser instead of Chrome

echo "🎮 CardHub Flutter Launcher (Yandex Browser)"
echo "=============================================="
echo ""

# Common Yandex Browser paths
YANDEX_PATHS=(
    "/usr/bin/yandex-browser"
    "/usr/bin/yandex-browser-stable"
    "$HOME/.local/share/yandex/browser/yandex-browser"
    "/opt/yandex/browser/yandex-browser"
)

# Find Yandex Browser
YANDEX_BROWSER=""
for path in "${YANDEX_PATHS[@]}"; do
    if [ -f "$path" ]; then
        YANDEX_BROWSER="$path"
        echo "✓ Found Yandex Browser: $YANDEX_BROWSER"
        break
    fi
done

if [ -z "$YANDEX_BROWSER" ]; then
    echo "❌ Yandex Browser not found in standard locations."
    echo ""
    echo "Please install Yandex Browser or specify the path manually:"
    echo "  export CHROME_EXECUTABLE=/path/to/yandex-browser"
    echo "  ./run_flutter_yandex.sh"
    echo ""
    echo "Common locations to check:"
    for path in "${YANDEX_PATHS[@]}"; do
        echo "  - $path"
    done
    exit 1
fi

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed or not in PATH"
    echo ""
    echo "Please install Flutter first. See FLUTTER_SETUP.md for instructions."
    exit 1
fi

echo "✓ Flutter is installed"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || exit 1

echo "📦 Installing Flutter dependencies..."
flutter pub get

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Flutter dependencies"
    exit 1
fi

echo ""
echo "✓ Dependencies installed"
echo ""
echo "🚀 Starting Flutter app with Yandex Browser..."
echo "   Browser: $YANDEX_BROWSER"
echo ""
echo "💡 Press Ctrl+C to stop the app"
echo ""

# Set Chrome executable to Yandex Browser and run Flutter
export CHROME_EXECUTABLE="$YANDEX_BROWSER"
flutter run -d web-server --web-port=8080 --web-browser-flag="--disable-web-security"

echo ""
echo "👋 Flutter app stopped"
