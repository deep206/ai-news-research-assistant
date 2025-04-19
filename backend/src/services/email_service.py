"""
Email service for sending newsletters and notifications using Brevo.
"""
import os
from brevo_python import BrevoClient
from jinja2 import Environment, FileSystemLoader
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.brevo_client = BrevoClient(api_key=os.getenv('BREVO_API_KEY'))
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@subscribeainews.web.app')
        self.from_name = 'AI News Research Assistant'
        
    async def send_welcome_email(self, email: str, name: str) -> bool:
        """Send welcome email to new subscribers."""
        try:
            template = self.env.get_template('welcome.html')
            content = template.render(name=name)
            
            response = self.brevo_client.send_transactional_email(
                to=[{'email': email, 'name': name}],
                subject='Welcome to AI News Research Assistant!',
                html_content=content,
                sender={'email': self.from_email, 'name': self.from_name}
            )
            
            logger.info(f"Welcome email sent to {email}. Response: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending welcome email to {email}: {str(e)}")
            return False
            
    async def send_newsletter(self, email: str, name: str, articles: List[Dict[str, Any]]) -> bool:
        """Send weekly newsletter with processed articles."""
        try:
            template = self.env.get_template('newsletter.html')
            content = template.render(
                name=name,
                articles=articles,
                date=datetime.utcnow().strftime('%B %d, %Y'),
                unsubscribe_url=f"{os.getenv('FRONTEND_URL')}/unsubscribe?email={email}"
            )
            
            response = self.brevo_client.send_transactional_email(
                to=[{'email': email, 'name': name}],
                subject='Your Weekly AI News Digest',
                html_content=content,
                sender={'email': self.from_email, 'name': self.from_name}
            )
            
            logger.info(f"Newsletter sent to {email}. Response: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending newsletter to {email}: {str(e)}")
            return False
            
    async def send_unsubscribe_confirmation(self, email: str, name: str) -> bool:
        """Send confirmation email when user unsubscribes."""
        try:
            template = self.env.get_template('unsubscribe.html')
            content = template.render(name=name)
            
            response = self.brevo_client.send_transactional_email(
                to=[{'email': email, 'name': name}],
                subject='You have been unsubscribed',
                html_content=content,
                sender={'email': self.from_email, 'name': self.from_name}
            )
            
            logger.info(f"Unsubscribe confirmation sent to {email}. Response: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending unsubscribe confirmation to {email}: {str(e)}")
            return False 