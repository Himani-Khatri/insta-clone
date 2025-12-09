# bee_intelligence/config.py
import os
from pathlib import Path

class Config:
    # Voice Settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    VOICE_PROFILE_PATH = Path("bee_intelligence/voice_profiles")
    
    # AI Settings
    MODEL_PATH = Path("bee_intelligence/models/intent_classifier.h5")  # Example model
    CONVERSATION_LOG = Path("conversations.log")
    
    # Security
    OWNER_ID = os.getenv("BEE_OWNER_ID", "default_owner")
    WAKE_WORD = "hey bee"
    
    @classmethod
    def setup_directories(cls):
        cls.VOICE_PROFILE_PATH.mkdir(exist_ok=True, parents=True)

Config.setup_directories()