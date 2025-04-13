#!/usr/bin/env python
"""
MDN Web Scraper MCPサーバーのエントリーポイント

このスクリプトはMDN Web Scraper MCPサーバーを起動します。
MCPプロトコルに準拠し、MDNウェブドキュメントをスクレイピングして
LLMアプリケーションに適したコンテキストとして提供します。
"""

import os
import uvicorn
from typing import Optional

def main():
    """
    MDN Web Scraper MCPサーバーのエントリーポイント
    """
    print("Starting MDN Web Scraper MCP Server...")
    
    # 環境変数からホストとポートを取得（デフォルト値あり）
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Server running at: http://{host}:{port}")
    print("Available MCP endpoints:")
    print(f"  - POST http://{host}:{port}/mcp/contexts")
    print("Available custom endpoints:")
    print(f"  - POST http://{host}:{port}/fetch-mdn")
    print(f"  - GET  http://{host}:{port}/health")
    
    # FastAPIアプリケーションをuvicornで起動
    uvicorn.run(
        "server:app", 
        host=host, 
        port=port, 
        reload=os.environ.get("DEBUG", "").lower() == "true"
    )

if __name__ == "__main__":
    main()
