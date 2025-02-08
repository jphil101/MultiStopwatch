# api/index.py

from server import app  # assuming your Flask app is defined as "app" in server.py

def handler(environ, start_response):
    """WSGI-compatible handler for Vercel."""
    return app(environ, start_response)
