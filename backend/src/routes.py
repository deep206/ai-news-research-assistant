from quart import Blueprint, request
from .config.firebase import db
import os
from datetime import datetime
from google.cloud import firestore
import traceback

main_bp = Blueprint('main', __name__)

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
        print(f"Topic: {topic}")
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
                'topic': topic,
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
        topic = data.get('topic', '').strip()
        
        print(f"\n=== Unsubscribe Request ===")
        print(f"Email: {email}")
        print(f"Topic: {topic}")
        print(f"Raw data: {data}")
        
        if not all([email, topic]):
            return {'error': 'Please provide both email and topic'}, 400
        
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
            
            # Delete all matching subscriptions
            deleted = False
            for doc in query_result:
                if doc.get('topic') == topic:
                    print(f"\n=== Deleting Subscription ===")
                    print(f"Deleting subscription for email: {email}, topic: {topic}")
                    doc.reference.delete()
                    deleted = True
            
            if deleted:
                print(f"\n=== Success ===")
                print(f"Successfully unsubscribed user: {email}")
                return {
                    'message': 'Successfully unsubscribed from the newsletter.'
                }, 200
            else:
                print(f"\n=== No Match Found ===")
                print(f"No matching subscription found for email: {email}, topic: {topic}")
                return {
                    'error': 'Subscription not found',
                    'message': 'No subscription found for this email and topic combination.'
                }, 404
                
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
def test_email():
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Validate admin password
        if encryption_manager.decrypt(password) != os.getenv('ADMIN_PWD'):
            return jsonify({'error': 'Invalid password'}), 401
        
        # TODO: Implement test email functionality
        return jsonify({'message': 'Test email will be sent'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 