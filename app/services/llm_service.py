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
        
        # System messages for different enhancement types
        self.humanize_message = """You are a text formatting assistant. Your task is to 
        add appropriate punctuation, breaks, and spaces to make text sound more natural 
        when spoken by a TTS system. DO NOT add, remove, or change any words. Only add
        punctuation and spacing. Example:
        Input: "hello how are you doing today i am good"
        Output: "Hello, how are you doing today? I am good."
        """
        
        self.enhance_message = """You are a helpful AI assistant specializing in 
        natural language enhancement for people with speech impairments. Your task 
        is to take user input and rephrase it into clear, well-structured sentences
        while maintaining the original meaning and intent. Focus on:
        1. Clarity and naturalness of expression
        2. Proper grammar and sentence structure
        3. Maintaining the user's intended tone and meaning
        4. Using appropriate conversational language"""

    def humanize_text(self, text: str) -> str:
        """Add punctuation and breaks for better TTS output."""
        try:
            self.logger.info(f"Humanizing text: {text}")
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.humanize_message},
                    {"role": "user", "content": f'Format: "{text}"'}
                ],
                temperature=0.3,  # Lower temperature for more consistent formatting
                max_tokens=256,
                stream=False
            )
            
            humanized_text = self._clean_response(completion.choices[0].message.content)
            self.logger.info(f"Humanized text result: {humanized_text}")
            return humanized_text
            
        except Exception as e:
            self.logger.error(f"Error humanizing text: {str(e)}")
            return text

    def enhance_text(self, text: str) -> str:
        """Enhance the text content while maintaining meaning."""
        try:
            self.logger.info(f"Enhancing text: {text}")
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.enhance_message},
                    {"role": "user", "content": f'Enhance: "{text}"'}
                ],
                temperature=0.7,
                max_tokens=256,
                stream=False
            )
            
            enhanced_text = self._clean_response(completion.choices[0].message.content)
            self.logger.info(f"Enhanced text result: {enhanced_text}")
            return enhanced_text
            
        except Exception as e:
            self.logger.error(f"Error enhancing text: {str(e)}")
            return text

    def process_text(self, text: str, should_enhance: bool = False) -> tuple[str, str]:
        """Process text through humanization and optional enhancement."""
        humanized = self.humanize_text(text)
        if should_enhance:
            enhanced = self.enhance_text(humanized)
            return humanized, enhanced
        return humanized, humanized

    def _clean_response(self, text: str) -> str:
        """Clean up the model's response."""
        self.logger.debug(f"Cleaning response text: {text}")
        
        # Remove any markdown formatting
        text = text.replace('```', '').strip()
        
        # Remove quotes
        text = text.strip('"').strip("'")
        
        # Remove explanatory text and keep only the actual output
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Skip empty lines and lines that look like explanations
            if not line or any(x in line.lower() for x in [
                'input is', 'output is', 'output remains', 'the sentence',
                'this is', 'already well', 'no enhancement', 'perfect just'
            ]):
                continue
            cleaned_lines.append(line)
        
        text = ' '.join(cleaned_lines)
        
        # Remove common prefixes
        prefixes = [
            "Enhanced text:", "Enhanced version:", "Here's the enhanced text:",
            "Here is the enhanced text:", "Enhanced:", "Result:", "Format:",
            "Formatting:", "Formatted text:", "Response:"
        ]
        for prefix in prefixes:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()
        
        # Clean up any remaining quotes or special characters
        text = text.strip('"').strip("'").strip()
        
        self.logger.debug(f"Cleaned text result: {text}")
        return text