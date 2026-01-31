"""
Desktop wrapper for UFS Maritime Notices Tracker
Creates a native desktop application window instead of opening in browser
"""
import webview
import threading
import time
import sys
import os
import urllib.request
import urllib.error

# Import the Flask app
from app import app as flask_app, init_db

def start_flask():
    """Start Flask server in background thread"""
    try:
        # Initialize database
        init_db()
        
        # Run Flask without debug mode and without opening browser
        flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Error starting Flask: {e}")
        sys.exit(1)

def wait_for_flask(max_attempts=30, delay=0.5):
    """Wait for Flask server to be ready"""
    print("Waiting for Flask server to start...")
    for i in range(max_attempts):
        try:
            response = urllib.request.urlopen('http://127.0.0.1:5000', timeout=1)
            if response.status == 200:
                print("Flask server is ready!")
                return True
        except (urllib.error.URLError, ConnectionError):
            time.sleep(delay)
    
    print("Flask server failed to start within timeout period")
    return False

def main():
    """Main entry point for desktop application"""
    print("=" * 60)
    print("UFS Maritime Notices Tracker - Desktop Application")
    print("=" * 60)
    
    # Start Flask in background thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Wait for Flask to be ready
    if not wait_for_flask():
        print("ERROR: Could not start Flask server")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Create native window
    print("Opening application window...")
    window = webview.create_window(
        title='UFS Maritime Notices Tracker',
        url='http://127.0.0.1:5000',
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600),
        confirm_close=False
    )
    
    # Start the GUI event loop (this blocks until window is closed)
    webview.start(debug=False)
    
    print("Application closed")

if __name__ == '__main__':
    main()
