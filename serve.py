#!/usr/bin/env python3
"""
Academic Absence & A-Mark Analyzer local server launcher.
This script overcomes browser security restrictions for local files (file:// protocol)
and iframe rendering issues inside IDE editor frames.
"""

import http.server
import socketserver
import webbrowser
import socket
import sys
import os

# Set current directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8000
while PORT < 8080:
    try:
        # Check if port is in use
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', PORT))
            break
    except socket.error:
        PORT += 1

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silence terminal request logs

print("=" * 60)
print(f"Starting local server at: http://localhost:{PORT}")
print("This overcomes 'file://' unique origin security restrictions,")
print("enabling full frame rendering and offline capabilities.")
print("Press Ctrl+C to stop the server.")
print("=" * 60)

# Automatically open default browser tab
webbrowser.open(f"http://localhost:{PORT}/amark_analysis.html")

try:
    with socketserver.TCPServer(('127.0.0.1', PORT), QuietHandler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
    sys.exit(0)
