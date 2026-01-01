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
    WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', 'http://localhost:5000')
    WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '5000'))
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2:latest')
    
    # Gemini Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')  # Updated to 'gemini-flash-latest' based on ListModels output
    
    # Claude Configuration
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-opus-4-5-20251101')
    
    # ElevenLabs Configuration
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
    ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', 'EXAVIT9mxAsU4AKpD7Kx')  # Default: Bella
    ELEVENLABS_MODEL_ID = os.getenv('ELEVENLABS_MODEL_ID', 'eleven_turbo_v2_5')  # Turbo v2.5 for lowest latency
    
    # Audio Configuration
    AUDIO_TEMP_DIR = os.getenv('AUDIO_TEMP_DIR', '/tmp/phone_agent_audio')
    AUDIO_FORMAT = 'wav'  # Format for Twilio compatibility
    
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

