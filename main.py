import os
import sys
import asyncio
from server import app

def main():
    """
    MDN Web Scraper MCPサーバーのエントリーポイント
    """
    print("Starting MDN Web Scraper MCP Server...")
    
    # 環境変数からホストとポートを取得（デフォルト値あり）
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Server running at: http://{host}:{port}")
    print("Available endpoints:")
    print(f"  - POST http://{host}:{port}/fetch-mdn")
    print(f"  - GET  http://{host}:{port}/health")
    
    # サーバーを起動
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
