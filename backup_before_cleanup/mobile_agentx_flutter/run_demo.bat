@echo off
echo.
echo ========================================
echo  Mobile AgentX Flutter Demo
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Flutter installation...
flutter --version
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Flutter is not installed or not in PATH
    echo Please install Flutter SDK from: https://flutter.dev/docs/get-started/install
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
flutter pub get
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting Mobile AgentX app...
echo.
echo TIP: The app works in demo mode even without the backend running
echo Try these commands:
echo   - "Prepare for my 3 PM meeting"
echo   - "Morning routine setup"
echo   - "Triage unread messages"
echo.

flutter run