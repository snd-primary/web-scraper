# Web Scraper MCP Server

Pythonで実装されたModelContextProtocol（MCP）サーバーで、ウェブスクレイピング機能を提供します。Claude Desktopと連携して使用できます。

## 機能

- MDNウェブドキュメントからコンテンツをスクレイピング
- MCPプロトコルを通じてClaudeとシームレスに連携
- 標準ライブラリのみで実装された軽量バージョンを選択可能

## インストール

1. リポジトリをクローン:
   ```bash
   git clone https://github.com/snd-primary/web-scraper.git
   cd web-scraper
   ```

2. 標準版を使用する場合は、依存関係をインストール:
   ```bash
   pip install -r requirements.txt
   ```

## Claude Desktopでの使用方法

### 軽量版 (外部依存なし)

**"Server transport closed" エラーが発生する場合は、こちらの方法をお試しください**

この軽量版は外部パッケージに依存せず、Pythonの標準ライブラリのみで実装されています。

1. `claude_desktop_config.json` ファイルを作成または更新:

   ```json
   {
     "mcpServers": {
       "web-scraper": {
         "command": "python",
         "args": [
           "C:\\path\\to\\web-scraper\\claude_desktop_mcp.py"
         ]
       }
     }
   }
   ```

   `C:\\path\\to\\web-scraper` を、実際のリポジトリをクローンした場所のパスに置き換えてください。Windowsのパスでは、バックスラッシュを二重にする必要があることに注意してください。

2. 設定を適用するために、Claude Desktopを再起動します。

3. Claude Desktopで、web-scraper MCPサーバーを使用できるようになります:
   ```
   https://developer.mozilla.org/en-US/docs/Web/JavaScript の内容をスクレイピングして、JavaScriptについての基本情報を教えてください。
   ```

### 標準版 (フル機能)

こちらは外部パッケージを使用した、より多機能な実装です。

1. `claude_desktop_config.json` ファイルを更新:

   ```json
   {
     "mcpServers": {
       "web-scraper": {
         "command": "python",
         "args": [
           "C:\\path\\to\\web-scraper\\main.py"
         ]
       }
     }
   }
   ```

   `C:\\path\\to\\web-scraper` を、実際のリポジトリをクローンした場所のパスに置き換えてください。

2. 設定を適用するために、Claude Desktopを再起動します。

## トラブルシューティング

### "No module named 'uvicorn'" エラー

このエラーが発生する場合は、以下の方法で解決できます:

1. 依存関係を確認してインストール:
   ```bash
   pip install uvicorn fastapi httpx beautifulsoup4
   ```

2. それでも解決しない場合は、軽量版を使用してください:
   ```
   claude_desktop_mcp.py
   ```

   こちらはPythonの標準ライブラリのみで実装されているため、外部依存関係なしで動作します。

### "Server transport closed unexpectedly" エラー

1. `claude_desktop_mcp.py` を使用してください。
2. 起動時にエラーが出る場合は、コンソール出力を確認してください。
3. 依然として問題が解決しない場合は、[Model Context Protocol Debugging Documentation](https://modelcontextprotocol.io/docs/tools/debugging)を参照してください。

## API リファレンス

web-scraper MCPサーバーは以下の機能を提供します:

### fetch-mdn

MDNウェブドキュメントからコンテンツをスクレイピングします。

**パラメータ:**
- `url` (文字列, 必須): スクレイピングするMDNウェブサイトのURL（https://developer.mozilla.org/ で始まる必要があります）

**戻り値:**
- ドキュメントのタイトル
- コンテンツテキスト
- 元のURL
- ソース情報

## 実装ファイル

- `main.py` - 標準版MCPサーバーのエントリーポイント（外部依存あり）
- `server.py` - FastAPIを使用したMCPサーバーの実装
- `web_scraper.py` - ウェブスクレイピング機能の実装
- `claude_desktop_mcp.py` - 軽量版MCPサーバー（標準ライブラリのみ）
- `requirements.txt` - 必要なPythonパッケージのリスト
