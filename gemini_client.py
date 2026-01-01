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
            # #region agent log
            import json, time
            with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"G3","location":"gemini_client.py:36","message":"Gemini configure start","data":{"api_key_prefix":self.api_key[:5] if self.api_key else None},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            # #region agent log
            with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"G3","location":"gemini_client.py:42","message":"Gemini configure failed","data":{"error":str(e)},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
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

            # Relax safety settings even more - using list of dicts which is more robust across versions
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_CIVIC_INTEGRITY", "threshold": "BLOCK_NONE"},
            ]
            
            # #region agent log
            import json, time
            with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"G1","location":"gemini_client.py:97","message":"Gemini request start","data":{"model":self.model_name,"is_chat":bool(chat_history),"prompt":prompt},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion

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
            
            # #region agent log
            with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                finish_reason = response.candidates[0].finish_reason if response.candidates else "unknown"
                has_parts = bool(response.candidates and response.candidates[0].content.parts)
                f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"G2","location":"gemini_client.py:105","message":"Gemini response received","data":{"finish_reason":str(finish_reason),"has_parts":has_parts,"candidates_len":len(response.candidates) if response.candidates else 0},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion

            # Check if the response was blocked by safety
            if response.candidates and response.candidates[0].finish_reason == 2:
                # #region agent log
                with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"G2","location":"gemini_client.py:111","message":"Gemini blocked by safety","data":{"prompt":prompt},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
                logger.warning(f"Gemini blocked response for prompt: {prompt}. Falling back to Ollama.")
                raise ValueError("Response blocked by safety filters")

            try:
                response_text = response.text.strip()
                return response_text
            except (AttributeError, IndexError, ValueError) as e:
                # #region agent log
                with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"G4","location":"gemini_client.py:121","message":"Gemini response text error","data":{"error":str(e)},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
                # If there's no text but it wasn't a standard safety block, still log and fail gracefully
                logger.error(f"Gemini returned empty or invalid response: {e}")
                raise ValueError("Empty response from Gemini")
            
        except Exception as e:
            # #region agent log
            import json, time
            with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","hypothesisId":"G4","location":"gemini_client.py:131","message":"Gemini API exception","data":{"error":str(e)},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
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
