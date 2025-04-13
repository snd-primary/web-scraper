from modelcontextprotocol import McpServer
import requests
from bs4 import BeautifulSoup
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_website(url, selector=None):
    """
    Scrape content from a website
    
    Args:
        url (str): The URL of the website to scrape
        selector (str, optional): CSS selector to target specific elements
        
    Returns:
        dict: Scraped content
    """
    try:
        # Set a user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # If a selector is provided, extract content from those elements
        if selector:
            elements = soup.select(selector)
            
            # If multiple elements are selected, return an array of their text/html
            if len(elements) > 1:
                results = []
                
                for element in elements:
                    results.append({
                        'text': element.get_text().strip(),
                        'html': str(element)
                    })
                
                return {
                    'url': url,
                    'selector': selector,
                    'count': len(elements),
                    'results': results
                }
            
            # If a single element is selected, return its text/html
            elif len(elements) == 1:
                return {
                    'url': url,
                    'selector': selector,
                    'text': elements[0].get_text().strip(),
                    'html': str(elements[0])
                }
            
            # If no elements match the selector
            else:
                return {
                    'url': url,
                    'selector': selector,
                    'count': 0,
                    'message': 'No elements found matching the provided selector'
                }
        
        # If no selector is provided, return basic page information
        else:
            title = soup.title.string.strip() if soup.title else 'No title found'
            description = soup.find('meta', attrs={'name': 'description'})
            description = description['content'] if description else ''
            
            # Get body text, limited to first 1000 characters
            body_text = soup.body.get_text().strip() if soup.body else ''
            body_text = body_text[:1000] + '...' if len(body_text) > 1000 else body_text
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'bodyText': body_text
            }
    
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {
            'success': False,
            'error': f"Failed to scrape {url}: {str(e)}"
        }

def main():
    # Initialize the MCP Server
    server = McpServer(
        name="web-scraper",
        version="1.0.0",
        description="MCP server for web scraping"
    )
    
    # Register the scrape function
    @server.register_function(
        name="scrape",
        description="Scrape content from a website URL",
        parameters={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the website to scrape"
                },
                "selector": {
                    "type": "string",
                    "description": "Optional CSS selector to target specific elements"
                }
            },
            "required": ["url"]
        }
    )
    def handle_scrape_request(params):
        url = params.get("url")
        selector = params.get("selector")
        
        try:
            scraped_data = scrape_website(url, selector)
            return {"success": True, "data": scraped_data}
        except Exception as e:
            logger.error(f"Error in handle_scrape_request: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Start the server
    logger.info("Starting Web Scraper MCP Server")
    server.start()

if __name__ == "__main__":
    main()
