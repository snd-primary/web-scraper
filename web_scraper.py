import httpx
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Optional

async def fetch_mdn_doc(url: str) -> Optional[str]:
    """
    MDNのドキュメントページを取得し、メインコンテンツを抽出する
    
    Args:
        url: MDNドキュメントのURL
        
    Returns:
        抽出されたドキュメントのテキスト内容、取得失敗時はNone
    """
    # URLがMDNのものか確認
    if not url.startswith("https://developer.mozilla.org/"):
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # BeautifulSoupでHTMLを解析
            soup = BeautifulSoup(response.text, "html.parser")
            
            # メインコンテンツを抽出（MDNのメインコンテンツは通常article要素内にある）
            main_content = soup.select_one("article.main-page-content")
            if not main_content:
                # 古いページやレイアウトが変わっている場合の対応
                main_content = soup.select_one("main#content")
            
            if not main_content:
                return None
            
            # 不要な要素を削除（ナビゲーション、広告など）
            for element in main_content.select(".sidebar, .newsletter-container, .prevnext-container"):
                element.decompose()
            
            # タイトルを取得
            title = soup.select_one("h1").text.strip() if soup.select_one("h1") else "MDN Document"
            
            # メタ情報を取得
            meta_desc = soup.select_one('meta[name="description"]')
            description = meta_desc["content"] if meta_desc else ""
            
            # 整形された内容を返す
            content = f"# {title}\n\n{description}\n\n{main_content.get_text(separator='\n', strip=True)}"
            
            # 余分な空行を削除
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            return content
    
    except Exception as e:
        print(f"Error fetching MDN document: {e}")
        return None

def create_mdn_context(doc_content: str, url: str) -> Dict[str, Any]:
    """
    MCPに渡すためのコンテキスト辞書を作成
    
    Args:
        doc_content: 抽出されたドキュメントのテキスト内容
        url: 元のMDN URL
        
    Returns:
        MCP用のコンテキスト辞書
    """
    # MDN URLからIDを生成
    doc_id = url.split("/")[-1] if "/" in url else "mdn-doc"
    
    # MCPの標準フォーマットに合わせたコンテキスト構造
    return {
        "type": "mdn_document",
        "url": url,
        "content": doc_content,
        "source": "Mozilla Developer Network (MDN)",
        "instruction": "以下はMDNから取得したドキュメントです。開発者の質問に答える際にこの情報を参照してください。"
    }
