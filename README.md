# MDN Web Document Scraper for LLM Applications

MDN Web Document Scraper は、[Mozilla Developer Network (MDN)](https://developer.mozilla.org/) のドキュメントを取得し、Claude Desktop などの LLM アプリケーションで利用できるようにする Model Context Protocol (MCP)サーバーです。

## 機能

- MDN のドキュメント URL を受け取り、ドキュメントのメインコンテンツを抽出
- LLM 用に整形されたコンテキストとしてドキュメント内容を提供
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)仕様に準拠した API エンドポイント

## 必要条件

- Python 3.13 以上
- 依存パッケージ：httpx, fastapi, uvicorn, beautifulsoup4, pydantic

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/snd-primary/web-scraper.git
cd web-scraper


# 依存関係をインストール
uv pip install .
# または個別にインストール
uv pip install httpx fastapi uvicorn beautifulsoup4 pydantic

```

## 使い方

### サーバーの起動

```bash
# 直接実行
uv run main.py

# または環境変数でホスト/ポートを指定
HOST=0.0.0.0 PORT=9000 python main.py

# 開発モード（ファイル変更時に自動再起動）
DEBUG=true python main.py
```

サーバーはデフォルトで `http://127.0.0.1:8000` で起動します。

### API エンドポイント

#### MCP 標準エンドポイント

MCP プロトコルに準拠したメインエンドポイント:

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

#### MCP マニフェスト取得エンドポイント

```http
GET /mcp/manifest
```

MCP 接続設定に必要なマニフェスト情報を提供します。

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

## Claude Desktop との連携

この MCP サーバーは Claude Desktop と連携して使用できます。以下の手順で設定を行ってください。

### Claude Desktop での設定方法

1. Claude Desktop を起動し、「設定」または「Settings」メニューを開きます
2. 「MCP Connections」または「MCP サーバー接続」の設定項目を選択します
3. 「Add Connection」または「接続を追加」ボタンをクリックします
4. 以下の情報を入力します：
   - **名前**: MDN Document Scraper（任意）
   - **エンドポイント URL**: `http://127.0.0.1:8000/mcp/contexts`（または実際のサーバー URL）
   - **種類**: MCP サーバー
5. 「Save」または「保存」をクリックして設定を完了します

### 使用方法

1. MDN Web Scraper MCP サーバーを起動します
2. Claude Desktop で会話中に、MDN ドキュメントに関する質問をします
3. 必要に応じて、「Add Context」または「コンテキストを追加」機能を使って、MDN Web Scraper を選択し、特定の URL を指定することもできます

例：

```
MDN Web ScraperからJavaScriptのArray.prototype.reduceについて情報を取得して説明してください。
URL: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reduce
```

## LLM アプリとの連携

この MCP サーバーは、[Model Context Protocol](https://modelcontextprotocol.io/)仕様に準拠した LLM アプリケーションと連携することを目的としています。
LLM アプリはこのサーバーを通じて最新の MDN ドキュメントにアクセスでき、開発者の質問に適切に回答できるようになります。

### MCP プロトコルについて

Model Context Protocol (MCP)は、LLM と外部コンテキストソースが対話するための標準プロトコルです。
詳細は[MCP 公式ドキュメント](https://modelcontextprotocol.io/introduction)を参照してください。

## ライセンス

MIT ライセンス
