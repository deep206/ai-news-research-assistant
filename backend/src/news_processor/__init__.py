"""
News processing module for AI News Research Assistant.
Handles news aggregation, content extraction, and summarization.
"""

from .news_fetcher import NewsFetcher
from .content_extractor import ContentExtractor
from .summarizer import Summarizer

__all__ = ['NewsFetcher', 'ContentExtractor', 'Summarizer'] 