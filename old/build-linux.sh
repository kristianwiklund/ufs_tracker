#!/bin/bash
# Build script for Linux/Mac executable
# Requires Python 3.8+ and PyInstaller

echo "================================================"
echo "UFS Tracker - Build Script"
echo "================================================"
echo ""

echo "Installing PyInstaller..."
pip install pyinstaller

echo ""
echo "Building executable..."
pyinstaller --clean \
    --name=UFS-Tracker \
    --onefile \
    --add-data "templates:templates" \
    --hidden-import=flask \
    --hidden-import=requests \
    --hidden-import=bs4 \
    --hidden-import=sqlite3 \
    --hidden-import=argparse \
    app.py

echo ""
echo "Creating portable package..."
mkdir -p "dist/UFS-Tracker-Portable"
cp "dist/UFS-Tracker" "dist/UFS-Tracker-Portable/"
cp "README.md" "dist/UFS-Tracker-Portable/"
cp "USER_GUIDE.md" "dist/UFS-Tracker-Portable/"

# Create startup script
cat > "dist/UFS-Tracker-Portable/start.sh" << 'EOF'
#!/bin/bash
echo "Starting UFS Maritime Notices Tracker..."
echo "The application will open in your web browser."
echo ""

# Open browser after a short delay
sleep 2 && open http://127.0.0.1:5000 &

# Start the application
./UFS-Tracker
EOF

chmod +x "dist/UFS-Tracker-Portable/start.sh"
chmod +x "dist/UFS-Tracker-Portable/UFS-Tracker"

echo ""
echo "================================================"
echo "Build complete!"
echo "================================================"
echo ""
echo "Portable package created at: dist/UFS-Tracker-Portable"
echo ""
echo "To run:"
echo "  1. Navigate to dist/UFS-Tracker-Portable"
echo "  2. Run: ./start.sh"
echo ""
echo "The application will start and open in your web browser."
echo ""
