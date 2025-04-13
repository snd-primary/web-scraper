import asyncio
import sys
import os
from typing import Dict, Any, List, Optional

from mcp import create_app, Request, Response
from pydantic import BaseModel

from web_scraper import fetch_mdn_doc, create_mdn_context

app = create_app()

class MDNRequest(BaseModel):
    url: str

@app.post("/fetch-mdn")
async def fetch_mdn_endpoint(request: Request[MDNRequest]) -> Response:
    """
    MDNドキュメントを取得するエンドポイント
    
    Args:
        request: MDN URLを含むリクエスト
        
    Returns:
        成功または失敗レスポンス
    """
    url = request.body.url
    
    # MDN URLの検証
    if not url.startswith("https://developer.mozilla.org/"):
        return Response.json(
            {"error": "Invalid URL. Only MDN URLs (https://developer.mozilla.org/) are supported."},
            status_code=400
        )
    
    # ドキュメントの取得
    doc_content = await fetch_mdn_doc(url)
    
    if not doc_content:
        return Response.json(
            {"error": "Failed to fetch or parse MDN document."},
            status_code=500
        )
    
    # コンテキストの作成
    context = create_mdn_context(doc_content, url)
    
    return Response.json({
        "status": "success",
        "message": "MDN document fetched successfully",
        "context": context
    })

@app.get("/health")
async def health_check() -> Response:
    """ヘルスチェックエンドポイント"""
    return Response.json({"status": "healthy"})

if __name__ == "__main__":
    # 環境変数からホストとポートを取得（デフォルト値あり）
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting MDN Document Scraper MCP Server on {host}:{port}")
    app.run(host=host, port=port)
