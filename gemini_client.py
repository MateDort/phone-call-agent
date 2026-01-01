"""Google Gemini LLM client for conversation generation."""
import logging
from typing import List, Dict, Optional
from config import Config

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """Initialize Gemini client.
        
        Args:
            api_key: Gemini API key (defaults to config)
            model: Model name to use (defaults to gemini-1.5-flash)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package is required. Install with: pip install google-generativeai")
        
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model_name = model or Config.GEMINI_MODEL
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            logger.error(f"Error during Gemini setup: {e}")
            raise
    
    def generate_response(self, prompt: str, context: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate a response from Gemini.
        
        Args:
            prompt: The prompt to send to the model
            context: Optional conversation history as list of dicts with 'role' and 'content'
        
        Returns:
            Generated response text
        """
        try:
            # System prompt for Gemini
            system_instruction = """You are a friendly AI assistant having a phone conversation. 
Keep your responses concise and natural, as if speaking over the phone. 
Be conversational and helpful. Keep responses to 1-2 sentences when possible."""
            
            # Build conversation history for Gemini
            chat_history = []
            if context:
                for item in context:
                    role = "user" if item['role'] == 'user' else "model"
                    chat_history.append({
                        "role": role,
                        "parts": [item['content']]
                    })
            
            # Create model with system instruction and generation config for speed
            generation_config = {
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 100,  # Keep responses short for fast phone conversations
            }

            # Relax safety settings to prevent benign responses from being blocked
            # Note: HARM_CATEGORY_CIVIC_INTEGRITY might not be available in all SDK versions
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            # Add CIVIC_INTEGRITY only if it exists in the current SDK version
            if hasattr(HarmCategory, "HARM_CATEGORY_CIVIC_INTEGRITY"):
                safety_settings[HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY] = HarmBlockThreshold.BLOCK_NONE
            
            model_with_instruction = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Start or continue chat
            if chat_history:
                chat = model_with_instruction.start_chat(history=chat_history)
                response = chat.send_message(prompt)
            else:
                response = model_with_instruction.generate_content(prompt)
            
            # Check if the response was blocked by safety
            if response.candidates and response.candidates[0].finish_reason == 2:
                logger.warning(f"Gemini blocked response for prompt: {prompt}. Falling back to Ollama.")
                raise ValueError("Response blocked by safety filters")

            try:
                response_text = response.text.strip()
                return response_text
            except (AttributeError, IndexError, ValueError) as e:
                # If there's no text but it wasn't a standard safety block, still log and fail gracefully
                logger.error(f"Gemini returned empty or invalid response: {e}")
                raise ValueError("Empty response from Gemini")
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise
    
    def check_connection(self) -> bool:
        """Check if Gemini API is accessible.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            if not self.api_key:
                return False
            # Simple test request with timeout
            try:
                test_model = genai.GenerativeModel(self.model_name)
                test_response = test_model.generate_content("test")
                return test_response is not None and test_response.text is not None
            except Exception as test_error:
                logger.debug(f"Gemini connection test failed: {test_error}")
                return False
        except Exception as e:
            logger.error(f"Cannot connect to Gemini API: {e}")
            return False
