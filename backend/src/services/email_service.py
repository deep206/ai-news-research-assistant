"""
Email service for sending newsletters and notifications using Brevo API.
"""
import os
import logging
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv
import asyncio
import traceback

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('BREVO_API_KEY')
        self.frontend_url = os.getenv('FRONTEND_URL')
        self.backend_url = os.getenv('BACKEND_URL')
        if not self.api_key:
            raise ValueError("BREVO_API_KEY environment variable is not set")
        
        self.base_url = "https://api.brevo.com/v3"
        self.headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }

    def _create_html_content(self, summary: str, articles: List[Dict], send_to_email: str) -> str:
        """
        Create HTML content for the email.
        
        Args:
            summary: The main summary content
            articles: List of articles with their metadata
            
        Returns:
            Formatted HTML string
        """
        # Trim markdown code block markers if present
        summary = summary.strip()
        if summary.startswith('```html'):
            summary = summary[7:]
        if summary.endswith('```'):
            summary = summary[:-3]
        summary = summary.strip()
        
        # Start with the summary
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .summary {{ margin-bottom: 20px; }}
                .articles {{ margin-top: 20px; }}
                .article {{ margin-bottom: 15px; padding: 10px; border-left: 3px solid #007bff; }}
                .title {{ font-weight: bold; color: #007bff; }}
                .source {{ color: #666; font-size: 0.9em; }}
                .link {{ color: #007bff; text-decoration: none; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; font-size: 0.8em; color: #666; }}
            </style>
        </head>
        <body>
            <div>
                <h1>Hey there! 🙋</h1>
            </div>
            <div class="summary">
                {summary}
            </div>
            <div class="articles">
                <h2>Source Articles</h2>
        """
        
        # Add each article
        for article in articles:
            html_content += f"""
                <div class="article">
                    <div class="title">{article.get('title', 'Untitled')}</div>
                    <div class="source">{article.get('source', 'Unknown')} - {article.get('date', 'Unknown')}</div>
                    <a href="{article.get('link', '#')}" class="link">Read original article</a>
                </div>
            """
        
        # Add footer
        html_content += f"""
            </div>
            <div class="footer">
                <p>This is an automated AI generated newsletter from <a href="{self.frontend_url}">Subscribe to AI Newsletter by Deep Patel</a>.</p>
                <p>To unsubscribe, please visit our website or <a href="{self.backend_url}/unsubscribe-email?email={send_to_email}">click here</a>.</p>
            </div>
        </body>
        </html>
        """
        
        return html_content

    async def send_summary(self, summary: str, articles: List[Dict], send_to_email: str, topic: str) -> bool:
        """
        Send a summary email to the configured test email address.
        
        Args:
            summary: The main summary content
            articles: List of articles with their metadata
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Create HTML content
            html_content = self._create_html_content(summary, articles, send_to_email)
            
            # Prepare email data
            email_data = {
                "sender": {
                    "name": "Subscribe to AI Newsletter by Deep Patel",
                    "email": os.getenv('FROM_EMAIL')
                },
                "to": [{"email": send_to_email}],
                "subject": f"Weekly News Summary for {topic}",
                "htmlContent": html_content
            }
            
            # Send email using Brevo API
            url = f"{self.base_url}/smtp/email"
            response = await asyncio.to_thread(
                requests.post,
                url,
                headers=self.headers,
                json=email_data
            )
            
            if response.status_code == 201:
                logger.info(f"Email sent successfully to {send_to_email}")
                return True
            else:
                logger.error(f"Failed to send email. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False 