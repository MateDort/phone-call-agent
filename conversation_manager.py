"""Conversation state management and prompt formatting."""
import logging
from typing import List, Dict, Optional
from ollama_client import OllamaClient

logger = logging.getLogger(__name__)

# Try to import Claude client
try:
    from claude_client import ClaudeClient
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    ClaudeClient = None

# Try to import Gemini client, but make it optional
try:
    from gemini_client import GeminiClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    GeminiClient = None


class ConversationManager:
    """Manages conversation state and generates responses."""
    
    def __init__(self, ollama_client: OllamaClient, claude_client=None, gemini_client=None):
        """Initialize conversation manager.
        
        Args:
            ollama_client: Ollama client instance
            claude_client: Optional Claude client instance for primary LLM
            gemini_client: Optional Gemini client instance for fallback
        """
        self.ollama_client = ollama_client
        self.claude_client = claude_client
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
        
        response = None
        
        # Try Claude first if available (as requested by user)
        if self.claude_client:
            try:
                # #region agent log
                import json, time
                with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"C1","location":"conversation_manager.py:68","message":"Trying Claude","data":{"user_text":user_text},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
                response = self.claude_client.generate_response(
                    prompt=user_text.strip(),
                    context=self.conversation_history[:-1]
                )
                if response:
                    # #region agent log
                    import json, time
                    with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"C1","location":"conversation_manager.py:75","message":"Claude success","data":{"response":response},"timestamp":int(time.time()*1000)}) + '\n')
                    # #endregion
                    logger.info("Claude response generated successfully")
            except Exception as e:
                # #region agent log
                import json, time
                with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"C1","location":"conversation_manager.py:81","message":"Claude failed","data":{"error":str(e)},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
                logger.warning(f"Claude failed: {e}. Attempting fallback...")
        
        # Fallback to Gemini if Claude failed and Gemini is available
        if response is None and self.gemini_client:
            try:
                # #region agent log
                import json, time
                with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"G1","location":"conversation_manager.py:90","message":"Trying Gemini","data":{"user_text":user_text},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
                response = self.gemini_client.generate_response(
                    prompt=user_text.strip(),
                    context=self.conversation_history[:-1]
                )
                if response:
                    # #region agent log
                    import json, time
                    with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"G1","location":"conversation_manager.py:97","message":"Gemini success","data":{"response":response},"timestamp":int(time.time()*1000)}) + '\n')
                    # #endregion
                    logger.info("Gemini response generated successfully")
            except Exception as e:
                # #region agent log
                import json, time
                with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"G1","location":"conversation_manager.py:103","message":"Gemini failed","data":{"error":str(e)},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
                logger.warning(f"Gemini failed: {e}. Attempting Ollama fallback...")

        # Fallback to Ollama if both Claude and Gemini failed
        if response is None:
            try:
                # Format prompt for Ollama
                prompt = self._format_prompt(user_text)
                # #region agent log
                import json, time
                with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"O1","location":"conversation_manager.py:114","message":"Trying Ollama","data":{"user_text":user_text},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
                response = self.ollama_client.generate_response(
                    prompt=prompt,
                    context=self.conversation_history[:-1]
                )
                if response:
                    # #region agent log
                    import json, time
                    with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"O1","location":"conversation_manager.py:122","message":"Ollama success","data":{"response":response},"timestamp":int(time.time()*1000)}) + '\n')
                    # #endregion
                    logger.info("Ollama response generated successfully")
            except Exception as ollama_error:
                # #region agent log
                import json, time
                with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"O1","location":"conversation_manager.py:128","message":"Ollama failed","data":{"error":str(ollama_error)},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
                logger.error(f"Ollama fallback also failed: {ollama_error}")
        
        # Return fallback message if all fail
        if response is None:
            response = "I'm having trouble processing that right now. Could you repeat?"
        
        # Add agent response to history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
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
