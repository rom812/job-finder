#!/usr/bin/env python3
"""
Simple Server - Runs everything without npm/vite
Just Python - works every time!
"""

import http.server
import socketserver
import webbrowser
import threading
import time
import os
import sys

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        if self.path == '/':
            self.path = '/simple_ui.html'
        return super().do_GET()

def start_server():
    """Start the HTTP server"""
    os.chdir('/Users/romsheynis/Documents/GitHub/job-finder')

    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("\n" + "=" * 80)
        print(f"🚀 Job Finder Server Running!")
        print("=" * 80)
        print(f"\n✅ Server: http://localhost:{PORT}")
        print(f"\n📖 Open in browser: http://localhost:{PORT}")
        print("\n💡 This is a simple HTML interface - no npm/vite needed!")
        print("\nPress Ctrl+C to stop")
        print("=" * 80 + "\n")

        # Auto-open browser after 2 seconds
        def open_browser():
            time.sleep(2)
            webbrowser.open(f'http://localhost:{PORT}')

        threading.Thread(target=open_browser, daemon=True).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down server...")
            httpd.shutdown()

if __name__ == '__main__':
    print("\n🔧 Starting Simple Job Finder Server...")
    print("   No npm, no vite, no timeouts - just Python!\n")
    start_server()
