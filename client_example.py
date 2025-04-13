#!/usr/bin/env python
"""
MDN Web Document Scraperのクライアント例 (MCP仕様準拠)

使い方:
  python client_example.py <MDN URL>

例:
  python client_example.py https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array
"""

import sys
import asyncio
import json
import httpx
from typing import Dict, Any, List, Optional

async def fetch_mdn_doc_mcp(url: str, server_url: str = "http://127.0.0.1:8000") -> Optional[Dict[str, Any]]:
    """
    MDN Web Document ScraperからMDNドキュメントをMCP準拠で取得する

    Args:
        url: MDNのドキュメントURL
        server_url: MDN Web Document ScraperのURL

    Returns:
        取得したドキュメントのコンテキスト
    """
    # MCPの標準エンドポイントを使用
    endpoint = f"{server_url}/mcp/contexts"
    
    # MCP標準フォーマットのリクエスト
    mcp_request = {
        "parameters": {
            "url": url
        },
        "metadata": {
            "client": "mdn-scraper-client-example"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json=mcp_request
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        
        # MCPレスポンスからコンテキストを抽出
        contexts = data.get("contexts", [])
        if contexts and len(contexts) > 0:
            return contexts[0]
        
        return None

async def fetch_mdn_doc_legacy(url: str, server_url: str = "http://127.0.0.1:8000") -> Optional[Dict[str, Any]]:
    """
    MDN Web Document ScraperからMDNドキュメントを従来の方法で取得する
    (後方互換性のため)

    Args:
        url: MDNのドキュメントURL
        server_url: MDN Web Document ScraperのURL

    Returns:
        取得したドキュメントのコンテキスト
    """
    endpoint = f"{server_url}/fetch-mdn"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json={"url": url}
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        return data.get("context")

async def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    mdn_url = sys.argv[1]
    print(f"Fetching MDN documentation from: {mdn_url}")
    print("Using MCP-compatible endpoint...")
    
    # MCP互換エンドポイントを使用してドキュメントを取得
    context = await fetch_mdn_doc_mcp(mdn_url)
    
    if context:
        print("\n=== MDN Document fetched successfully ===")
        
        # context構造がMCP準拠の形式に変更されているため、データの取得方法を調整
        content_text = context.get("content", {}).get("text", "")
        title = content_text.split("\n")[0].replace("# ", "") if content_text else "No title"
        
        print(f"Title: {title}")
        print(f"Source: {context.get('metadata', {}).get('source', 'Unknown')}")
        print(f"URL: {context.get('metadata', {}).get('url', 'Unknown')}")
        
        print("\nContent preview (first 500 chars):")
        preview = content_text[:500] + "..." if len(content_text) > 500 else content_text
        print(preview)
        
        # 結果をファイルに保存するオプション
        save = input("\nSave the full document to a file? (y/n): ")
        if save.lower() == 'y':
            filename = f"mdn_doc_{mdn_url.split('/')[-1]}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content_text)
            print(f"Document saved to {filename}")
    else:
        print("Failed to fetch MDN document")
        
        # フォールバック: 従来のエンドポイントを試す
        print("Trying legacy endpoint...")
        legacy_context = await fetch_mdn_doc_legacy(mdn_url)
        
        if legacy_context:
            print("\n=== MDN Document fetched successfully (using legacy endpoint) ===")
            print(f"Title: {legacy_context['content'].split('\\n')[0]}")
            print(f"Source: {legacy_context['source']}")
            print(f"URL: {legacy_context['url']}")
            
            print("\nContent preview (first 500 chars):")
            preview = legacy_context['content'][:500] + "..." if len(legacy_context['content']) > 500 else legacy_context['content']
            print(preview)
            
            # 結果をファイルに保存するオプション
            save = input("\nSave the full document to a file? (y/n): ")
            if save.lower() == 'y':
                filename = f"mdn_doc_{mdn_url.split('/')[-1]}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(legacy_context['content'])
                print(f"Document saved to {filename}")
        else:
            print("Failed to fetch MDN document with both endpoints")

if __name__ == "__main__":
    asyncio.run(main())
