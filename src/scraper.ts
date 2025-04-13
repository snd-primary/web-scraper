import axios from 'axios';
import * as cheerio from 'cheerio';

/**
 * Scrape content from a website
 * @param url The URL of the website to scrape
 * @param selector Optional CSS selector to target specific elements
 * @returns Object containing scraped content
 */
export async function scrapeWebsite(url: string, selector?: string): Promise<any> {
  try {
    // Validate URL
    const urlObj = new URL(url);
    
    // Make the request
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      },
    });

    // Parse the HTML
    const $ = cheerio.load(response.data);
    
    // If a selector is provided, extract content from those elements
    if (selector) {
      const elements = $(selector);
      
      // If multiple elements are selected, return an array of their text/html
      if (elements.length > 1) {
        const results: { text: string; html: string }[] = [];
        
        elements.each((i, el) => {
          results.push({
            text: $(el).text().trim(),
            html: $(el).html() || '',
          });
        });
        
        return {
          url: url,
          selector: selector,
          count: elements.length,
          results: results,
        };
      } 
      // If a single element is selected, return its text/html
      else if (elements.length === 1) {
        return {
          url: url,
          selector: selector,
          text: elements.text().trim(),
          html: elements.html() || '',
        };
      }
      // If no elements match the selector
      else {
        return {
          url: url,
          selector: selector,
          count: 0,
          message: 'No elements found matching the provided selector',
        };
      }
    } 
    // If no selector is provided, return basic page information
    else {
      return {
        url: url,
        title: $('title').text().trim(),
        description: $('meta[name="description"]').attr('content') || '',
        bodyText: $('body').text().trim().substring(0, 1000) + '...',
      };
    }
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to scrape ${url}: ${error.message}`);
    }
    throw new Error(`Failed to scrape ${url}: Unknown error`);
  }
}
