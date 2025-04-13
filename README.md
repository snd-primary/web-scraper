# Web Scraper MCP Server

A ModelContextProtocol (MCP) server for web scraping, designed to be used with Claude Desktop.

## Features

- Scrape content from any website
- Filter content using CSS selectors
- Seamlessly integrate with Claude through the MCP protocol

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/snd-primary/web-scraper.git
   cd web-scraper
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Build the project:
   ```bash
   npm run build
   ```

## Usage with Claude Desktop

1. Update your `claude_desktop_config.json` file to include the web-scraper MCP server:

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
         "command": "node",
         "args": [
           "path/to/web-scraper/dist/index.js"
         ]
       }
     }
   }
   ```

   Replace `path/to/web-scraper` with the actual path to where you cloned this repository.

2. Restart Claude Desktop to load the updated configuration.

3. In Claude Desktop, you can now use the web-scraper MCP server:
   ```
   Please scrape the content from https://example.com and tell me what it contains.
   ```

## API Reference

The web-scraper MCP server provides the following function:

### scrape

Scrapes content from a website.

**Parameters:**
- `url` (string, required): The URL of the website to scrape
- `selector` (string, optional): CSS selector to target specific elements

**Returns:**
- If a selector is provided:
  - Text and HTML of matching elements
  - Count of matching elements
- If no selector is provided:
  - Page title
  - Meta description
  - First 1000 characters of body text

## Development

To run the server in development mode:

```bash
npm run dev
```

## License

MIT
