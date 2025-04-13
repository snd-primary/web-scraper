# MDN Web Document Scraper for LLM Applications

MDN Web Document Scraperは、[Mozilla Developer Network (MDN)](https://developer.mozilla.org/) のドキュメントを取得し、Claude Desktop などのLLMアプリケーションで利用できるようにするMCPサーバーです。

## 機能

- MDNのドキュメントURLを受け取り、ドキュメントのメインコンテンツを抽出
- LLM用に整形されたコンテキストとしてドキュメント内容を提供
- MCPプロトコルを使用したAPIエンドポイント

## 必要条件

- Python 3.13以上
- 依存パッケージ：httpx, mcp, beautifulsoup4, pydantic

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
```

サーバーはデフォルトで `http://127.0.0.1:8000` で起動します。

### APIエンドポイント

#### MDNドキュメントの取得

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

## LLMアプリとの連携

このMCPサーバーは、Claude DesktopなどのLLMアプリケーションと連携することを目的としています。
LLMアプリはこのサーバーを通じて最新のMDNドキュメントにアクセスでき、開発者の質問に適切に回答できるようになります。

## ライセンス

MITライセンス
