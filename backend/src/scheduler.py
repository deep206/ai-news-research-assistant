"""
Scheduler module for periodic news processing.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from .news_processor.processor import Processor
from firebase_admin import firestore
import asyncio
from .utils.firebase import has_active_users, get_active_topics

logger = logging.getLogger(__name__)

class NewsScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.processor = Processor()
        self.db = firestore.client()
        
    def start(self):
        """Start the scheduler and add the news processing job."""
        try:
            # Schedule job to run every Sunday at 7 AM ET
            self.scheduler.add_job(
                self.process_and_store_news,
                CronTrigger(
                    day_of_week='sun',
                    hour=7,
                    minute=0,
                    timezone='America/New_York'
                ),
                id='news_processing',
                name='Process and store news articles',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info("News scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise

    async def process_and_store_news(self):
        """Process news articles and store them in Firestore."""
        try:
            logger.info("Starting news processing job")
            
            # Check if there are any active users
            if not await has_active_users():
                logger.info("No active users found. Skipping news processing.")
                return
            
            # Get all active topics
            active_topics = await get_active_topics()
            if not active_topics:
                logger.warning("No active topics found for processing")
                return
            
            # Process each topic
            results = await self.processor.process_topics(active_topics)
            
            # Store results in Firestore
            for topic, articles in results.items():
                if articles:
                    # Create a batch for this topic's articles
                    batch = self.db.batch()
                    collection_ref = self.db.collection('processed_articles')
                    
                    # Add each article to the batch
                    for article in articles:
                        # Create a document reference with a unique ID
                        doc_ref = collection_ref.document()
                        batch.set(doc_ref, {
                            **article,
                            'topic': topic,
                            'processed_at': datetime.utcnow().isoformat(),
                            'status': 'processed'
                        })
                    
                    # Commit the batch
                    await batch.commit()
                    logger.info(f"Stored {len(articles)} articles for topic: {topic}")
            
            logger.info("News processing job completed successfully")
            
        except Exception as e:
            logger.error(f"Error in news processing job: {str(e)}")
            raise

    def stop(self):
        """Stop the scheduler."""
        try:
            self.scheduler.shutdown()
            logger.info("News scheduler stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
            raise 