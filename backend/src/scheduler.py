"""
Scheduler module for periodic news processing.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import logging
from .news_processor.processor import Processor
from firebase_admin import firestore
import asyncio
from .utils.firebase import has_active_users, get_active_topics
from .services.email_service import EmailService
import os

logger = logging.getLogger(__name__)

class NewsScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.processor = Processor()
        self.email_service = EmailService()
        self.db = firestore.client()
        self.job_id = 'news_processing'
        
    def start(self):
        """Start the scheduler and add the news processing job."""
        try:
            # Remove any existing job first
            if self.scheduler.get_job(self.job_id):
                self.scheduler.remove_job(self.job_id)
                logger.info("Removed existing job before scheduling new one")
            
            # For local testing, run immediately and only once
            if os.getenv('NODE_ENV') == 'development' and os.getenv('RUN_CRON_JOB') == 'true':
                # Schedule job to run immediately
                self.scheduler.add_job(
                    self.process_and_store_news,
                    DateTrigger(run_date=datetime.now() + timedelta(seconds=5)),  # Run after 5 seconds
                    id=self.job_id,
                    name='Process and store news articles (One-time)',
                    replace_existing=True,
                    max_instances=1  # Ensure only one instance runs at a time
                )
                logger.info("Development mode: Scheduled one-time news processing job")
            else:
                # Production: Schedule job to run every Sunday at 7 AM ET
                self.scheduler.add_job(
                    self.process_and_store_news,
                    CronTrigger(
                        day_of_week='sun',
                        hour=7,
                        minute=0,
                        timezone='America/New_York'
                    ),
                    id=self.job_id,
                    name='Process and store news articles',
                    replace_existing=True,
                    max_instances=1  # Ensure only one instance runs at a time
                )
                logger.info("Production mode: Scheduled weekly news processing job")
            
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
            if not has_active_users():
                logger.info("No active users found. Skipping news processing.")
                return
            
            # Get all active topics
            active_topics = get_active_topics()
            if not active_topics:
                logger.warning("No active topics found for processing")
                return
            
            # Create a dictionary mapping topic values to their search terms
            topic_search_terms = {}
            for topic in active_topics:
                topic_value = topic.get('value')
                search_terms = topic.get('searchTerms', [])
                if topic_value and search_terms:
                    topic_search_terms[topic_value] = search_terms
            
            if not topic_search_terms:
                logger.warning("No valid topics found for processing")
                return
            
            # Process each topic
            results = await self.processor.process_topics(topic_search_terms)
            
            # Store results in Firestore and prepare for email sending
            topic_articles = {}  # Store articles by topic for email sending
            for topic_value, articles in results.items():
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
                            'topic': topic_value,
                            'processed_at': datetime.utcnow().isoformat(),
                            'status': 'processed'
                        })
                    
                    # Commit the batch
                    batch.commit()
                    logger.info(f"Stored {len(articles)} articles for topic: {topic_value}")
                    
                    # Store articles for email sending
                    topic_articles[topic_value] = articles
            
            # Send emails to users based on their topics
            if topic_articles:
                logger.info("Starting email distribution")
                users_ref = self.db.collection('users')
                query = users_ref.where('status', '==', 'active')
                users = query.get()
                
                for user_doc in users:
                    user_data = user_doc.to_dict()
                    user_topic = user_data.get('topic')
                    if user_topic in topic_articles:
                        try:
                            # Get articles for user's topic
                            user_articles = topic_articles[user_topic]
                            
                            # Send email to user
                            email_sent = await self.email_service.send_summary(
                                user_articles[0].get('summary', ''),  # Using first article's summary
                                user_articles,
                                user_data['email'],
                                user_data['name']
                            )
                            
                            if email_sent:
                                logger.info(f"Successfully sent email to {user_data['email']} for topic {user_topic}")
                            else:
                                logger.error(f"Failed to send email to {user_data['email']} for topic {user_topic}")
                                
                        except Exception as e:
                            logger.error(f"Error sending email to {user_data['email']}: {str(e)}")
                            continue
                
                logger.info("Email distribution completed")
            
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