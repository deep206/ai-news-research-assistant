"""
Summarizer module that uses Gemini API to generate content summaries.
"""
import os
from typing import Dict, Optional, List
import google.generativeai as genai
import logging
import asyncio

logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(os.getenv('GEMINI_MODEL'))
        
        # Define the summarization prompt
        self.summary_prompt = """
        # Role
        You are a research assistant who is working for a busy executive.

        # Task
        Please provide a comprehensive summary of the following articles. Focus on the key points and main ideas.
        The summary should be:
        1. Clear and easy to understand
        2. Ensure to include key takeaways from the articles
        3. Capture the main topic and important details
        4. Written in a professional tone
        5. Include emojis to make it easier to read
        6. Include links to the original articles
        7. Group similar topics together
        8. Highlight any conflicting information or different perspectives
        9. End with a conclusion that ties everything together

        # Output Format
        You need to provide an output summary in html format, following this markdown template (note that the template is in markdown format, but the output should be in html format):

        Articles:
        {content}
        """

    async def summarize(self, content: Dict) -> Optional[Dict]:
        """
        Generate a summary of the given content using Gemini API.
        
        Args:
            content: Dictionary containing the article content
            
        Returns:
            Dictionary containing the original content and its summary
        """
        try:
            if not content or not content.get('content'):
                logger.error("No content provided for summarization")
                return None
            
            logger.info(f"Generating summary for article: {content.get('title', 'Untitled')}")
            
            # Prepare the prompt
            prompt = self.summary_prompt.format(content=content['content'])
            
            # Generate the summary
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            if not response.text:
                logger.error("No summary generated")
                return None
            
            # Return the original content with the summary
            return {
                **content,
                "summary": response.text.strip()
            }

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return None

    async def batch_summarize(self, contents: List[Dict]) -> Dict:
        """
        Generate a single comprehensive summary for multiple articles.
        
        Args:
            contents: List of article content dictionaries
            
        Returns:
            Dictionary containing the combined summary and article metadata
        """
        try:
            if not contents:
                logger.warning("No articles provided for summarization")
                return {
                    "summary": "No articles to summarize",
                    "articles": []
                }
            
            logger.info(f"Starting batch summarization for {len(contents)} articles")
            
            # Combine all article content into a single string
            combined_content = "\n\n---\n\n".join([
                f"Title: {article.get('title', 'Untitled')}\n"
                f"Source: {article.get('source', 'Unknown')}\n"
                f"Date: {article.get('date', 'Unknown')}\n"
                f"Content: {article.get('content', '')}\n"
                f"Link: {article.get('link', '')}"
                for article in contents
            ])
            
            # Create a single summary for all articles
            summary_prompt = self.summary_prompt.format(content=combined_content)
            response = await asyncio.to_thread(self.model.generate_content, summary_prompt)
            
            if not response.text:
                logger.error("No summary generated for batch")
                return {
                    "summary": "Failed to generate summary",
                    "articles": contents
                }
            
            logger.info("Successfully generated comprehensive summary")
            
            return {
                "summary": response.text.strip(),
                "articles": contents
            }
            
        except Exception as e:
            logger.error(f"Error in batch summarization: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "summary": f"Error generating summary: {str(e)}",
                "articles": contents
            } 