@echo off
REM Build script for Windows executable
REM Requires Python 3.8+ and PyInstaller

echo ================================================
echo UFS Tracker - Windows Build Script
echo ================================================
echo.

echo Installing dependencies...
pip install pyinstaller
pip install pywebview

echo.
echo Building Console executable...
pyinstaller --clean ^
    --name=UFS-Tracker-Console ^
    --onefile ^
    --console ^
    --add-data "templates;templates" ^
    --hidden-import=flask ^
    --hidden-import=requests ^
    --hidden-import=bs4 ^
    --hidden-import=sqlite3 ^
    app.py

echo.
echo Building Desktop GUI executable...
pyinstaller --clean ^
    --name=UFS-Tracker ^
    --onefile ^
    --noconsole ^
    --add-data "templates;templates" ^
    --hidden-import=flask ^
    --hidden-import=requests ^
    --hidden-import=bs4 ^
    --hidden-import=sqlite3 ^
    --hidden-import=webview ^
    --collect-all=webview ^
    desktop_app.py

echo.
echo Creating portable package...
if not exist "dist\UFS-Tracker-Portable" mkdir "dist\UFS-Tracker-Portable"
copy "dist\UFS-Tracker.exe" "dist\UFS-Tracker-Portable\"
copy "dist\UFS-Tracker-Console.exe" "dist\UFS-Tracker-Portable\"
copy "README.md" "dist\UFS-Tracker-Portable\"
copy "USER_GUIDE.md" "dist\UFS-Tracker-Portable\"

REM Create startup batch file for Desktop app
echo @echo off > "dist\UFS-Tracker-Portable\start.bat"
echo echo Starting UFS Maritime Notices Tracker (Desktop App)... >> "dist\UFS-Tracker-Portable\start.bat"
echo UFS-Tracker.exe >> "dist\UFS-Tracker-Portable\start.bat"

REM Create startup batch file for Console/Browser mode
echo @echo off > "dist\UFS-Tracker-Portable\start-console.bat"
echo echo Starting UFS Maritime Notices Tracker (Browser mode)... >> "dist\UFS-Tracker-Portable\start-console.bat"
echo echo The application will open in your web browser. >> "dist\UFS-Tracker-Portable\start-console.bat"
echo echo. >> "dist\UFS-Tracker-Portable\start-console.bat"
echo start http://127.0.0.1:5000 >> "dist\UFS-Tracker-Portable\start-console.bat"
echo UFS-Tracker-Console.exe >> "dist\UFS-Tracker-Portable\start-console.bat"

REM Create package README
echo UFS Maritime Notices Tracker - Windows Package > "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo. >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo TWO VERSIONS INCLUDED: >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo. >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo 1. Desktop Application (RECOMMENDED): >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo    - Double-click: start.bat >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo    - Runs in a native desktop window >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo    - No browser needed >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo    - File: UFS-Tracker.exe >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo. >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo 2. Console/Browser Mode: >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo    - Double-click: start-console.bat >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo    - Opens in your default web browser >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo    - Shows console window >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"
echo    - File: UFS-Tracker-Console.exe >> "dist\UFS-Tracker-Portable\README-PACKAGE.txt"

echo.
echo ================================================
echo Build complete!
echo ================================================
echo.
echo Portable package created at: dist\UFS-Tracker-Portable
echo.
echo To run Desktop App (Recommended):
echo   1. Navigate to dist\UFS-Tracker-Portable
echo   2. Double-click start.bat
echo.
echo To run in Browser mode:
echo   1. Navigate to dist\UFS-Tracker-Portable
echo   2. Double-click start-console.bat
echo.
pause
