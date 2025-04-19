"""
Firebase utility functions for the AI News Research Assistant.
"""
from firebase_admin import firestore
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def get_active_topics() -> List[Dict[str, str]]:
    """
    Fetch all active topics from Firestore.
    
    Returns:
        List of active topics with their search terms
    """
    try:
        db = firestore.client()
        topics_ref = db.collection('topics')
        
        # Query for active topics
        query = topics_ref.where('isActive', '==', True)
        topics = query.get()
        
        # Format the results
        formatted_topics = []
        for topic in topics:
            topic_data = topic.to_dict()
            formatted_topics.append({
                'value': topic_data['name'],
                'label': topic_data['name'],
                'searchTerms': topic_data['searchTerms']
            })
        
        logger.info(f"Found {len(formatted_topics)} active topics")
        return formatted_topics
        
    except Exception as e:
        logger.error(f"Error fetching topics: {str(e)}")
        return []

async def has_active_users() -> bool:
    """
    Check if there are any active users in the database.
    
    Returns:
        True if there are active users, False otherwise
    """
    try:
        db = firestore.client()
        users_ref = db.collection('users')
        
        # Query for active users
        query = users_ref.where('status', '==', 'active')
        users = await query.get()
        
        has_users = len(users) > 0
        logger.info(f"Active users check: {has_users}")
        return has_users
        
    except Exception as e:
        logger.error(f"Error checking active users: {str(e)}")
        return False 