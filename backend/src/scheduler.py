"""
Scheduler module for periodic news processing.
"""
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from .news_processor.news_fetcher import NewsFetcher
from .news_processor.content_extractor import ContentExtractor
from .news_processor.summarizer import Summarizer
from .services.email_service import EmailService
from firebase_admin import firestore

logger = logging.getLogger(__name__)

class NewsScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.news_fetcher = NewsFetcher()
        self.content_extractor = ContentExtractor()
        self.summarizer = Summarizer()
        self.email_service = EmailService()
        self.db = firestore.client()

    async def process_and_store_news(self):
        """Process news articles and send emails to users."""
        try:
            logger.info("Starting weekly news processing job")
            
            # Step 1: Get all active users
            users_ref = self.db.collection('users')
            users = users_ref.where('status', '==', 'active').get()
            
            if not users:
                logger.info("No active users found, skipping processing")
                return
                
            logger.info(f"Found {len(users)} active users")
            
            # Step 2: Get all active topics
            topics_ref = self.db.collection('topics')
            topics = topics_ref.where('isActive', '==', True).get()
            
            if not topics:
                logger.warning("No active topics found")
                return
                
            logger.info(f"Found {len(topics)} active topics")
            
            # Step 3: Process each topic
            topic_summaries = {}  # Store summaries by topic
            
            for topic in topics:
                topic_data = topic.to_dict()
                topic_value = topic_data['name']
                search_terms = topic_data['searchTerms']
                
                try:
                    logger.info(f"Processing topic: {topic_value}")
                    
                    # Fetch news articles
                    articles = await self.news_fetcher.search_news(search_terms, "week")
                    if not articles:
                        logger.warning(f"No articles found for topic: {topic_value}")
                        continue
                        
                    logger.info(f"Found {len(articles)} articles for topic: {topic_value}")
                    
                    # Extract content from articles
                    processed_articles = []
                    for article in articles:
                        try:
                            content = await self.content_extractor.extract_content(article['link'])
                            if content:
                                processed_article = {
                                    **article,
                                    **content
                                }
                                processed_articles.append(processed_article)
                        except Exception as e:
                            logger.error(f"Error extracting content for article: {str(e)}")
                            continue
                    
                    if not processed_articles:
                        logger.warning(f"No content extracted for topic: {topic_value}")
                        continue
                        
                    # Generate summary
                    summary_result = await self.summarizer.batch_summarize(processed_articles)
                    if not summary_result.get('summary'):
                        logger.warning(f"No summary generated for topic: {topic_value}")
                        continue
                        
                    topic_summaries[topic_value] = {
                        'summary': summary_result['summary'],
                        'articles': processed_articles
                    }
                    
                    logger.info(f"Successfully processed topic: {topic_value}")
                    
                except Exception as e:
                    logger.error(f"Error processing topic {topic_value}: {str(e)}")
                    continue
            
            # Step 4: Send emails to users for each topic
            if topic_summaries:
                logger.info("Starting email distribution")
                
                # Get all users and their topics
                users_data = []
                for user_doc in users:
                    user_data = user_doc.to_dict()
                    users_data.append(user_data)
                
                # Send emails for each topic that has a summary
                for topic, topic_data in topic_summaries.items():
                    logger.info(f"Sending emails for topic: {topic}")
                    
                    # Find all users subscribed to this topic
                    topic_users = [user for user in users_data if user.get('topic') == topic]
                    
                    if not topic_users:
                        logger.warning(f"No users found for topic: {topic}")
                        continue
                        
                    logger.info(f"Found {len(topic_users)} users for topic: {topic}")
                    
                    # Send email to each user
                    for user_data in topic_users:
                        try:
                            email_sent = await self.email_service.send_summary(
                                topic_data['summary'],
                                topic_data['articles'],
                                user_data['email'],
                                topic
                            )
                            
                            if email_sent:
                                logger.info(f"Successfully sent email to {user_data['email']} for topic {topic}")
                            else:
                                logger.error(f"Failed to send email to {user_data['email']} for topic {topic}")
                                
                        except Exception as e:
                            logger.error(f"Error sending email to {user_data['email']}: {str(e)}")
                            continue
                
                logger.info("Email distribution completed")
            
            logger.info("Weekly news processing job completed successfully")
            
        except Exception as e:
            logger.error(f"Error in news processing job: {str(e)}")
            raise

    def start(self):
        """Start the scheduler."""
        # Schedule job to run every Sunday at 7 AM ET
        self.scheduler.add_job(
            self.process_and_store_news,
            CronTrigger(
                day_of_week=os.getenv('SCHEDULER_DAY'),
                hour=os.getenv('SCHEDULER_HOUR'),
                minute=os.getenv('SCHEDULER_MINUTE'),
                timezone=os.getenv('SCHEDULER_TIMEZONE')
            ),
            id='weekly_news_processing',
            name='Process and send weekly news',
            replace_existing=True
        )
        
        self.scheduler.start()
        
        logger.info("News scheduler started")

    def stop(self):
        """Stop the scheduler."""
        try:
            self.scheduler.shutdown()
            logger.info("News scheduler stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
            raise 