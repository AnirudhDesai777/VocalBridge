# app/services/llm_service.py

from groq import Groq
import os
from typing import Optional
from app.utils.logger import CustomLogger

class LLMService:
    def __init__(self):
        self.logger = CustomLogger("llm_service").get_logger()
        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            self.logger.error("GROQ_API_KEY not found in environment variables")
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.logger.info("Initializing LLM Service with Groq API")
        self.client = Groq(api_key=api_key)
        self.model = "llama3-70b-8192"
        
        self.system_message = """You are a helpful AI assistant specializing in 
        natural language enhancement for people with speech impairments. Your task 
        is to take user input and rephrase it into clear, well-structured sentences
        while maintaining the original meaning and intent. Important: Return ONLY 
        the enhanced text without any explanations, prefixes, or formatting.
        
        Focus on:
        1. Clarity and naturalness of expression
        2. Proper grammar and sentence structure
        3. Maintaining the user's intended tone and meaning
        4. Using appropriate conversational language
        
        Remember: Provide ONLY the enhanced text as your response."""

    def enhance_text(self, text: str) -> str:
        """Enhance the input text using LLaMA through Groq API."""
        try:
            self.logger.info(f"Enhancing text: {text}")
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": f'Enhance: "{text}"'}
                ],
                temperature=0.7,
                max_tokens=256,
                top_p=0.9,
                stream=False
            )
            
            enhanced_text = self._clean_response(completion.choices[0].message.content)
            self.logger.info(f"Enhanced text result: {enhanced_text}")
            return enhanced_text
            
        except Exception as e:
            self.logger.error(f"Error enhancing text: {str(e)}")
            return text

    def _clean_response(self, text: str) -> str:
        """Clean up the model's response."""
        self.logger.debug(f"Cleaning response text: {text}")
        
        # Remove any markdown formatting
        text = text.replace('```', '').strip()
        # Remove quotes
        text = text.strip('"')
        # Remove common prefixes
        prefixes = [
            "Enhanced text:", "Enhanced version:", "Here's the enhanced text:",
            "Here is the enhanced text:", "Enhanced:", "Result:"
        ]
        for prefix in prefixes:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()
        
        self.logger.debug(f"Cleaned text result: {text}")
        return text