#!/bin/bash
# Startup script for UFS Maritime Notices Tracker

echo "================================================"
echo "UFS Maritime Notices Tracker"
echo "================================================"
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt --break-system-packages

echo ""
echo "Starting application..."
echo "Open your browser at: http://127.0.0.1:5000"
echo ""
echo "Use './start.sh --debug' to enable debug output"
echo "Press Ctrl+C to stop the server"
echo "================================================"
echo ""

python app.py "$@"
