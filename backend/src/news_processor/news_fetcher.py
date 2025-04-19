"""
News fetcher module that uses SerpApi to search for news articles.
"""
import os
from typing import List, Dict
import aiohttp
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        self.api_key = os.getenv('SERPAPI_KEY')
        if not self.api_key:
            raise ValueError("SERPAPI_KEY environment variable is not set")
        
        self.base_url = "https://serpapi.com/search"
        self.search_params = {
            "engine": "google",
            "api_key": self.api_key,
            "tbm": "nws",  # news search
            "num": 10,     # number of results
            "gl": "us",    # country
            "hl": "en"     # language
        }

    async def search_news(self, query: str, time_period: str = "week") -> List[Dict]:
        """
        Search for news articles related to the given query.
        
        Args:
            query: Search query string
            time_period: Time period for news (day, week, month)
            
        Returns:
            List of news articles with their details
        """
        try:
            # Calculate date range based on time_period
            end_date = datetime.now()
            if time_period == "day":
                start_date = end_date - timedelta(days=1)
            elif time_period == "week":
                start_date = end_date - timedelta(days=7)
            elif time_period == "month":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=7)  # default to week

            # Add date range to search parameters
            params = self.search_params.copy()
            params.update({
                "q": query,
                "tbs": f"cdr:1,cd_min:{start_date.strftime('%m/%d/%Y')},cd_max:{end_date.strftime('%m/%d/%Y')}"
            })

            logger.info(f"Searching news for query: {query}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    news_results = data.get("news_results", [])
                    
                    # Process and format the results
                    formatted_results = []
                    for article in news_results:
                        formatted_article = {
                            "title": article.get("title", ""),
                            "link": article.get("link", ""),
                            "source": article.get("source", ""),
                            "date": article.get("date", ""),
                            "snippet": article.get("snippet", ""),
                            "thumbnail": article.get("thumbnail", "")
                        }
                        formatted_results.append(formatted_article)
                    
                    logger.info(f"Found {len(formatted_results)} news articles")
                    return formatted_results

        except aiohttp.ClientError as e:
            logger.error(f"Error fetching news: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in news search: {str(e)}")
            raise 