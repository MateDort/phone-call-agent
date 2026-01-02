"""Anthropic Claude LLM client for conversation generation."""
import logging
from typing import List, Dict, Optional
from config import Config

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for interacting with Anthropic Claude API."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """Initialize Claude client.
        
        Args:
            api_key: Claude API key (defaults to config)
            model: Model name to use (defaults to claude-3-5-sonnet-20240620)
        """
        if not CLAUDE_AVAILABLE:
            raise ImportError("anthropic package is required. Install with: pip install anthropic")
        
        self.api_key = api_key or Config.CLAUDE_API_KEY
        self.model_name = model or Config.CLAUDE_MODEL
        
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY is required")
        
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Error during Claude setup: {e}")
            raise
    
    def generate_response(self, prompt: str, context: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate a response from Claude.
        
        Args:
            prompt: The prompt to send to the model
            context: Optional conversation history as list of dicts with 'role' and 'content'
        
        Returns:
            Generated response text
        """
        try:
            # System prompt
            system_instruction = """You are a friendly AI assistant having a phone conversation. 
Keep your responses concise and natural, as if speaking over the phone. 
Be conversational and helpful. Keep responses to 1-2 sentences when possible."""
            
            # Build conversation history for Claude
            messages = []
            if context:
                for item in context:
                    role = "user" if item['role'] == 'user' else "assistant"
                    messages.append({
                        "role": role,
                        "content": item['content']
                    })
            
            # Add current prompt
            messages.append({
                "role": "user",
                "content": prompt
            })

            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=150,
                system=system_instruction,
                messages=messages
            )
            
            if response.content and hasattr(response.content[0], 'text'):
                response_text = response.content[0].text.strip()
                return response_text
            else:
                raise ValueError("Empty or invalid response from Claude")
            
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            raise
    
    def check_connection(self) -> bool:
        """Check if Claude API is accessible.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            if not self.api_key:
                return False
            # Simple test request
            test_response = self.client.messages.create(
                model=self.model_name,
                max_tokens=5,
                messages=[{"role": "user", "content": "hi"}]
            )
            return test_response is not None and len(test_response.content) > 0
        except Exception as e:
            logger.error(f"Cannot connect to Claude API: {e}")
            return False

