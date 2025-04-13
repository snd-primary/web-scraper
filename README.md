# Web Scraper MCP Server

Pythonで実装されたModelContextProtocol（MCP）サーバーで、ウェブスクレイピング機能を提供します。Claude Desktopと連携して使用できます。

## 機能

- 任意のウェブサイトからコンテンツをスクレイピング
- CSSセレクタを使用して特定の要素を抽出
- MCPプロトコルを通じてClaudeとシームレスに連携

## インストール

1. リポジトリをクローン:
   ```bash
   git clone https://github.com/snd-primary/web-scraper.git
   cd web-scraper
   ```

2. 依存関係のインストール:
   ```bash
   pip install -r requirements.txt
   ```

## Claude Desktopでの使用方法

1. `claude_desktop_config.json` ファイルを更新して、web-scraper MCPサーバーを含めます:

   ```json
   {
     "mcpServers": {
       "github": {
         "command": "node",
         "args": [
           "C:\\Program Files\\nodejs\\node_modules\\@modelcontextprotocol\\server-github\\dist\\index.js"
         ],
         "env": {
           "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token"
         }
       },
       "web-scraper": {
         "command": "python",
         "args": [
           "C:\\path\\to\\web-scraper\\web_scraper_server.py"
         ]
       }
     }
   }
   ```

   `C:\\path\\to\\web-scraper` を、実際のリポジトリをクローンした場所のパスに置き換えてください。Windowsのパスでは、バックスラッシュを二重にする必要があることに注意してください。

2. 設定を適用するために、Claude Desktopを再起動します。

3. Claude Desktopで、web-scraper MCPサーバーを使用できるようになります:
   ```
   https://example.com の内容をスクレイピングして、何について書かれているか教えてください。
   ```

   または、セレクタを使用する場合:
   ```
   ニュースサイト https://news-site.com から、セレクタ ".headline" を使用して見出し記事をスクレイピングしてください。
   ```

## API リファレンス

web-scraper MCPサーバーは以下の関数を提供します:

### scrape

ウェブサイトからコンテンツをスクレイピングします。

**パラメータ:**
- `url` (文字列, 必須): スクレイピングするウェブサイトのURL
- `selector` (文字列, オプション): 特定の要素をターゲットにするCSSセレクタ

**戻り値:**
- セレクタが提供された場合:
  - マッチする要素のテキストとHTML
  - マッチする要素の数
- セレクタが提供されない場合:
  - ページのタイトル
  - メタ description
  - 本文テキストの最初の1000文字
