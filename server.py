from contextlib import asynccontextmanager
import os
import json
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from web_scraper import fetch_mdn_doc, create_mdn_context
from mcp_protocol import MCPContext, MCPResponse

# リクエストモデル定義
class MDNRequest(BaseModel):
    """MDNドキュメント取得リクエストのモデル"""
    url: str

# FastAPIアプリケーションの起動
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時処理
    print("Starting MDN Document Scraper MCP Server...")
    yield
    # 終了時処理
    print("Shutting down MDN Document Scraper MCP Server...")

app = FastAPI(lifespan=lifespan)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/fetch-mdn")
async def fetch_mdn_endpoint(request: MDNRequest) -> Dict[str, Any]:
    """
    MDNドキュメントを取得するエンドポイント
    
    Args:
        request: MDN URLを含むリクエスト
        
    Returns:
        MCP互換のレスポンス
    """
    # MDN URLの検証
    if not request.url.startswith("https://developer.mozilla.org/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL. Only MDN URLs (https://developer.mozilla.org/) are supported."
        )
    
    # ドキュメントの取得
    doc_content = await fetch_mdn_doc(request.url)
    
    if not doc_content:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch or parse MDN document."
        )
    
    # コンテキストの作成
    context_data = create_mdn_context(doc_content, request.url)
    
    # MCP互換形式でレスポンスを構築
    context_id = f"mdn-{request.url.split('/')[-1]}"
    
    mcp_context = MCPContext(
        id=context_id,
        content={
            "text": context_data["content"],
            "format": "markdown"
        },
        metadata={
            "source": context_data["source"],
            "url": context_data["url"],
            "type": context_data["type"],
            "instruction": context_data["instruction"]
        }
    )
    
    response = MCPResponse(
        contexts=[mcp_context],
        metadata={
            "status": "success",
            "message": "MDN document fetched successfully"
        }
    )
    
    return response.to_dict()

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return JSONResponse(content={"status": "healthy"})

# MCP マニフェストの提供
@app.get("/mcp/manifest")
async def mcp_manifest():
    """MCPマニフェストを提供するエンドポイント"""
    try:
        with open('mcp_manifest.json', 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        return JSONResponse(content=manifest_data)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="MCP manifest file not found."
        )

# MCP 互換の統合エンドポイント
@app.post("/mcp/contexts")
async def mcp_contexts_endpoint(request: Request) -> Dict[str, Any]:
    """
    MCP標準の統合エンドポイント
    このエンドポイントではMDN URLをパラメータとして受け取り、処理します
    
    Args:
        request: MCP互換リクエスト
        
    Returns:
        MCP互換のレスポンス
    """
    data = await request.json()
    
    # リクエストからURLを抽出
    url = data.get("parameters", {}).get("url", "")
    
    if not url:
        raise HTTPException(
            status_code=400,
            detail="URL parameter is required."
        )
    
    # 内部の既存実装を活用
    mdn_request = MDNRequest(url=url)
    return await fetch_mdn_endpoint(mdn_request)

if __name__ == "__main__":
    # このファイルが直接実行された場合は、uvicornでサーバーを起動
    import uvicorn
    
    # 環境変数からホストとポートを取得（デフォルト値あり）
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting MDN Document Scraper MCP Server on {host}:{port}")
    uvicorn.run("server:app", host=host, port=port, reload=True)
