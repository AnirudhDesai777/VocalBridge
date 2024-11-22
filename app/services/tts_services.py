from yapper import Yapper, PiperSpeaker, PiperVoice, PiperQuality
import os
import base64
import tempfile

class TTSService:
    def __init__(self):
        self.speakers = {}
        self._initialize_speakers()

    def _initialize_speakers(self):
        """Initialize different voices with PiperSpeaker"""
        voices = [PiperVoice.AMY, PiperVoice.ARCTIC, PiperVoice.BRYCE]
        for voice in voices:
            self.speakers[voice.value] = PiperSpeaker(
                voice=voice,
                quality=PiperQuality.MEDIUM
            )

    def generate_speech(self, text, voice='amy'):
        """
        Generate speech from text using specified voice.
        Returns base64 encoded WAV data.
        """
        if voice not in self.speakers:
            raise ValueError(f"Unknown voice: {voice}")

        # Create temporary file for audio output
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            try:
                # Generate speech to temporary file
                speaker = self.speakers[voice]
                speaker.say(text)
                
                # Read the generated audio file and encode to base64
                with open(temp_file.name, 'rb') as audio_file:
                    audio_data = audio_file.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                return audio_base64
            finally:
                # Clean up temporary file
                os.unlink(temp_file.name)