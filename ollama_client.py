"""Ollama LLM client for conversation generation."""
import requests
import logging
from typing import List, Dict, Optional
from config import Config

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with local Ollama instance."""
    
    def __init__(self, base_url: str = None, model: str = None):
        """Initialize Ollama client.
        
        Args:
            base_url: Ollama API base URL (defaults to config)
            model: Model name to use (defaults to config)
        """
        self.base_url = base_url or Config.OLLAMA_BASE_URL
        self.model = model or Config.OLLAMA_MODEL
        self.api_url = f"{self.base_url}/api/generate"
        
    def generate_response(self, prompt: str, context: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate a response from Ollama.
        
        Args:
            prompt: The prompt to send to the model
            context: Optional conversation history as list of dicts with 'role' and 'content'
        
        Returns:
            Generated response text
        """
        try:
            # Format context if provided
            full_prompt = prompt
            if context:
                context_str = "\n".join([f"{item['role']}: {item['content']}" for item in context])
                full_prompt = f"{context_str}\n\n{prompt}"
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            }
            
            # Increased timeout to 30 seconds to allow for model loading
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get('response', '').strip()
            return response_text
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Ollama API timeout: {e}")
            raise  # Raise exception to trigger Gemini fallback
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise  # Raise to trigger Gemini fallback
        except Exception as e:
            logger.error(f"Unexpected error in Ollama client: {e}")
            raise  # Raise to trigger Gemini fallback
    
    def check_connection(self) -> bool:
        """Check if Ollama is accessible.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Cannot connect to Ollama: {e}")
            return False
