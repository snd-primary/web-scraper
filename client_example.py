#!/usr/bin/env python
"""
MDN Web Document Scraperのクライアント例

使い方:
  python client_example.py <MDN URL>

例:
  python client_example.py https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array
"""

import sys
import asyncio
import json
import httpx

async def fetch_mdn_doc(url, server_url="http://127.0.0.1:8000"):
    """
    MDN Web Document ScraperからMDNドキュメントを取得する

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
        return data["context"] if "context" in data else None

async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    mdn_url = sys.argv[1]
    print(f"Fetching MDN documentation from: {mdn_url}")
    
    context = await fetch_mdn_doc(mdn_url)
    
    if context:
        print("\n=== MDN Document fetched successfully ===")
        print(f"Title: {context['content'].split('\\n')[0]}")
        print(f"Source: {context['source']}")
        print(f"URL: {context['url']}")
        print("\nContent preview (first 500 chars):")
        preview = context['content'][:500] + "..." if len(context['content']) > 500 else context['content']
        print(preview)
        
        # 結果をファイルに保存するオプション
        save = input("\nSave the full document to a file? (y/n): ")
        if save.lower() == 'y':
            filename = f"mdn_doc_{mdn_url.split('/')[-1]}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(context['content'])
            print(f"Document saved to {filename}")
    else:
        print("Failed to fetch MDN document")

if __name__ == "__main__":
    asyncio.run(main())
