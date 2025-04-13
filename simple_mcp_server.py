#!/usr/bin/env python
"""
Simplified MCP Server for Web Scraping

This standalone implementation provides a minimalistic MCP server
that can be run without external dependencies beyond the standard library.
It follows the Model Context Protocol specification but uses only Python standard libraries.
"""

import json
import sys
import os
import socket
import threading
import urllib.request
import urllib.error
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List, Optional
import time
import ssl
import urllib.parse

# HTML parsing functions (simple version without BeautifulSoup)
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

def fetch_mdn_doc(url):
    """Fetch MDN documentation without external dependencies"""
    if not url.startswith("https://developer.mozilla.org/"):
        return {"error": "Only MDN URLs are supported"}
    
    try:
        # Set up request with user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        
        # Make the request
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
            # Extract text content
            result = extract_text_from_html(html)
            
            return {
                "url": url,
                "title": result["title"],
                "content": result["content"],
                "source": "Mozilla Developer Network (MDN)"
            }
    
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}", file=sys.stderr)
        return {"error": f"Failed to fetch content: {str(e)}"}

# MCP Protocol Implementation
class MCPContext:
    """MCP context object following protocol spec"""
    def __init__(self, id, content, metadata=None, attachments=None):
        self.id = id
        self.content = content
        self.metadata = metadata or {}
        self.attachments = attachments or {}
    
    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "attachments": self.attachments
        }

class MCPResponse:
    """MCP response object following protocol spec"""
    def __init__(self, contexts, metadata=None):
        self.contexts = contexts
        self.metadata = metadata or {}
    
    def to_dict(self):
        return {
            "contexts": [ctx.to_dict() for ctx in self.contexts],
            "metadata": self.metadata
        }

class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP requests"""
    
    def _set_response(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self._set_response()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self._set_response()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
            return
        
        if self.path == '/mcp-manifest.json' or self.path == '/mcp/manifest':
            manifest = {
                "name": "mdn-web-scraper",
                "version": "1.0.0",
                "description": "MDNウェブドキュメントをスクレイピングして提供するMCPサーバー",
                "protocols": {
                    "mcp": "1.0.0"
                },
                "parameters": {
                    "url": {
                        "type": "string",
                        "description": "取得するMDN URLを指定してください",
                        "required": True
                    }
                }
            }
            self._set_response()
            self.wfile.write(json.dumps(manifest).encode())
            return
        
        # Default 404 response
        self._set_response(404)
        self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        """Handle POST requests for MCP or direct API access"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request_body = json.loads(post_data)
            
            # MCP protocol endpoint
            if self.path == '/mcp':
                # Handle according to MCP protocol
                print("Received MCP request", file=sys.stderr)
                
                # Extract parameters from MCP request
                parameters = request_body.get('parameters', {})
                url = parameters.get('url')
                
                if not url:
                    self._set_response(400)
                    self.wfile.write(json.dumps({"error": "URL parameter is required"}).encode())
                    return
                
                # Fetch the MDN document
                result = fetch_mdn_doc(url)
                
                if 'error' in result:
                    self._set_response(500)
                    self.wfile.write(json.dumps({"error": result['error']}).encode())
                    return
                
                # Create MCP response with context
                context = MCPContext(
                    id=f"mdn-{int(time.time())}",
                    content={
                        "type": "mdn_document",
                        "url": result["url"],
                        "title": result["title"],
                        "content": result["content"],
                        "source": result["source"]
                    },
                    metadata={
                        "source": "mdn-web-scraper",
                        "timestamp": time.time()
                    }
                )
                
                response = MCPResponse(
                    contexts=[context],
                    metadata={
                        "request_id": f"req-{int(time.time())}",
                        "server": "mdn-web-scraper-mcp"
                    }
                )
                
                self._set_response()
                self.wfile.write(json.dumps(response.to_dict()).encode())
                return
                
            # Direct API endpoint
            elif self.path == '/fetch-mdn':
                url = request_body.get('url')
                
                if not url:
                    self._set_response(400)
                    self.wfile.write(json.dumps({"error": "URL parameter is required"}).encode())
                    return
                
                result = fetch_mdn_doc(url)
                
                if 'error' in result:
                    self._set_response(500)
                    self.wfile.write(json.dumps({"error": result['error']}).encode())
                    return
                
                self._set_response()
                self.wfile.write(json.dumps(result).encode())
                return
            
            # Default 404 for unknown endpoints
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
            
        except json.JSONDecodeError:
            self._set_response(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        except Exception as e:
            print(f"Error processing request: {str(e)}", file=sys.stderr)
            self._set_response(500)
            self.wfile.write(json.dumps({"error": f"Internal server error: {str(e)}"}).encode())

def main():
    """Start the simplified MCP server"""
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting Simplified MDN Web Scraper MCP Server on {host}:{port}", file=sys.stderr)
    
    server = HTTPServer((host, port), MCPRequestHandler)
    
    print("Server started. Available endpoints:", file=sys.stderr)
    print(f"  - POST http://{host}:{port}/mcp", file=sys.stderr)
    print(f"  - POST http://{host}:{port}/fetch-mdn", file=sys.stderr)
    print(f"  - GET  http://{host}:{port}/health", file=sys.stderr)
    print(f"  - GET  http://{host}:{port}/mcp-manifest.json", file=sys.stderr)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopping...", file=sys.stderr)
        server.server_close()

if __name__ == "__main__":
    main()
