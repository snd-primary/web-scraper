#!/usr/bin/env python
"""
A simplified MCP server implementation for Claude Desktop that doesn't require external dependencies.
This is a minimal implementation to work around the "No module named 'uvicorn'" error.
"""

import json
import sys
import os
import socket
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import time

# Simple HTML text extraction function
def extract_text_from_html(html):
    """Extract readable text from HTML without external dependencies"""
    # Remove script and style elements
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    
    # Extract title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
    title = title_match.group(1).strip() if title_match else "No title found"
    
    # Extract main content (attempt to find article tag for MDN)
    main_content_match = re.search(r'<article class="main-page-content"[^>]*>(.*?)</article>', html, re.DOTALL)
    if main_content_match:
        main_content = main_content_match.group(1)
    else:
        # Fall back to body content
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        main_content = body_match.group(1) if body_match else html
    
    # Convert HTML to text (very basic)
    text = re.sub(r'<[^>]*>', ' ', main_content)  # Remove HTML tags
    text = re.sub(r'\s+', ' ', text).strip()      # Normalize whitespace
    
    return {
        "title": title,
        "content": text[:10000]  # Limit content length
    }

# Simple HTTP server for MCP
class MCPHandler(BaseHTTPRequestHandler):
    def _send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/health':
            self._send_json_response({"status": "healthy"})
        elif self.path == '/mcp/manifest' or self.path == '/mcp-manifest.json':
            # MCP manifest
            manifest = {
                "name": "mdn-web-scraper",
                "version": "1.0.0",
                "description": "MDNウェブドキュメントをスクレイピングして提供するMCPサーバー",
                "protocols": {"mcp": "1.0.0"},
                "parameters": {
                    "url": {
                        "type": "string",
                        "description": "取得するMDN URLを指定してください",
                        "required": True
                    }
                }
            }
            self._send_json_response(manifest)
        else:
            self._send_json_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        if self.path == '/mcp':
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            request = json.loads(post_data)
            
            # Log the request
            print(f"Received MCP request: {request}", file=sys.stderr)
            
            # Extract URL from MCP parameters
            url = request.get('parameters', {}).get('url')
            if not url or not url.startswith("https://developer.mozilla.org/"):
                self._send_json_response({
                    "error": "Invalid or missing URL parameter. Only MDN URLs are supported."
                }, 400)
                return
            
            try:
                # Very simple MDN scraper
                headers = {'User-Agent': 'Mozilla/5.0'}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    html = response.read().decode('utf-8')
                    
                    # Extract text content
                    result = extract_text_from_html(html)
                    
                    # Create MCP response following protocol specs
                    mcp_response = {
                        "contexts": [
                            {
                                "id": f"mdn-{int(time.time())}",
                                "content": {
                                    "type": "mdn_document",
                                    "url": url,
                                    "title": result["title"],
                                    "content": result["content"],
                                    "source": "Mozilla Developer Network (MDN)"
                                },
                                "metadata": {
                                    "source": "mdn-web-scraper",
                                    "timestamp": time.time()
                                }
                            }
                        ],
                        "metadata": {
                            "request_id": f"req-{int(time.time())}",
                            "server": "mdn-web-scraper-mcp"
                        }
                    }
                    
                    self._send_json_response(mcp_response)
            
            except Exception as e:
                print(f"Error processing request: {str(e)}", file=sys.stderr)
                self._send_json_response({
                    "error": f"Failed to fetch MDN content: {str(e)}"
                }, 500)
                
        elif self.path == '/fetch-mdn':
            # Direct API access (non-MCP)
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            request = json.loads(post_data)
            
            url = request.get('url')
            if not url or not url.startswith("https://developer.mozilla.org/"):
                self._send_json_response({
                    "error": "Invalid or missing URL parameter. Only MDN URLs are supported."
                }, 400)
                return
            
            try:
                # Simple MDN scraper
                headers = {'User-Agent': 'Mozilla/5.0'}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    html = response.read().decode('utf-8')
                    
                    # Extract text content
                    result = extract_text_from_html(html)
                    
                    response_data = {
                        "status": "success",
                        "url": url,
                        "title": result["title"],
                        "content": result["content"],
                        "source": "Mozilla Developer Network (MDN)"
                    }
                    
                    self._send_json_response(response_data)
            
            except Exception as e:
                print(f"Error processing request: {str(e)}", file=sys.stderr)
                self._send_json_response({
                    "error": f"Failed to fetch MDN content: {str(e)}"
                }, 500)
        else:
            self._send_json_response({"error": "Endpoint not found"}, 404)

def main():
    """Start the MCP server"""
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting Simple MCP Server on {host}:{port}", file=sys.stderr)
    
    server = HTTPServer((host, port), MCPHandler)
    
    print("Server started. Available endpoints:", file=sys.stderr)
    print(f"  - POST http://{host}:{port}/mcp", file=sys.stderr)
    print(f"  - POST http://{host}:{port}/fetch-mdn", file=sys.stderr)
    print(f"  - GET  http://{host}:{port}/health", file=sys.stderr)
    print(f"  - GET  http://{host}:{port}/mcp/manifest", file=sys.stderr)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopping...", file=sys.stderr)
        server.server_close()

if __name__ == "__main__":
    main()
