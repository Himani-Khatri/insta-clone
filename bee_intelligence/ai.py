import json
from typing import Dict, Optional, List
from .memory import ConversationMemory

class BeeAI:
    def __init__(self, db_path: str = 'bee.db'):
        self.memory = ConversationMemory(db_path)
        self.conversation_flows = self._load_conversation_flows()

    def _load_conversation_flows(self) -> Dict:
        """Load conversation flows from configuration"""
        return {
            'greeting': {
                'patterns': ['hello', 'hi', 'hey'],
                'responses': [
                    "Hey hey! What's buzzing?",
                    "Yo, what's good?",
                    "Hey there, how can I help you today?"
                ],
                'next_states': ['ask_mood', 'offer_help']
            },
            'ask_mood': {
                'patterns': ['how are you', 'how\'s it going'],
                'responses': [
                    "I'm buzzing with energy! How about you?",
                    "I'm having a fantastic day! How are you feeling?"
                ],
                'next_states': ['handle_mood_response', 'offer_help']
            }
            # Add more conversation flows as needed
        }

    def process_input(self, user_id: int, text: str) -> str:
        """
        Process user input and generate appropriate response
        """
        # Get user context and recent conversations
        context = self.memory.get_user_context(user_id)
        
        # Determine conversation state and generate response
        response = self._generate_response(text, context)
        
        # Store conversation
        self.memory.store_conversation(user_id, text, response)
        
        return response

    def _generate_response(self, text: str, context: Dict) -> str:
        """
        Generate contextual response based on input and conversation history
        """
        text = text.lower()
        
        # Check for matching conversation flows
        for flow_name, flow in self.conversation_flows.items():
            if any(pattern in text for pattern in flow['patterns']):
                responses = flow['responses']
                return responses[hash(text) % len(responses)]
        
        # Default response if no flow matches
        return "I'm not sure how to respond to that. Could you rephrase?"

    def handle_media_command(self, command: str) -> Dict:
        """
        Process commands related to media posting
        """
        if 'post' in command or 'upload' in command:
            media_type = 'photo' if 'photo' in command else 'video'
            return {
                'action': 'media_upload',
                'type': media_type,
                'caption': command.replace(f'post {media_type}', '').strip()
            }
        return {'action': 'none'}

    def is_owner_command(self, command: str) -> bool:
        """
        Check if command requires owner privileges
        """
        owner_commands = [
            'system settings',
            'delete all',
            'reset system',
            'modify permissions'
        ]
        return any(cmd in command.lower() for cmd in owner_commands)