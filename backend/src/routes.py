from quart import Blueprint, request, jsonify
from .config.firebase import db
import os
from datetime import datetime, timedelta
from google.cloud import firestore
import traceback
from .utils.firebase import get_active_topics, has_active_users
import logging
from typing import List, Dict, Any
from firebase_admin import firestore
from .news_processor.news_fetcher import NewsFetcher
from .news_processor.content_extractor import ContentExtractor
from .news_processor.processor import Processor
from .news_processor.summarizer import Summarizer

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/topics', methods=['GET'])
def get_topics():
    """Get all active topics from the database."""
    try:
        logger.info("Fetching active topics")
        topics = get_active_topics()
        logger.info(f"Found {len(topics)} active topics")
        
        return jsonify({
            'topics': topics
        }), 200
    except Exception as e:
        logger.error(f"Error fetching topics: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Failed to fetch topics',
            'message': str(e)
        }), 500

@main_bp.route('/subscribe', methods=['POST'])
async def subscribe():
    try:
        data = await request.get_json()
        if not data:
            return {'error': 'Invalid request', 'message': 'No JSON data provided'}, 400
            
        email = data.get('email', '').strip().lower()  # Normalize email
        name = data.get('name', '').strip()
        topic = data.get('topic', '').strip()
        
        print(f"\n=== New Subscription Request ===")
        print(f"Email: {email}")
        print(f"Name: {name}")
        print(f"Topics: {topic}")
        print(f"Raw data: {data}")
        
        if not all([email, name, topic]):
            return {'error': 'Please fill in all required fields'}, 400
        
        # Validate email domain
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com']
        if not any(email.endswith(domain) for domain in allowed_domains):
            return {'error': 'Please use a Gmail, Yahoo, or Outlook email address'}, 400
        
        # Check if user already exists
        users_ref = db.collection('users')
        try:
            # Get all users first to verify the collection
            all_users = users_ref.get()
            print(f"\n=== Current Database State ===")
            print(f"Total users in database: {len(all_users)}")
            print("Existing users:")
            
            # Check for duplicate email
            duplicate_found = False
            for user in all_users:
                user_data = user.to_dict()
                print(f"- Email: {user_data['email']}")
                if user_data['email'] == email:
                    print(f"  MATCH FOUND! This email already exists in the database.")
                    duplicate_found = True
                    break
                print(f"  Name: {user_data['name']}")
                print(f"  Topic: {user_data['topic']}")
            
            if duplicate_found:
                print(f"\n=== Duplicate Found ===")
                print(f"Found existing user with email: {email}")
                return {
                    'error': 'You are already subscribed',
                    'message': 'This email address is already registered. If you want to change your subscription, please unsubscribe first.',
                    'show_unsubscribe': True
                }, 409
            
            # Check user limit
            total_users = len(all_users)
            print(f"\n=== User Limit Check ===")
            print(f"Current total users: {total_users}, Max allowed: {int(os.getenv('MAX_USERS', 5))}")
            if total_users >= int(os.getenv('MAX_USERS', 5)):
                return {
                    'error': 'Maximum user limit reached',
                    'message': 'Apologies for the inconvenience, this is a research project and we have reached maximum user limit due to cost constraints! Please try again later. Please reach out to me directly if interested in supporting me!'
                }, 403
            
            # Add new user
            user_data = {
                'email': email,
                'name': name,
                'topics': topic,
                'createdAt': datetime.utcnow(),
                'status': 'active'
            }
            
            print(f"\n=== Adding New User ===")
            print(f"User data to be added: {user_data}")
            users_ref.add(user_data)
            print(f"Successfully added new user")
            
            return {
                'message': 'You are successfully subscribed! You will receive weekly emails starting this Sunday.',
                'show_unsubscribe': True
            }, 201
            
        except Exception as db_error:
            print(f"\n=== Database Error ===")
            print(f"Error type: {type(db_error)}")
            print(f"Error message: {str(db_error)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                'error': 'Database operation failed',
                'message': 'An error occurred while accessing the database. Please try again later.',
                'details': str(db_error)
            }, 500
    
    except Exception as e:
        print(f"\n=== Error Occurred ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'error': 'Subscription failed',
            'message': 'An unexpected error occurred. Please try again later.',
            'details': str(e)
        }, 500

@main_bp.route('/unsubscribe', methods=['POST'])
async def unsubscribe():
    try:
        data = await request.get_json()
        if not data:
            return {'error': 'Invalid request', 'message': 'No JSON data provided'}, 400
            
        email = data.get('email', '').strip().lower()  # Normalize email
        
        print(f"\n=== Unsubscribe Request ===")
        print(f"Email: {email}")
        print(f"Raw data: {data}")
        
        if not email:
            return {'error': 'Email is required'}, 400
        
        # Find and delete user
        users_ref = db.collection('users')
        try:
            # Use the recommended filter syntax
            query = users_ref.where(filter=firestore.FieldFilter('email', '==', email))
            query_result = query.get()
            print(f"Query result length: {len(query_result)}")
            
            if len(query_result) == 0:
                print(f"\n=== No User Found ===")
                print(f"No user found with email: {email}")
                return {
                    'error': 'User not found',
                    'message': 'No subscription found for this email address.'
                }, 404
            
            # Delete the subscription
            for doc in query_result:
                print(f"\n=== Deleting Subscription ===")
                print(f"Deleting subscription for email: {email}")
                doc.reference.delete()
            
            print(f"\n=== Success ===")
            print(f"Successfully unsubscribed user: {email}")
            return {
                'message': 'Successfully unsubscribed from the newsletter.'
            }, 200
                
        except Exception as db_error:
            print(f"\n=== Database Error ===")
            print(f"Error type: {type(db_error)}")
            print(f"Error message: {str(db_error)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                'error': 'Database operation failed',
                'message': 'An error occurred while accessing the database. Please try again later.',
                'details': str(db_error)
            }, 500
    
    except Exception as e:
        print(f"\n=== Error Occurred ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'error': 'Unsubscribe failed',
            'message': 'An unexpected error occurred. Please try again later.',
            'details': str(e)
        }, 500

@main_bp.route('/test', methods=['POST'])
async def test_email():
    """Test endpoint for admin functionality including news fetching, content extraction, and summarization."""
    try:
        data = await request.get_json()
        password = data.get('password')
        
        if not password:
            logger.warning("Test request received without password")
            return jsonify({'error': 'Password is required'}), 400
        
        # Validate admin password
        if password != os.getenv('ADMIN_PWD'):
            logger.warning("Invalid admin password provided")
            return jsonify({'error': 'Invalid password'}), 401
        
        logger.info("Admin authentication successful, proceeding with test operations")
        
        # Initialize components
        news_fetcher = NewsFetcher()
        content_extractor = ContentExtractor()
        summarizer = Summarizer()
        
        # Step 1: Fetch news articles
        logger.info("Starting news fetch for 'Artificial Intelligence News'")
        articles = await news_fetcher.search_news("Artificial Intelligence News", "week")
        
        if not articles:
            logger.warning("No articles found in the search")
            return jsonify({
                'status': 'success',
                'message': 'No articles found',
                'articles': []
            }), 200
        
        logger.info(f"Successfully fetched {len(articles)} articles")
        
        # Step 2: Extract content from articles
        logger.info("Starting content extraction for fetched articles")
        processed_articles = []
        
        for i, article in enumerate(articles, 1):
            try:
                logger.info(f"Extracting content for article {i}/{len(articles)}: {article['title']}")
                content = await content_extractor.extract_content(article['link'])
                
                if content:
                    processed_article = {
                        **article,
                        **content
                    }
                    processed_articles.append(processed_article)
                    logger.info(f"Successfully extracted content for article {i}")
                else:
                    logger.warning(f"Failed to extract content for article {i}")
                    
            except Exception as e:
                logger.error(f"Error processing article {i}: {str(e)}")
                logger.debug(f"Article details: {article}")
                continue
        
        logger.info(f"Content extraction completed. Successfully processed {len(processed_articles)} articles")
        
        # Step 3: Generate summaries
        logger.info("Starting content summarization")
        summarized_articles = await summarizer.batch_summarize(processed_articles)
        
        logger.info(f"Summarization completed. Successfully summarized {len(summarized_articles)} articles")
        
        return jsonify({
            'status': 'success',
            'message': f'Processed and summarized {len(summarized_articles)} articles',
            'articles': summarized_articles
        }), 200
    
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@main_bp.route('/articles', methods=['GET'])
async def get_articles():
    """Get all processed articles with optional filtering."""
    try:
        # Get query parameters
        topic = request.args.get('topic')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 10))
        
        # Initialize Firestore
        db = firestore.client()
        articles_ref = db.collection('processed_articles')
        
        # Build query
        query = articles_ref
        
        if topic:
            query = query.where('topic', '==', topic)
            
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.where('processed_at', '>=', start_dt.isoformat())
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format (YYYY-MM-DD)'}), 400
                
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.where('processed_at', '<=', end_dt.isoformat())
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format (YYYY-MM-DD)'}), 400
        
        # Execute query
        articles = await query.order_by('processed_at', direction=firestore.Query.DESCENDING).limit(limit).get()
        
        # Format results
        results = []
        for article in articles:
            article_data = article.to_dict()
            article_data['id'] = article.id
            results.append(article_data)
            
        return jsonify({
            'count': len(results),
            'articles': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching articles: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/articles/recent', methods=['GET'])
async def get_recent_articles():
    """Get recent articles (last 7 days) with optional topic filter."""
    try:
        topic = request.args.get('topic')
        limit = int(request.args.get('limit', 10))
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Initialize Firestore
        db = firestore.client()
        articles_ref = db.collection('processed_articles')
        
        # Build query
        query = articles_ref.where('processed_at', '>=', start_date.isoformat())
        
        if topic:
            query = query.where('topic', '==', topic)
            
        # Execute query
        articles = await query.order_by('processed_at', direction=firestore.Query.DESCENDING).limit(limit).get()
        
        # Format results
        results = []
        for article in articles:
            article_data = article.to_dict()
            article_data['id'] = article.id
            results.append(article_data)
            
        return jsonify({
            'count': len(results),
            'articles': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching recent articles: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/test/news', methods=['GET'])
async def test_news_fetcher():
    """Test endpoint for news fetcher functionality."""
    try:
        # Get query parameters
        query = request.args.get('query', 'AI technology')
        time_period = request.args.get('time_period', 'week')
        
        # Initialize news fetcher
        news_fetcher = NewsFetcher()
        
        # Fetch news articles
        articles = await news_fetcher.search_news(query, time_period)
        
        if not articles:
            return jsonify({
                'status': 'success',
                'message': 'No articles found',
                'articles': []
            }), 200
        
        # Initialize content extractor
        content_extractor = ContentExtractor()
        
        # Extract content for the first article
        first_article = articles[0]
        content = await content_extractor.extract_content(first_article['link'])
        
        if content:
            first_article.update(content)
        
        return jsonify({
            'status': 'success',
            'message': f'Found {len(articles)} articles',
            'articles': articles,
            'sample_content': first_article if content else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error in news fetcher test: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 