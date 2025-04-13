import asyncio
import sys
import os
from typing import Dict, Any, List, Optional

# MCPのインポート部分を修正
import mcp
from pydantic import BaseModel

from web_scraper import fetch_mdn_doc, create_mdn_context

# MCPアプリケーション作成方法を修正
app = mcp.App()

class MDNRequest(BaseModel):
    url: str

@app.post("/fetch-mdn")
async def fetch_mdn_endpoint(request: mcp.Request) -> mcp.Response:
    """
    MDNドキュメントを取得するエンドポイント
    
    Args:
        request: MDN URLを含むリクエスト
        
    Returns:
        成功または失敗レスポンス
    """
    # リクエストボディをパース
    body = await request.json()
    url = body.get("url", "")
    
    # MDN URLの検証
    if not url.startswith("https://developer.mozilla.org/"):
        return mcp.Response(
            json={"error": "Invalid URL. Only MDN URLs (https://developer.mozilla.org/) are supported."},
            status_code=400
        )
    
    # ドキュメントの取得
    doc_content = await fetch_mdn_doc(url)
    
    if not doc_content:
        return mcp.Response(
            json={"error": "Failed to fetch or parse MDN document."},
            status_code=500
        )
    
    # コンテキストの作成
    context = create_mdn_context(doc_content, url)
    
    return mcp.Response(
        json={
            "status": "success",
            "message": "MDN document fetched successfully",
            "context": context
        }
    )

@app.get("/health")
async def health_check() -> mcp.Response:
    """ヘルスチェックエンドポイント"""
    return mcp.Response(json={"status": "healthy"})

if __name__ == "__main__":
    # 環境変数からホストとポートを取得（デフォルト値あり）
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting MDN Document Scraper MCP Server on {host}:{port}")
    app.run(host=host, port=port)
