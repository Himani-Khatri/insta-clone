# bee_intelligence/voice.py
import speech_recognition as sr
import numpy as np
import logging
from .config import Config

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.logger = logging.getLogger(__name__)
        self.voice_profiles = {}  # Stores voice profiles for enrolled users

    def enroll_voice(self, user_id, num_samples=3):
        """
        Enrolls a user's voice by capturing and storing voice samples.
        """
        self.logger.info(f"Starting voice enrollment for user {user_id}.")
        samples = []

        for i in range(num_samples):
            print(f"Please say the wake word (sample {i + 1}/{num_samples}):")
            with self.microphone as source:
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                    audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
                    samples.append(audio_data)
                    print("Sample captured.")
                except sr.WaitTimeoutError:
                    print("No speech detected. Please try again.")
                    return False
                except Exception as e:
                    self.logger.error(f"Error during enrollment: {e}")
                    return False

        # Store the voice samples for the user
        self.voice_profiles[user_id] = samples
        self.logger.info(f"Voice enrollment completed for user {user_id}.")
        return True

    def listen(self, timeout=5):
        """
        Listens for voice input and returns the recognized text.
        """
        with self.microphone as source:
            try:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio)
                self.logger.info(f"Recognized text: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                self.logger.warning("No speech detected within the timeout period.")
                return None
            except sr.UnknownValueError:
                self.logger.warning("Speech recognition could not understand the audio.")
                return None
            except Exception as e:
                self.logger.error(f"Voice recognition error: {e}")
                return None

    def verify_voice(self, user_id, audio_data):
        """
        Verifies if the provided audio data matches the enrolled voice profile.
        """
        if user_id not in self.voice_profiles:
            self.logger.warning(f"No voice profile found for user {user_id}.")
            return False

        # Simplified verification logic (for demonstration purposes)
        # In a real-world scenario, use a voice verification model or library
        enrolled_samples = self.voice_profiles[user_id]
        similarity_score = self._compare_audio(audio_data, enrolled_samples[0])  # Compare with the first sample

        # Threshold for verification (can be adjusted)
        if similarity_score > 0.8:
            self.logger.info(f"Voice verification successful for user {user_id}.")
            return True
        else:
            self.logger.warning(f"Voice verification failed for user {user_id}.")
            return False

    def _compare_audio(self, audio1, audio2):
        """
        Compares two audio samples and returns a similarity score.
        This is a placeholder implementation and should be replaced with a proper audio comparison algorithm.
        """
        # Placeholder: Calculate similarity based on the length of the audio data
        len1 = len(audio1)
        len2 = len(audio2)
        similarity = 1 - abs(len1 - len2) / max(len1, len2)
        return similarity