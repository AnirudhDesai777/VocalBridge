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
        
        # Enhanced system messages for better text formatting
        self.humanize_message = """You are a text formatting assistant specializing in making text sound more natural 
        when spoken by a Text-to-Speech (TTS) system. Your task is to format text to enhance its spoken delivery by:

        1. Adding appropriate punctuation and pauses
        2. Inserting natural breaks using commas and periods
        3. Adding slight pauses using ellipsis (...) for emphasis
        4. Including breathing space with proper paragraph breaks
        5. Using em dashes (—) for natural speech transitions
        6. Adjusting spacing around punctuation marks
        7. Breaking up run-on sentences
        8. Adding appropriate question marks and exclamation points

        Important rules:
        - DO NOT change any words or their order
        - DO NOT add or remove content
        - DO NOT add descriptions or explanations
        - ONLY add punctuation and whitespace
        - Add a small pause before and after important phrases
        - Ensure there's breathing room between sentences

        Example:
        Input: "hello everyone I hope you are doing well today I wanted to talk about something important"
        Output: "Hello everyone... I hope you are doing well today. I wanted to talk about something important."
        """
        
        self.enhance_message = """You are a helpful AI assistant specializing in 
        natural language enhancement for Text-to-Speech systems. Your task 
        is to take user input and rephrase it into clear, well-structured sentences 
        that sound natural when spoken aloud. Focus on:

        1. Natural conversational flow
        2. Clear pronunciation-friendly words
        3. Proper pacing and rhythm
        4. Context-appropriate tone
        5. Smooth transitions between ideas
        6. Natural speech patterns
        7. Appropriate emphasis

        Maintain the original meaning while making it sound more natural for speech synthesis.
        """

    def humanize_text(self, text: str) -> str:
        """Add punctuation and breaks for better TTS output."""
        try:
            self.logger.info(f"Humanizing text: {text}")
            
            # Add spacing for better processing
            spaced_text = f"\n\nPlease format this text for natural speech: \"{text}\"\n"
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.humanize_message},
                    {"role": "user", "content": spaced_text}
                ],
                temperature=0.3,
                max_tokens=256,
                stream=False
            )
            
            humanized_text = self._clean_response(completion.choices[0].message.content)
            
            # Add subtle spacing and breaks
            humanized_text = self._add_speech_spacing(humanized_text)
            
            self.logger.info(f"Humanized text result: {humanized_text}")
            return humanized_text
            
        except Exception as e:
            self.logger.error(f"Error humanizing text: {str(e)}")
            return text

    def _add_speech_spacing(self, text: str) -> str:
        """Add subtle spacing and breaks for better speech synthesis."""
        # Add small pauses around punctuation
        text = text.replace('. ', '.  ')  # Double space after periods
        text = text.replace('? ', '?  ')  # Double space after questions
        text = text.replace('! ', '!  ')  # Double space after exclamations
        text = text.replace(', ', ',  ')  # Extra space after commas
        
        # Add breath marks for natural pauses
        text = text.replace(':', '... ')
        text = text.replace(';', '... ')
        
        # Ensure proper spacing around dashes
        text = text.replace('—', ' — ')
        
        # Clean up any multiple spaces
        while '   ' in text:
            text = text.replace('   ', '  ')
        
        return text.strip()

    def enhance_text(self, text: str) -> str:
        """Enhance the text content while maintaining meaning."""
        try:
            self.logger.info(f"Enhancing text: {text}")
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.enhance_message},
                    {"role": "user", "content": f'Enhance this for speech: "{text}"'}
                ],
                temperature=0.7,
                max_tokens=256,
                stream=False
            )
            
            enhanced_text = self._clean_response(completion.choices[0].message.content)
            # Apply speech spacing to enhanced text as well
            enhanced_text = self._add_speech_spacing(enhanced_text)
            
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
        
        # Extract quoted text if present
        import re
        quote_pattern = r'"([^"]*)"'
        matches = re.findall(quote_pattern, text)
        
        if matches:
            cleaned_text = matches[0].strip()
        else:
            # If no quoted text found, use basic cleaning
            cleaned_text = text.strip()
            for prefix in [
                "Here's", "Here is", "The formatted", "The enhanced",
                "Enhanced version:", "Format:", "Output:"
            ]:
                if cleaned_text.lower().startswith(prefix.lower()):
                    cleaned_text = cleaned_text[len(prefix):].strip()
            
            # Remove any remaining quotes and explanations
            cleaned_text = cleaned_text.replace('"', '').replace("'", "")
            cleaned_text = cleaned_text.split("\n")[0].strip()
        
        self.logger.debug(f"Cleaned text result: {cleaned_text}")
        return cleaned_text