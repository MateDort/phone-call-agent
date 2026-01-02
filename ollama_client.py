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
        self.api_url = f"{self.base_url}/api/chat"
        
    def generate_response(self, prompt: str, context: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate a response from Ollama using the Chat API.
        
        Args:
            prompt: The prompt to send to the model
            context: Optional conversation history as list of dicts with 'role' and 'content'
        
        Returns:
            Generated response text
        """
        try:
            messages = []
            
            # Add system message
            system_prompt = """You are a friendly AI assistant having a phone conversation. 
Keep your responses concise and natural, as if speaking over the phone. 
Be conversational and helpful. Keep responses to 1-2 sentences when possible."""
            
            messages.append({
                "role": "system",
                "content": system_prompt
            })
            
            # Add context
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
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False
            }
            
            # Increased timeout to 120 seconds for slower models/machines
            try:
                response = requests.post(self.api_url, json=payload, timeout=120)
            except requests.exceptions.RequestException as e:
                # If primary model fails/times out, try a smaller model as a last resort
                if self.model != "llama3.2:latest":
                    logger.warning(f"Ollama {self.model} failed, trying llama3.2:latest fallback...")
                    payload["model"] = "llama3.2:latest"
                    response = requests.post(self.api_url, json=payload, timeout=60)
                else:
                    raise
            
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get('message', {}).get('content', '').strip()
            return response_text
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Ollama chat API timeout: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Ollama chat client: {e}")
            raise
    
    def check_connection(self) -> bool:
        """Check if Ollama is accessible.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [m.get('name') for m in response.json().get('models', [])]
                return self.model in models or f"{self.model}:latest" in models or self.model.split(':')[0] in [m.split(':')[0] for m in models]
            return False
        except Exception as e:
            logger.error(f"Cannot connect to Ollama: {e}")
            return False
