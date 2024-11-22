# app/services/llm_service.py
from groq import Groq
import os
from typing import Optional

class LLMService:
    def __init__(self):
        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama2-70b-4096"  # Groq supports different LLaMA variants
        
        # System message for speech assistance
        self.system_message = """You are a helpful AI assistant specializing in 
        natural language enhancement for people with speech impairments. Your task 
        is to take user input and rephrase it into clear, well-structured sentences
        while maintaining the original meaning and intent. Focus on:
        1. Clarity and naturalness of expression
        2. Proper grammar and sentence structure
        3. Maintaining the user's intended tone and meaning
        4. Using appropriate conversational language
        """

    def enhance_text(self, text: str) -> str:
        """
        Enhance the input text using LLaMA through Groq API.
        Falls back to original text if enhancement fails.
        
        Args:
            text (str): Input text to enhance
            
        Returns:
            str: Enhanced text or original text if enhancement fails
        """
        try:
            # Create chat completion request
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": f'Enhance this text: "{text}"'}
                ],
                temperature=0.7,  # Adjust for creativity vs consistency
                max_tokens=256,   # Adjust based on your needs
                top_p=0.9,
                stream=False
            )
            
            # Extract and clean the enhanced text
            enhanced_text = completion.choices[0].message.content.strip()
            # Remove quotes if present
            enhanced_text = enhanced_text.strip('"')
            
            return enhanced_text
        
        except Exception as e:
            print(f"Error enhancing text with Groq API: {str(e)}")
            return text

    def _clean_response(self, text: str) -> str:
        """
        Clean up the model's response by removing any artifacts or unwanted formatting.
        
        Args:
            text (str): Raw response from the model
            
        Returns:
            str: Cleaned text
        """
        # Remove any markdown formatting if present
        text = text.replace('```', '').strip()
        # Remove quotes if present
        text = text.strip('"')
        # Remove "Enhanced text:" or similar prefixes if present
        prefixes = ["Enhanced text:", "Enhanced version:", "Here's the enhanced text:"]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        return text