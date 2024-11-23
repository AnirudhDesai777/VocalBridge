from app.utils.logger import CustomLogger
from typing import Dict, Optional
import os
import base64
import tempfile
from yapper.speaker import BaseSpeaker
from yapper.enums import PiperVoice, PiperQuality
from yapper.utils import APP_DIR, get_random_name, install_piper, download_piper_model
import subprocess
import pygame

class CustomPiperSpeaker(BaseSpeaker):
    def __init__(
        self,
        voice: PiperVoice = PiperVoice.AMY,
        quality: PiperQuality = PiperQuality.MEDIUM,
        speed: float = 1.0,
    ):
        """
        Speaks the text using piper with speed control.
        Parameters
        ----------
        voice : str, optional
            Name of the piper voice to be used (default: PiperVoice.AMY)
        quality : str, optional
            Quality of the voice (default: PiperQuality.MEDIUM)
        speed : float, optional
            Speed multiplier for speech rate (default: 1.0)
            Values > 1.0 make speech faster
            Values < 1.0 make speech slower
        """
        assert voice in PiperVoice, f"voice must be one of {', '.join(PiperVoice)}"
        assert quality in PiperQuality, f"quality must be one of {', '.join(PiperQuality)}"
        assert 0.1 <= speed <= 3.0, "speed must be between 0.1 and 3.0"
        
        install_piper()
        self.exe_path = str(
            APP_DIR / "piper" / ("piper.exe" if os.name == "nt" else "piper")
        )
        self.onnx_f, self.conf_f = download_piper_model(voice.value, quality.value)
        self.onnx_f, self.conf_f = str(self.onnx_f), str(self.conf_f)
        self.speed = speed
        pygame.mixer.init()

    def say(self, text: str, output_file: str = None):
        """
        Speaks the given text at the specified speed
        If output_file is provided, saves the audio to that file instead of playing
        """
        # Use provided output file or generate temporary one
        f = output_file if output_file else APP_DIR / f"{get_random_name()}.wav"
        
        # length_scale is inverse of speed (0.8 length = 1.25x speed)
        length_scale = 1.0 / self.speed
        
        subprocess.run(
            [
                self.exe_path,
                "-m", self.onnx_f,
                "-c", self.conf_f,
                "-f", str(f),
                "--length-scale", str(length_scale),
                "-q",
            ],
            input=text.encode("utf-8"),
            check=True,
            stdout=subprocess.DEVNULL,
        )
        
        # Only play audio if no output file was specified
        if not output_file:
            sound = pygame.mixer.Sound(f)
            sound.play()
            while pygame.mixer.get_busy():
                pygame.time.wait(100)
            os.remove(f)

class TTSService:
    def __init__(self):
        self.logger = CustomLogger("tts_service").get_logger()
        self.logger.info("Initializing TTS Service")
        self.speakers: Dict[str, Dict[str, CustomPiperSpeaker]] = {}
        self._initialize_speakers()

    def _initialize_speakers(self):
        """Initialize different voices with CustomPiperSpeaker with quality options"""
        try:
            # Define available voices and their supported qualities
            voice_configs = {
                'amy': {'medium': PiperQuality.MEDIUM, 'low': PiperQuality.LOW},
                'arctic': {'medium': PiperQuality.MEDIUM},
                'bryce': {'medium': PiperQuality.MEDIUM},
                'danny': {'low': PiperQuality.LOW},
                'john': {'medium': PiperQuality.MEDIUM},
                'kathleen': {'low': PiperQuality.LOW},
                'kristin': {'medium': PiperQuality.MEDIUM},
                'ljspeech': {'high': PiperQuality.HIGH, 'medium': PiperQuality.MEDIUM},
                'norman': {'medium': PiperQuality.MEDIUM}
            }

            for voice_name, qualities in voice_configs.items():
                self.speakers[voice_name] = {}
                for quality_name, quality_enum in qualities.items():
                    self.logger.info(f"Initializing voice: {voice_name} ({quality_name})")
                    try:
                        speaker = self._create_speaker(voice_name, quality_enum)
                        if speaker:
                            self.speakers[voice_name][quality_name] = speaker
                            self.logger.info(f"Successfully initialized {voice_name} ({quality_name})")
                    except Exception as e:
                        self.logger.error(f"Failed to initialize {voice_name} ({quality_name}): {str(e)}")
                        continue

            self.logger.info("Voice initialization completed")

        except Exception as e:
            self.logger.error(f"Error initializing voices: {str(e)}")
            raise

    def _create_speaker(self, voice_name: str, quality: PiperQuality) -> Optional[CustomPiperSpeaker]:
        """Create a CustomPiperSpeaker instance with error handling"""
        try:
            voice_enum = getattr(PiperVoice, voice_name.upper())
            return CustomPiperSpeaker(voice=voice_enum, quality=quality)
        except Exception as e:
            self.logger.error(f"Error creating speaker for {voice_name}: {str(e)}")
            return None

    def _get_speaker(self, voice: str, quality: str = 'medium') -> CustomPiperSpeaker:
        """Get appropriate speaker based on voice and quality preference"""
        if voice not in self.speakers:
            raise ValueError(f"Voice {voice} not available")

        available_qualities = self.speakers[voice]
        if not available_qualities:
            raise ValueError(f"No qualities available for voice {voice}")

        # Try to get requested quality, fall back to available quality
        if quality in available_qualities:
            return available_qualities[quality]
        
        # Fallback logic: prefer medium > low > high
        fallback_order = ['medium', 'low', 'high']
        for fallback_quality in fallback_order:
            if fallback_quality in available_qualities:
                self.logger.warning(
                    f"Requested quality {quality} not available for {voice}, "
                    f"using {fallback_quality} instead"
                )
                return available_qualities[fallback_quality]

        # If we get here, use the first available quality
        first_quality = list(available_qualities.keys())[0]
        self.logger.warning(
            f"Using {first_quality} quality for {voice} as fallback"
        )
        return available_qualities[first_quality]

    def generate_speech(self, text: str, voice: str = 'amy', speed: float = 1.0, quality: str = 'medium') -> str:
        """Generate speech from text using specified voice and speed."""
        self.logger.info(f"Generating speech - Voice: {voice}, Speed: {speed}, Quality: {quality}, Text: {text}")
        
        # Get speaker and update its speed
        speaker = self._get_speaker(voice, quality)
        if not speaker:
            error_msg = f"Could not initialize speaker for voice: {voice}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Update speaker speed
        speaker.speed = max(0.1, min(3.0, speed))  # Clamp speed between 0.1 and 3.0

        temp_file = None
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                prefix='speech_',
                suffix='.wav',
                delete=False
            )
            temp_file.close()
            self.logger.debug(f"Created temporary file: {temp_file.name}")
            
            # Generate speech directly to the temporary file
            speaker.say(text, output_file=temp_file.name)
            
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