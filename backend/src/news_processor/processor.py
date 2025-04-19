"""
Main processor module that orchestrates the news processing pipeline.
"""
from typing import List, Dict
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
                self.content_extractor.extract_content(article['link'])
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
            summarized_articles = self.summarizer.batch_summarize(articles_with_content)
            
            # Add processing metadata
            for article in summarized_articles:
                article['processed_at'] = datetime.utcnow().isoformat()
                article['topic'] = topic
            
            logger.info(f"Successfully processed {len(summarized_articles)} articles for topic: {topic}")
            return summarized_articles

        except Exception as e:
            logger.error(f"Error processing topic {topic}: {str(e)}")
            raise

    async def process_topics(self, topics: List[str], time_period: str = "week") -> Dict[str, List[Dict]]:
        """
        Process multiple topics and return results organized by topic.
        
        Args:
            topics: List of topics to process
            time_period: Time period for news (day, week, month)
            
        Returns:
            Dictionary mapping topics to their processed articles
        """
        results = {}
        
        # Process topics concurrently
        topic_tasks = [
            self.process_topic(topic, time_period)
            for topic in topics
        ]
        topic_results = await asyncio.gather(*topic_tasks, return_exceptions=True)
        
        # Combine results
        for topic, result in zip(topics, topic_results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process topic {topic}: {str(result)}")
                results[topic] = []
            else:
                results[topic] = result
        
        return results 