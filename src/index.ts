import { McpServer } from '@modelcontextprotocol/server';
import { scrapeWebsite } from './scraper';

// Initialize the MCP Server
const server = new McpServer({
  name: 'web-scraper',
  version: '1.0.0',
  description: 'MCP server for web scraping',
});

// Register the scrape function
server.registerFunction({
  name: 'scrape',
  description: 'Scrape content from a website URL',
  parameters: {
    type: 'object',
    properties: {
      url: {
        type: 'string',
        description: 'The URL of the website to scrape',
      },
      selector: {
        type: 'string',
        description: 'Optional CSS selector to target specific elements',
      },
    },
    required: ['url'],
  },
  handler: async ({ url, selector }) => {
    try {
      const scrapedData = await scrapeWebsite(url, selector);
      return { success: true, data: scrapedData };
    } catch (error) {
      if (error instanceof Error) {
        return { success: false, error: error.message };
      }
      return { success: false, error: 'Unknown error occurred' };
    }
  },
});

// Start the server
server.start();

console.log('Web Scraper MCP Server started');
