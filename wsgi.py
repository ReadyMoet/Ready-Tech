"""
WSGI entry point file for Ready Tech application
This file helps Render and other WSGI servers locate and load the Flask application.
"""

from app_new import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)