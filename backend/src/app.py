import os
from pathlib import Path
from dotenv import load_dotenv
from quart import Quart
from quart_cors import cors  # Using Quart-CORS instead of Flask-CORS

# Load environment variables from the backend directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def create_app():
    app = Quart(__name__)
    
    # Configure CORS using Quart-CORS
    app = cors(app, allow_origin="*")
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['MAX_USERS'] = int(os.getenv('MAX_USERS', 100))
    
    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    @app.route('/health', methods=['GET'])
    async def health_check():
        return {'status': 'healthy'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 