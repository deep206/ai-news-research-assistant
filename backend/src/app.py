"""
Main application module for the AI News Research Assistant.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from quart import Quart
from quart_cors import cors
from .routes import main_bp
from .scheduler import NewsScheduler
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Quart application."""
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # Create the Quart app
    app = Quart(__name__)
    
    # Configure CORS
    cors(app, allow_origin="*")
    
    # Register blueprints
    app.register_blueprint(main_bp)
    
    # Initialize scheduler
    scheduler = NewsScheduler()
    
    @app.before_serving
    async def startup():
        """Start the scheduler when the application starts."""
        try:
            scheduler.start()
            logger.info("Application started successfully")
        except Exception as e:
            logger.error(f"Failed to start application: {str(e)}")
            raise
    
    @app.after_serving
    async def shutdown():
        """Stop the scheduler when the application shuts down."""
        try:
            scheduler.stop()
            logger.info("Application stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping application: {str(e)}")
            raise
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 