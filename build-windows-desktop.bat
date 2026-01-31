@echo off
REM Build script for Windows Desktop GUI application
REM Creates a standalone .exe with native window (no browser needed)

echo ================================================
echo UFS Tracker - Desktop GUI Build Script
echo ================================================
echo.

echo Installing dependencies...
pip install pywebview pyinstaller

echo.
echo Building desktop application...
pyinstaller --clean ^
    --name=UFS-Tracker-Desktop ^
    --onefile ^
    --windowed ^
    --add-data "templates;templates" ^
    --hidden-import=flask ^
    --hidden-import=requests ^
    --hidden-import=bs4 ^
    --hidden-import=sqlite3 ^
    --hidden-import=webview ^
    --hidden-import=webview.platforms.winforms ^
    --collect-all=webview ^
    desktop_app.py

echo.
echo Creating portable package...
if not exist "dist\UFS-Tracker-Desktop" mkdir "dist\UFS-Tracker-Desktop"
copy "dist\UFS-Tracker-Desktop.exe" "dist\UFS-Tracker-Desktop\"
copy "README.md" "dist\UFS-Tracker-Desktop\"
copy "USER_GUIDE.md" "dist\UFS-Tracker-Desktop\"

echo.
echo ================================================
echo Build complete!
echo ================================================
echo.
echo Desktop application created at: dist\UFS-Tracker-Desktop
echo.
echo To run:
echo   1. Navigate to dist\UFS-Tracker-Desktop
echo   2. Double-click UFS-Tracker-Desktop.exe
echo.
echo The application will open in its own window.
echo No browser required!
echo.
pause
