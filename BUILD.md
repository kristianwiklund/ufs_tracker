# Build Instructions for UFS Maritime Notices Tracker

This document describes how to build standalone executables for Windows, Linux, Mac, and Android.

## Table of Contents
- [Windows Build](#windows-build)
- [Linux/Mac Build](#linuxmac-build)
- [Android Build](#android-build)
- [GitHub Actions Automated Builds](#github-actions-automated-builds)

---

## Windows Build

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Option 1: Automated Build Script (Recommended)

1. Open Command Prompt or PowerShell in the project directory
2. Run the build script:
   ```batch
   build-windows.bat
   ```

3. The script will:
   - Install PyInstaller
   - Build the executable
   - Create a portable package in `dist/UFS-Tracker-Portable/`

4. To run the application:
   - Navigate to `dist/UFS-Tracker-Portable/`
   - Double-click `start.bat`
   - The application will open in your web browser

### Option 2: Manual Build

1. Install PyInstaller:
   ```batch
   pip install pyinstaller
   ```

2. Build the executable:
   ```batch
   pyinstaller --clean --name=UFS-Tracker --onefile ^
       --add-data "templates;templates" ^
       --hidden-import=flask ^
       --hidden-import=requests ^
       --hidden-import=bs4 ^
       app.py
   ```

3. The executable will be in `dist/UFS-Tracker.exe`

### Distribution

The portable package (`dist/UFS-Tracker-Portable/`) contains:
- `UFS-Tracker.exe` - The main application
- `start.bat` - Convenient startup script
- `README.md` - Documentation
- `USER_GUIDE.md` - User guide

This folder can be zipped and distributed. Users just need to:
1. Extract the ZIP file
2. Double-click `start.bat`

**No Python installation required on the target machine!**

---

## Linux/Mac Build

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Option 1: Automated Build Script (Recommended)

1. Open Terminal in the project directory
2. Make the script executable (first time only):
   ```bash
   chmod +x build-linux.sh
   ```

3. Run the build script:
   ```bash
   ./build-linux.sh
   ```

4. The script will:
   - Install PyInstaller
   - Build the executable
   - Create a portable package in `dist/UFS-Tracker-Portable/`

5. To run the application:
   - Navigate to `dist/UFS-Tracker-Portable/`
   - Run: `./start.sh`
   - The application will open in your web browser

### Option 2: Manual Build

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller --clean --name=UFS-Tracker --onefile \
       --add-data "templates:templates" \
       --hidden-import=flask \
       --hidden-import=requests \
       --hidden-import=bs4 \
       app.py
   ```

3. The executable will be in `dist/UFS-Tracker`

---

## Android Build

### Important Note
Building for Android is more complex and requires significant system resources. There are two approaches:

### Approach 1: Termux (Simplest - Run Python Directly)

This doesn't create an APK but allows running the Python app natively on Android:

1. Install [Termux](https://f-droid.org/en/packages/com.termux/) from F-Droid
2. In Termux, run:
   ```bash
   pkg install python git
   git clone [your-repo-url]
   cd ufs-tracker
   pip install -r requirements.txt
   python app.py
   ```
3. Open browser to `http://127.0.0.1:5000`

### Approach 2: Build APK with Buildozer (Advanced)

**Prerequisites:**
- Linux computer (Ubuntu 20.04+ recommended)
- 8GB+ RAM
- 20GB+ free disk space

**Steps:**

1. Install system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install -y build-essential git ffmpeg libsdl2-dev \
       libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
       libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
       zlib1g-dev openjdk-17-jdk unzip
   ```

2. Install Python dependencies:
   ```bash
   pip install buildozer cython
   ```

3. Initialize buildozer (first time only):
   ```bash
   buildozer init
   ```

4. Edit `buildozer.spec` to configure your app:
   ```ini
   [app]
   title = UFS Tracker
   package.name = ufstracker
   package.domain = se.sjofartsverket
   requirements = python3,kivy,flask,requests,beautifulsoup4
   android.permissions = INTERNET
   ```

5. Build the APK:
   ```bash
   buildozer android debug
   ```

6. The APK will be in `bin/` directory

**Note:** First build can take 30-60 minutes as it downloads Android SDK/NDK.

### Approach 3: Progressive Web App (PWA) - Recommended Alternative

Instead of a native Android app, you can make the web interface installable as a PWA:

1. Users open the web app in Chrome/Firefox on Android
2. Select "Add to Home Screen" or "Install App"
3. The app behaves like a native app

This requires running the Flask app on a server accessible from the Android device.

---

## GitHub Actions Automated Builds

The project includes GitHub Actions workflows that automatically build releases when you push tags.

### Setup

1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin [your-repo-url]
   git push -u origin main
   ```

2. The workflows are already configured in `.github/workflows/`

### Creating a Release

1. Create and push a version tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. GitHub Actions will automatically:
   - Build Windows executable
   - Build Android APK (if configured)
   - Create a GitHub Release
   - Attach the builds to the release

3. Users can download the executables from the Releases page

### Available Workflows

- **build-windows.yml** - Builds Windows executable on every push
- **build-android.yml** - Builds Android APK (requires Kivy setup)

### Downloading Artifacts

Even without creating a release, you can download build artifacts:

1. Go to your GitHub repository
2. Click "Actions" tab
3. Click on a workflow run
4. Download artifacts from the "Artifacts" section

---

## Troubleshooting

### Windows Build Issues

**Problem:** "pyinstaller: command not found"
**Solution:** Install PyInstaller: `pip install pyinstaller`

**Problem:** Executable won't start
**Solution:** Check if antivirus is blocking it. Try building with `--debug` flag.

**Problem:** Templates not found
**Solution:** Ensure `--add-data "templates;templates"` is in the build command

### Linux/Mac Build Issues

**Problem:** Permission denied when running executable
**Solution:** Run `chmod +x dist/UFS-Tracker`

**Problem:** "No module named 'flask'"
**Solution:** PyInstaller didn't bundle Flask. Add `--hidden-import=flask`

### Android Build Issues

**Problem:** Build fails with "SDK not found"
**Solution:** Buildozer will download SDK automatically on first run. Be patient.

**Problem:** Out of memory during build
**Solution:** Android builds require 8GB+ RAM. Close other applications or use a cloud VM.

**Problem:** APK won't install on device
**Solution:** Enable "Install from Unknown Sources" in Android settings.

---

## File Sizes

Expected sizes for built applications:

- **Windows Executable:** ~15-25 MB
- **Linux/Mac Executable:** ~15-25 MB
- **Android APK:** ~30-50 MB (includes Python runtime)

---

## Distribution Checklist

Before distributing your builds:

- [ ] Test the executable on a clean machine without Python installed
- [ ] Include README.md and USER_GUIDE.md
- [ ] Create a proper .gitignore to exclude build artifacts
- [ ] Add version number to your builds
- [ ] Sign the executables (Windows) or APK (Android) for production
- [ ] Test on different OS versions (Windows 10/11, Android 8+)

---

## Advanced: Code Signing

### Windows Code Signing

For production releases, sign your Windows executable:

```batch
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/UFS-Tracker.exe
```

### Android Code Signing

For production APK, create a keystore and sign:

```bash
keytool -genkey -v -keystore my-release-key.keystore -alias alias_name -keyalg RSA -keysize 2048 -validity 10000
buildozer android release
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore bin/ufstracker-*.apk alias_name
```

---

## Support

For build issues, check:
1. Python version: `python --version` (need 3.8+)
2. PyInstaller version: `pyinstaller --version`
3. Build logs in GitHub Actions (if using automated builds)

---

**Last Updated:** 2026-01-28
