

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os
# Minimal server to satisfy Koyeb health check
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

def run_server():
    port = int(os.getenv("PORT", 8000))
    HTTPServer(('', port), Handler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

from http.server import BaseHTTPRequestHandler, HTTPServer

# --- Tiny Web Server so Koyeb Free Plan doesn't sleep ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web():
    port = int(os.getenv("PORT", 8000))
    server = HTTPServer(("", port), Handler)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

import threading, time, requests
def keep_alive():
    url = "https://" + os.getenv("KOYEB_APP_NAME") + ".koyeb.app"
    while True:
        try:
            requests.get(url)
        except:
            pass
        time.sleep(240)
threading.Thread(target=keep_alive, daemon=True).start()

import subprocess
import sys
import time

subprocess.Popen([sys.executable, "bot.py"])
subprocess.Popen([sys.executable, "bot2.py"])
subprocess.Popen([sys.executable, "bot3.py"])

# keep the app alive so Koyeb doesn't stop it
while True:
    time.sleep(60)
