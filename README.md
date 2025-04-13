# MDN Web Document Scraper for LLM Applications

MDN Web Document Scraperは、[Mozilla Developer Network (MDN)](https://developer.mozilla.org/) のドキュメントを取得し、Claude Desktop などのLLMアプリケーションで利用できるようにするModel Context Protocol (MCP)サーバーです。

## 機能

- MDNのドキュメントURLを受け取り、ドキュメントのメインコンテンツを抽出
- LLM用に整形されたコンテキストとしてドキュメント内容を提供
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)仕様に準拠したAPIエンドポイント

## 必要条件

- Python 3.13以上
- 依存パッケージ：httpx, fastapi, uvicorn, beautifulsoup4, pydantic

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/snd-primary/web-scraper.git
cd web-scraper

# 依存関係をインストール
python -m pip install .
```

## 使い方

### サーバーの起動

```bash
# 直接実行
python main.py

# または環境変数でホスト/ポートを指定
HOST=0.0.0.0 PORT=9000 python main.py

# 開発モード（ファイル変更時に自動再起動）
DEBUG=true python main.py
```

サーバーはデフォルトで `http://127.0.0.1:8000` で起動します。

### APIエンドポイント

#### MCP標準エンドポイント

MCPプロトコルに準拠したメインエンドポイント:

```http
POST /mcp/contexts
```

リクエスト例：

```json
{
  "parameters": {
    "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array"
  },
  "metadata": {
    "client": "sample-client"
  }
}
```

レスポンス例：

```json
{
  "contexts": [
    {
      "id": "mdn-Array",
      "content": {
        "text": "# Array\n\nJavaScript の Array オブジェクトは...",
        "format": "markdown"
      },
      "metadata": {
        "source": "Mozilla Developer Network (MDN)",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array",
        "type": "mdn_document",
        "instruction": "以下はMDNから取得したドキュメントです。開発者の質問に答える際にこの情報を参照してください。"
      }
    }
  ],
  "metadata": {
    "status": "success",
    "message": "MDN document fetched successfully"
  }
}
```

#### MCPマニフェスト取得エンドポイント

```http
GET /mcp/manifest
```

MCP接続設定に必要なマニフェスト情報を提供します。

#### 従来のエンドポイント (後方互換性)

```http
POST /fetch-mdn
```

リクエスト例：

```json
{
  "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array"
}
```

レスポンス例：

```json
{
  "status": "success",
  "message": "MDN document fetched successfully",
  "context": {
    "type": "mdn_document",
    "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array",
    "content": "# Array\n\nJavaScript の Array オブジェクトは...",
    "source": "Mozilla Developer Network (MDN)",
    "instruction": "以下はMDNから取得したドキュメントです。開発者の質問に答える際にこの情報を参照してください。"
  }
}
```

#### ヘルスチェック

```http
GET /health
```

レスポンス例：

```json
{
  "status": "healthy"
}
```

## Claude Desktopとの連携

このMCPサーバーはClaude Desktopと連携して使用できます。以下の手順で設定を行ってください。

### Claude Desktopでの設定方法

1. Claude Desktopを起動し、「設定」または「Settings」メニューを開きます
2. 「MCP Connections」または「MCPサーバー接続」の設定項目を選択します
3. 「Add Connection」または「接続を追加」ボタンをクリックします
4. 以下の情報を入力します：
   - **名前**: MDN Document Scraper（任意）
   - **エンドポイントURL**: `http://127.0.0.1:8000/mcp/contexts`（または実際のサーバーURL）
   - **種類**: MCPサーバー
5. 「Save」または「保存」をクリックして設定を完了します

### 使用方法

1. MDN Web Scraper MCPサーバーを起動します
2. Claude Desktopで会話中に、MDNドキュメントに関する質問をします
3. 必要に応じて、「Add Context」または「コンテキストを追加」機能を使って、MDN Web Scraperを選択し、特定のURLを指定することもできます

例：
```
MDN Web ScraperからJavaScriptのArray.prototype.reduceについて情報を取得して説明してください。
URL: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reduce
```

## LLMアプリとの連携

このMCPサーバーは、[Model Context Protocol](https://modelcontextprotocol.io/)仕様に準拠したLLMアプリケーションと連携することを目的としています。
LLMアプリはこのサーバーを通じて最新のMDNドキュメントにアクセスでき、開発者の質問に適切に回答できるようになります。

### MCPプロトコルについて

Model Context Protocol (MCP)は、LLMと外部コンテキストソースが対話するための標準プロトコルです。
詳細は[MCP公式ドキュメント](https://modelcontextprotocol.io/introduction)を参照してください。

## ライセンス

MITライセンス
