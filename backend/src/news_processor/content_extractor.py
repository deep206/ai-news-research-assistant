"""
Content extractor module that uses Scrapy to extract article content.
"""
import os
from typing import Dict, Optional
import aiohttp
import logging
from urllib.parse import urlparse
import re
from scrapy import Selector

logger = logging.getLogger(__name__)

class ContentExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def extract_content(self, url: str) -> Optional[Dict]:
        """
        Extract the main content from a news article URL.
        
        Args:
            url: URL of the news article
            
        Returns:
            Dictionary containing the extracted content or None if extraction fails
        """
        try:
            logger.info(f"Extracting content from URL: {url}")
            
            # Validate URL
            if not self._is_valid_url(url):
                logger.error(f"Invalid URL: {url}")
                return None

            # Fetch the webpage
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=10) as response:
                    response.raise_for_status()
                    html = await response.text()
            
            # Parse the HTML using Scrapy Selector
            selector = Selector(text=html)
            
            # Extract title
            title = self._extract_title(selector)
            
            # Extract main content
            content = self._extract_main_content(selector)
            
            # Clean and format the content
            cleaned_content = self._clean_content(content)
            
            if not cleaned_content:
                logger.warning(f"No content extracted from URL: {url}")
                return None
            
            return {
                "title": title,
                "content": cleaned_content,
                "url": url
            }

        except aiohttp.ClientError as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error extracting content from {url}: {str(e)}")
            return None

    def _is_valid_url(self, url: str) -> bool:
        """Validate the URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _extract_title(self, selector: Selector) -> str:
        """Extract the article title."""
        # Try different title selectors
        title_selectors = [
            'h1::text',
            'title::text',
            'meta[property="og:title"]::attr(content)',
            'meta[name="twitter:title"]::attr(content)'
        ]
        
        for selector_expr in title_selectors:
            title = selector.css(selector_expr).get()
            if title:
                return title.strip()
        
        return ""

    def _extract_main_content(self, selector: Selector) -> str:
        """Extract the main content of the article."""
        # Common content selectors
        content_selectors = [
            'article',
            'main',
            '.article-content',
            '.post-content',
            '.entry-content',
            '#content'
        ]
        
        for selector_expr in content_selectors:
            content = selector.css(selector_expr)
            if content:
                # Extract text from all paragraphs within the content
                paragraphs = content.css('p::text').getall()
                if paragraphs:
                    return ' '.join(paragraphs)
        
        # Fallback: try to find all paragraphs
        paragraphs = selector.css('p::text').getall()
        if paragraphs:
            return ' '.join(paragraphs)
        
        return ""

    def _clean_content(self, content: str) -> str:
        """Clean and format the extracted content."""
        if not content:
            return ""
            
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common unwanted elements
        content = re.sub(r'Advertisement|Sponsored|Related.*', '', content, flags=re.IGNORECASE)
        
        # Remove URLs
        content = re.sub(r'http[s]?://\S+', '', content)
        
        return content.strip() 