"""
Main entry point for Firebase Functions.
"""
import os
import logging
from quart import Quart
from quart_cors import cors
from dotenv import load_dotenv
from src.routes import main_bp
from src.scheduler import NewsScheduler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Quart app
app = Quart(__name__)
app = cors(app, allow_origin="*")

# Register blueprints
app.register_blueprint(main_bp)

# Initialize scheduler
scheduler = NewsScheduler()

@app.before_serving
async def startup():
    """Initialize services when the app starts."""
    try:
        # Start the scheduler
        scheduler.start()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")

@app.after_serving
async def shutdown():
    """Clean up when the app shuts down."""
    try:
        # Stop the scheduler
        scheduler.stop()
        logger.info("Scheduler stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")

# Firebase Functions entry point
def api(request):
    """Handle HTTP requests."""
    return app.handle_request(request) 