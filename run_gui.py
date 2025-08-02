#!/usr/bin/env python3
"""Simple script to run the GUI application."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.gui.app import create_app
    print("Successfully imported create_app")
except ImportError as e:
    print(f"Failed to import create_app: {e}")
    sys.exit(1)

if __name__ == '__main__':
    print("Starting Flask application...")
    try:
        # Create and run the app (database init happens inside create_app)
        app = create_app()
        print("App created successfully, starting server...")
        app.run(debug=True, host='127.0.0.1', port=4000)
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()