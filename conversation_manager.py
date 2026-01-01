"""Conversation state management and prompt formatting."""
import logging
from typing import List, Dict, Optional
from ollama_client import OllamaClient

logger = logging.getLogger(__name__)

# Try to import Gemini client, but make it optional
try:
    from gemini_client import GeminiClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    GeminiClient = None


class ConversationManager:
    """Manages conversation state and generates responses."""
    
    def __init__(self, ollama_client: OllamaClient, gemini_client=None):
        """Initialize conversation manager.
        
        Args:
            ollama_client: Ollama client instance
            gemini_client: Optional Gemini client instance for fallback
        """
        self.ollama_client = ollama_client
        self.gemini_client = gemini_client
        self.conversation_history: List[Dict[str, str]] = []
        self.greeting_sent = False
    
    def get_greeting(self) -> str:
        """Get the initial greeting message.
        
        Returns:
            Greeting text
        """
        if not self.greeting_sent:
            self.greeting_sent = True
            return "hey friend how can i help you"
        return ""
    
    def process_user_message(self, user_text: str) -> str:
        """Process user message and generate response.
        
        Args:
            user_text: User's spoken text
        
        Returns:
            Agent's response text
        """
        if not user_text or not user_text.strip():
            return "I didn't catch that. Could you repeat?"
        
        # Add user message to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_text.strip()
        })
        
        # Try Gemini first if available, fallback to Ollama
        response = None
        
        if self.gemini_client:
            try:
                # Gemini handles system prompts via its configuration, so we just pass the user text
                response = self.gemini_client.generate_response(
                    prompt=user_text.strip(),
                    context=self.conversation_history[:-1]
                )
                logger.info("Gemini response generated successfully")
            except Exception as e:
                logger.warning(f"Gemini failed: {e}. Attempting Ollama fallback...")
        
        # Fallback to Ollama if Gemini failed or wasn't available
        if response is None:
            try:
                # Format prompt for Ollama
                prompt = self._format_prompt(user_text)
                response = self.ollama_client.generate_response(
                    prompt=prompt,
                    context=self.conversation_history[:-1]
                )
                logger.info("Ollama response generated successfully")
            except Exception as ollama_error:
                logger.error(f"Ollama fallback also failed: {ollama_error}")
                # Return fallback message if both fail
                response = "I'm having trouble processing that right now. Could you repeat?"
        
        # Add agent response to history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
        # Keep conversation history manageable (last 10 exchanges)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return response
    
    def _format_prompt(self, user_message: str) -> str:
        """Format prompt for Ollama.
        
        Args:
            user_message: User's message
        
        Returns:
            Formatted prompt
        """
        system_prompt = """You are a friendly AI assistant having a phone conversation. 
Keep your responses concise and natural, as if speaking over the phone. 
Be conversational and helpful. Keep responses to 1-2 sentences when possible."""
        
        return f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
    
    def reset(self):
        """Reset conversation state."""
        self.conversation_history = []
        self.greeting_sent = False
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()
