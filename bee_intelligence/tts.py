# bee_intelligence/tts.py
from gtts import gTTS
import pygame
import tempfile
import logging
from .config import Config

class TTSEngine:
    def __init__(self):
        pygame.mixer.init()
        self.logger = logging.getLogger(__name__)
        
    def speak(self, text, lang='en'):
        try:
            with tempfile.NamedTemporaryFile(delete=True) as fp:
                tts = gTTS(text=text, lang=lang)
                tts.save(fp.name)
                pygame.mixer.music.load(fp.name)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    continue
        except Exception as e:
            self.logger.error(f"TTS Error: {e}")