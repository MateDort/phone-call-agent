"""Main entry point for the phone call agent."""
import logging
import signal
import sys
import threading
import time
from config import Config
from ollama_client import OllamaClient
from conversation_manager import ConversationManager
from speech_handler import SpeechHandler
from twilio_handler import TwilioHandler
from elevenlabs_client import ElevenLabsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PhoneCallAgent:
    """Main phone call agent application."""
    
    def __init__(self):
        """Initialize the phone call agent."""
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        
        # Initialize components
        logger.info("Initializing phone call agent...")
        
        # Check Ollama connection
        self.ollama_client = OllamaClient()
        if not self.ollama_client.check_connection():
            logger.warning("Cannot connect to Ollama. Ollama will not be available as fallback.")
        else:
            logger.info(f"Connected to Ollama (model: {self.ollama_client.model})")
        
        # Initialize Claude client as primary LLM (optional)
        claude_client = None
        if Config.CLAUDE_API_KEY:
            api_key_display = Config.CLAUDE_API_KEY[:10] + "..." + Config.CLAUDE_API_KEY[-4:] if len(Config.CLAUDE_API_KEY) > 14 else Config.CLAUDE_API_KEY[:10] + "..."
            logger.info(f"Claude API key found: {api_key_display} (length: {len(Config.CLAUDE_API_KEY)})")
            try:
                from claude_client import ClaudeClient
                claude_client = ClaudeClient()
                logger.info(f"Claude configured (model: {claude_client.model_name}) as primary LLM.")
            except ImportError as e:
                logger.warning("Claude API key provided but anthropic package not installed. Install with: pip install anthropic")
            except Exception as e:
                logger.warning(f"Failed to initialize Claude client: {e}.")
        else:
            logger.info("No Claude API key found in configuration")

        # Initialize Gemini client as fallback (optional)
        gemini_client = None
        # Echo API key for debugging (first 10 chars only for security)
        if Config.GEMINI_API_KEY:
            api_key_display = Config.GEMINI_API_KEY[:10] + "..." + Config.GEMINI_API_KEY[-4:] if len(Config.GEMINI_API_KEY) > 14 else Config.GEMINI_API_KEY[:10] + "..."
            logger.info(f"Gemini API key found: {api_key_display} (length: {len(Config.GEMINI_API_KEY)})")
        else:
            logger.info("No Gemini API key found in configuration")

        if Config.GEMINI_API_KEY:
            try:
                from gemini_client import GeminiClient
                gemini_client = GeminiClient()
                # Skip connection check to avoid blocking startup - we'll try at runtime
                logger.info(f"Gemini configured (model: {gemini_client.model_name}) as secondary fallback.")
            except ImportError as e:
                logger.warning("Gemini API key provided but google-generativeai package not installed. Install with: pip install google-generativeai")
                gemini_client = None
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}.")
                gemini_client = None
        
        # Initialize ElevenLabs client (optional)
        elevenlabs_client = None
        if Config.ELEVENLABS_API_KEY:
            try:
                elevenlabs_client = ElevenLabsClient(
                    Config.ELEVENLABS_API_KEY, 
                    Config.ELEVENLABS_VOICE_ID,
                    Config.ELEVENLABS_MODEL_ID
                )
                logger.info(f"ElevenLabs TTS configured (voice_id: {Config.ELEVENLABS_VOICE_ID}, model_id: {Config.ELEVENLABS_MODEL_ID})")
            except Exception as e:
                logger.warning(f"Failed to initialize ElevenLabs client: {e}. Will use 'say' fallback.")
        else:
            logger.info("No ElevenLabs API key provided. Using macOS 'say' command for TTS.")

        # Initialize handlers
        self.speech_handler = SpeechHandler(elevenlabs_client=elevenlabs_client)
        self.conversation_manager = ConversationManager(self.ollama_client, claude_client, gemini_client)
        self.twilio_handler = TwilioHandler(self.conversation_manager, self.speech_handler)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = True
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Shutdown signal received, stopping agent...")
        self.running = False
    
    def start(self):
        """Start the phone call agent."""
        logger.info("Starting phone call agent...")
        
        # Start Flask server in a separate thread
        server_thread = threading.Thread(
            target=self.twilio_handler.run_server,
            daemon=True
        )
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Make the call
        try:
            logger.info(f"Calling {Config.TARGET_PHONE_NUMBER}...")
            call_sid = self.twilio_handler.make_call()
            logger.info(f"Call initiated successfully. Call SID: {call_sid}")
            logger.info("Conversation started. Press Ctrl+C to stop.")
            
            # Keep running until interrupted
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error during call: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the agent and cleanup."""
        logger.info("Shutting down agent...")
        
        # Cleanup temporary files
        try:
            self.speech_handler.cleanup_temp_files()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
        
        logger.info("Agent stopped.")


def main():
    """Main entry point."""
    agent = PhoneCallAgent()
    agent.start()


if __name__ == '__main__':
    main()
