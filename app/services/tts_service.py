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
            # Initialize all available voices
            voices = [
                PiperVoice.AMY, PiperVoice.ARCTIC, PiperVoice.BRYCE,
                PiperVoice.JOHN, PiperVoice.NORMAN, PiperVoice.DANNY,
                PiperVoice.KATHLEEN, PiperVoice.KRISTIN, PiperVoice.LJSPEECH
            ]
            for voice in voices:
                self.logger.info(f"Initializing voice: {voice.value}")
                try:
                    self.speakers[voice.value] = PiperSpeaker(
                        voice=voice,
                        quality=PiperQuality.MEDIUM
                    )
                except Exception as e:
                    self.logger.error(f"Failed to initialize voice {voice.value}: {str(e)}")
                    continue
            self.logger.info("Voice initialization completed")
        except Exception as e:
            self.logger.error(f"Error initializing voices: {str(e)}")
            raise

    def generate_speech(self, text: str, voice: str = 'amy', speed: float = 1.0) -> str:
        """Generate speech from text using specified voice and speed."""
        self.logger.info(f"Generating speech - Voice: {voice}, Speed: {speed}, Text: {text}")
        
        if voice not in self.speakers:
            error_msg = f"Unknown voice: {voice}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        temp_file = None
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            self.logger.debug(f"Created temporary file: {temp_file.name}")
            
            # Close the file to allow other processes to access it
            temp_file.close()
            
            # Get speaker and generate speech
            speaker = self.speakers[voice]
            
            # Generate speech to the temporary file
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
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                    self.logger.debug(f"Cleaned up temporary file: {temp_file.name}")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up temporary file: {str(e)}")