#!/usr/bin/env python3
"""Simple script to run the GUI application."""

from src.gui.app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=4000)
