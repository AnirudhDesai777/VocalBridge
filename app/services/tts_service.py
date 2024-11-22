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
            # Initialize core voices with higher quality
            core_voices = {
                'amy': PiperVoice.AMY,
                'arctic': PiperVoice.ARCTIC,
                'bryce': PiperVoice.BRYCE,
                'john': PiperVoice.JOHN,
                'norman': PiperVoice.NORMAN
            }
            
            for voice_name, voice_enum in core_voices.items():
                self.logger.info(f"Initializing voice: {voice_name}")
                try:
                    self.speakers[voice_name] = PiperSpeaker(
                        voice=voice_enum,
                        quality=PiperQuality.HIGH  # Use high quality for better sound
                    )
                except Exception as e:
                    self.logger.error(f"Failed to initialize voice {voice_name}: {str(e)}")
                    # Try with medium quality as fallback
                    try:
                        self.speakers[voice_name] = PiperSpeaker(
                            voice=voice_enum,
                            quality=PiperQuality.MEDIUM
                        )
                    except Exception as e2:
                        self.logger.error(f"Fallback failed for {voice_name}: {str(e2)}")
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
            # Create temporary file with unique name
            temp_file = tempfile.NamedTemporaryFile(
                prefix='speech_',
                suffix='.wav',
                delete=False
            )
            self.logger.debug(f"Created temporary file: {temp_file.name}")
            
            # Close the file to ensure it's accessible
            temp_file.close()
            
            speaker = self.speakers[voice]
            
            # Generate speech with enhanced quality
            speaker_args = {
                'text': text,
                'output_file': temp_file.name
            }
            
            if hasattr(speaker, 'set_speed'):
                speaker.set_speed(speed)
            
            # Generate speech
            speaker.say(**speaker_args)
            
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
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                    self.logger.debug(f"Cleaned up temporary file: {temp_file.name}")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up temporary file: {str(e)}")