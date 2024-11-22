from yapper import Yapper, PiperSpeaker, PiperVoice, PiperQuality
import os
import base64
import tempfile
from app.utils.logger import CustomLogger

class TTSService:
    def __init__(self):
        self.logger = CustomLogger("tts_service").get_logger()
        self.logger.info("Initializing TTS Service")
        self.speakers = {}
        self._initialize_speakers()

    def _initialize_speakers(self):
        """Initialize different voices with PiperSpeaker"""
        try:
            voices = [PiperVoice.AMY, PiperVoice.ARCTIC, PiperVoice.BRYCE]
            for voice in voices:
                self.logger.info(f"Initializing voice: {voice.value}")
                self.speakers[voice.value] = PiperSpeaker(
                    voice=voice,
                    quality=PiperQuality.MEDIUM
                )
            self.logger.info("All voices initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing voices: {str(e)}")
            raise

    def generate_speech(self, text, voice='amy'):
        """Generate speech from text using specified voice."""
        self.logger.info(f"Generating speech for voice '{voice}' with text: {text}")
        
        if voice not in self.speakers:
            error_msg = f"Unknown voice: {voice}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Create temporary file for audio output
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            try:
                self.logger.debug(f"Created temporary file: {temp_file.name}")
                speaker = self.speakers[voice]
                
                # Generate speech
                speaker.say(text)
                
                # Read and encode the audio file
                with open(temp_file.name, 'rb') as audio_file:
                    audio_data = audio_file.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                self.logger.info("Speech generation successful")
                return audio_base64
                
            except Exception as e:
                self.logger.error(f"Error generating speech: {str(e)}")
                raise
            finally:
                # Clean up
                try:
                    os.unlink(temp_file.name)
                    self.logger.debug(f"Cleaned up temporary file: {temp_file.name}")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up temporary file: {str(e)}")