"""
MCPプロトコルの基本的な実装

このモジュールはModelContextProtocolの基本構造と機能を実装します。
外部パッケージに依存せず、プロジェクト内で使用するための軽量実装です。
"""

from typing import Dict, Any, List, Optional

class MCPContext:
    """MCP互換のコンテキスト構造"""
    def __init__(
        self,
        id: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        attachments: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.content = content
        self.metadata = metadata or {}
        self.attachments = attachments or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """コンテキストを辞書形式に変換"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "attachments": self.attachments
        }

class MCPResponse:
    """MCP互換のレスポンス構造"""
    def __init__(
        self,
        contexts: List[MCPContext],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.contexts = contexts
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """レスポンスを辞書形式に変換"""
        return {
            "contexts": [context.to_dict() for context in self.contexts],
            "metadata": self.metadata
        }

def create_manifest(
    name: str,
    version: str,
    description: str,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    MCPマニフェストを作成する
    
    Args:
        name: サーバー名
        version: バージョン
        description: 説明
        parameters: パラメータスキーマ
        
    Returns:
        MCP互換のマニフェスト辞書
    """
    return {
        "name": name,
        "version": version,
        "description": description,
        "protocols": {
            "mcp": "1.0.0"
        },
        "parameters": parameters or {}
    }
