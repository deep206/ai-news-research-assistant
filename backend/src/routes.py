from flask import Blueprint, request, jsonify
from .config.firebase import db
from .utils.encryption import encryption_manager
import os
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        topic = data.get('topic')
        
        if not all([email, name, topic]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate email domain
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com']
        if not any(email.endswith(domain) for domain in allowed_domains):
            return jsonify({'error': 'Invalid email domain'}), 400
        
        # Check if user already exists
        users_ref = db.collection('users')
        query = users_ref.where('encryptedEmail', '==', encryption_manager.encrypt(email)).get()
        
        if query:
            return jsonify({
                'message': 'You are already subscribed',
                'show_unsubscribe': True
            }), 200
        
        # Check user limit
        total_users = len(users_ref.get())
        if total_users >= int(os.getenv('MAX_USERS', 100)):
            return jsonify({
                'error': 'Maximum user limit reached',
                'message': 'Apologies for the inconvenience, this is a research project and we have reached maximum user limit due to cost constraints! Please try again later. Please reach out to me directly if interested in supporting me!'
            }), 403
        
        # Add new user
        user_data = {
            'encryptedEmail': encryption_manager.encrypt(email),
            'encryptedName': encryption_manager.encrypt(name),
            'topic': topic,
            'createdAt': datetime.utcnow(),
            'status': 'active'
        }
        
        users_ref.add(user_data)
        
        return jsonify({
            'message': 'You are successfully subscribed, you will receive weekly emails starting coming Sunday!',
            'show_unsubscribe': True
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    try:
        data = request.get_json()
        email = data.get('email')
        topic = data.get('topic')
        
        if not all([email, topic]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find and delete user
        users_ref = db.collection('users')
        query = users_ref.where('encryptedEmail', '==', encryption_manager.encrypt(email)).get()
        
        if not query:
            return jsonify({'error': 'User not found'}), 404
        
        for doc in query:
            if doc.get('topic') == topic:
                doc.reference.delete()
                return jsonify({'message': 'Successfully unsubscribed'}), 200
        
        return jsonify({'error': 'Subscription not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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