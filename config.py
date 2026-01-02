"""Configuration management for the phone call agent."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for phone call agent."""
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+14452344131')
    TARGET_PHONE_NUMBER = os.getenv('TARGET_PHONE_NUMBER', '+14049525557')
    
    # Webhook Configuration
    WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', 'http://localhost:5002')
    WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '5002'))
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2:latest')
    
    # Gemini Configuration (now primary for voice + LLM)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'models/gemini-2.5-flash-native-audio-preview-12-2025')
    GEMINI_VOICE = os.getenv('GEMINI_VOICE', 'Kore')  # Voice name: Kore, Puck, or Charon
    
    # Agent Configuration
    AUTO_CALL = os.getenv('AUTO_CALL', 'false').lower() == 'true'  # Auto-make call on startup
    
    # Language Configuration
    LANGUAGE = os.getenv('LANGUAGE', 'english').lower()  # english or hungarian
    
    # WebSocket Configuration for Media Streams
    WEBSOCKET_PORT = int(os.getenv('WEBSOCKET_PORT', '5001'))
    WEBSOCKET_URL = os.getenv('WEBSOCKET_URL', '')  # Separate ngrok URL for WebSocket
    
    # Audio Configuration
    AUDIO_SAMPLE_RATE = int(os.getenv('AUDIO_SAMPLE_RATE', '8000'))  # Twilio uses 8kHz μ-law
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        errors = []
        
        if not cls.TWILIO_ACCOUNT_SID:
            errors.append("TWILIO_ACCOUNT_SID is required")
        if not cls.TWILIO_AUTH_TOKEN:
            errors.append("TWILIO_AUTH_TOKEN is required")
        if not cls.TWILIO_PHONE_NUMBER:
            errors.append("TWILIO_PHONE_NUMBER is required")
        if not cls.TARGET_PHONE_NUMBER:
            errors.append("TARGET_PHONE_NUMBER is required")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True

