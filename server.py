from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# MCP SDK をインポート
from mcp.server.fastmcp import FastMCP, Context

from web_scraper import fetch_mdn_doc, create_mdn_context

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

# MCP サーバーの初期化
mcp = FastMCP("MDN Web Scraper", 
              description="MDNウェブドキュメントをスクレイピングして提供するMCPサーバー")

@app.post("/fetch-mdn")
async def fetch_mdn_endpoint(request: MDNRequest):
    """
    MDNドキュメントを取得するエンドポイント
    
    Args:
        request: MDN URLを含むリクエスト
        
    Returns:
        文書内容
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
    
    return {
        "status": "success",
        "content": context_data["content"],
        "source": context_data["source"],
        "url": context_data["url"]
    }

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return JSONResponse(content={"status": "healthy"})

# MCPリソースの定義
@mcp.resource("mdn://{path}")
async def get_mdn_doc(path: str) -> str:
    """
    MDNウェブドキュメントをリソースとして提供
    
    Args:
        path: ドキュメントのパス
        
    Returns:
        ドキュメントの内容
    """
    url = f"https://developer.mozilla.org/{path}"
    doc_content = await fetch_mdn_doc(url)
    
    if not doc_content:
        return f"Failed to fetch MDN document at {url}"
    
    return doc_content

# MCPツールの定義
@mcp.tool()
async def fetch_mdn_page(url: str, ctx: Context) -> str:
    """
    指定したURLのMDNページを取得して分析
    
    Args:
        url: MDNドキュメントのURL（https://developer.mozilla.org/ で始まる必要があります）
        
    Returns:
        取得したドキュメントの内容
    """
    # URLの検証
    if not url.startswith("https://developer.mozilla.org/"):
        return "Error: URL must start with https://developer.mozilla.org/"
    
    # 進捗報告
    ctx.info(f"Fetching document from {url}")
    
    # ドキュメント取得
    doc_content = await fetch_mdn_doc(url)
    
    if not doc_content:
        return f"Failed to fetch or parse MDN document from {url}"
    
    return doc_content

# FastAPI アプリに MCP サーバーをマウント
app.mount("/mcp", mcp.sse_app())

if __name__ == "__main__":
    # このファイルが直接実行された場合は、uvicornでサーバーを起動
    import uvicorn
    
    # 環境変数からホストとポートを取得（デフォルト値あり）
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting MDN Document Scraper MCP Server on {host}:{port}")
    uvicorn.run("server:app", host=host, port=port, reload=True)
