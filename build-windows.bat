@echo off
REM Build script for Windows executable
REM Requires Python 3.8+ and PyInstaller

echo ================================================
echo UFS Tracker - Windows Build Script
echo ================================================
echo.

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building executable...
pyinstaller --clean ^
    --name=UFS-Tracker ^
    --onefile ^
    --add-data "templates;templates" ^
    --hidden-import=flask ^
    --hidden-import=requests ^
    --hidden-import=bs4 ^
    --hidden-import=sqlite3 ^
    --hidden-import=argparse ^
    app.py

echo.
echo Creating portable package...
if not exist "dist\UFS-Tracker-Portable" mkdir "dist\UFS-Tracker-Portable"
copy "dist\UFS-Tracker.exe" "dist\UFS-Tracker-Portable\"
copy "README.md" "dist\UFS-Tracker-Portable\"
copy "USER_GUIDE.md" "dist\UFS-Tracker-Portable\"

REM Create startup batch file
echo @echo off > "dist\UFS-Tracker-Portable\start.bat"
echo echo Starting UFS Maritime Notices Tracker... >> "dist\UFS-Tracker-Portable\start.bat"
echo echo The application will open in your web browser. >> "dist\UFS-Tracker-Portable\start.bat"
echo echo. >> "dist\UFS-Tracker-Portable\start.bat"
echo start http://127.0.0.1:5000 >> "dist\UFS-Tracker-Portable\start.bat"
echo UFS-Tracker.exe >> "dist\UFS-Tracker-Portable\start.bat"

echo.
echo ================================================
echo Build complete!
echo ================================================
echo.
echo Portable package created at: dist\UFS-Tracker-Portable
echo.
echo To run:
echo   1. Navigate to dist\UFS-Tracker-Portable
echo   2. Double-click start.bat
echo.
echo The application will start and open in your web browser.
echo.
pause
