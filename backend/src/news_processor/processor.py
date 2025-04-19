"""
Main processor module that orchestrates the news processing pipeline.
"""
from typing import List, Dict, Any
from .news_fetcher import NewsFetcher
from .content_extractor import ContentExtractor
from .summarizer import Summarizer
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class Processor:
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.content_extractor = ContentExtractor()
        self.summarizer = Summarizer()

    async def process_topic(self, topic: str, time_period: str = "week") -> List[Dict]:
        """
        Process a topic by fetching news, extracting content, and generating summaries.
        
        Args:
            topic: Topic to search for
            time_period: Time period for news (day, week, month)
            
        Returns:
            List of processed articles with summaries
        """
        try:
            logger.info(f"Processing topic: {topic}")
            
            # Step 1: Fetch news articles
            news_articles = await self.news_fetcher.search_news(topic, time_period)
            if not news_articles:
                logger.warning(f"No news articles found for topic: {topic}")
                return []
            
            # Step 2: Extract content from each article concurrently
            content_tasks = [
                await self.content_extractor.extract_content(article['link'])
                for article in news_articles
            ]
            content_results = await asyncio.gather(*content_tasks, return_exceptions=True)
            
            # Combine articles with their content
            articles_with_content = []
            for article, content in zip(news_articles, content_results):
                if isinstance(content, Exception):
                    logger.error(f"Error extracting content for {article['link']}: {str(content)}")
                    continue
                if content:
                    articles_with_content.append({
                        **article,
                        **content
                    })
            
            if not articles_with_content:
                logger.warning(f"No content extracted for topic: {topic}")
                return []
            
            # Step 3: Generate summaries
            summarized_articles = await self.summarizer.batch_summarize(articles_with_content)
            
            # Add processing metadata
            for article in summarized_articles:
                article['processed_at'] = datetime.utcnow().isoformat()
                article['topic'] = topic
            
            logger.info(f"Successfully processed {len(summarized_articles)} articles for topic: {topic}")
            return summarized_articles

        except Exception as e:
            logger.error(f"Error processing topic {topic}: {str(e)}")
            raise

    async def process_topics(self, topics: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Process multiple topics and return their articles.
        
        Args:
            topics: Dictionary mapping topic values to their search terms
            
        Returns:
            Dictionary mapping topic values to lists of processed articles
        """
        results = {}
        
        for topic_value, search_terms in topics.items():
            try:
                logger.info(f"Processing topic: {topic_value}")
                
                # Fetch news articles for the topic
                articles = await self.news_fetcher.search_news(search_terms)
                if not articles:
                    logger.warning(f"No articles found for topic: {topic_value}")
                    results[topic_value] = []
                    continue
                
                # Process and summarize articles
                processed_articles = []
                for article in articles:
                    try:
                        # Validate article data
                        if not article or not isinstance(article, dict):
                            logger.warning("Invalid article data received")
                            continue
                            
                        url = article.get('url')
                        if not url:
                            logger.warning("Article missing URL")
                            continue
                            
                        # Extract article content
                        content = await self.content_extractor.extract_content(url)
                        if not content:
                            logger.warning(f"Failed to extract content from URL: {url}")
                            continue
                        
                        # Generate summary
                        summary = await self.summarizer.summarize(content)
                        
                        # Combine article data with content and summary
                        processed_article = {
                            **article,
                            'content': content,
                            'summary': summary
                        }
                        processed_articles.append(processed_article)
                        
                    except Exception as e:
                        logger.error(f"Error processing article: {str(e)}")
                        continue
                
                # Use the topic value (string) as the key
                results[topic_value] = processed_articles
                logger.info(f"Successfully processed {len(processed_articles)} articles for topic: {topic_value}")
                
            except Exception as e:
                logger.error(f"Error processing topic {topic_value}: {str(e)}")
                results[topic_value] = []
                continue
        
        return results 