#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple offline dev server for the generated static site."""
import http.server
import socketserver
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
os.chdir(ROOT)
PORT = 8000
with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    print("Serving %s at http://localhost:%d" % (ROOT, PORT))
    httpd.serve_forever()
