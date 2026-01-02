"""Main entry point for the phone call agent with Gemini Live Audio and agentic capabilities."""
import asyncio
import logging
import signal
import sys
import threading
import time
from config import Config
from gemini_live_client import GeminiLiveClient
from twilio_media_streams import TwilioMediaStreamsHandler
from sub_agents import get_all_agents, get_function_declarations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PhoneCallAgent:
    """Main phone call agent with Gemini Live Audio and agentic system."""
    
    def __init__(self):
        """Initialize the phone call agent."""
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        
        if not Config.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is required for the new system")
            sys.exit(1)
        
        logger.info("Initializing phone call agent with Gemini Live Audio...")
        
        # Initialize Gemini Live client
        system_instruction = """You are a helpful AI assistant on a phone call.
        
Keep your responses concise and natural for phone conversations - aim for 1-2 sentences.
You have access to:
- Google Search for real-time information
- Calendar management for scheduling
- Customer database for lookups
- Knowledge base for company information
- Calculation tools

Be conversational, friendly, and helpful. When you need specialized information or actions,
use the appropriate function calls."""
        
        self.gemini_client = GeminiLiveClient(
            api_key=Config.GEMINI_API_KEY,
            system_instruction=system_instruction
        )
        
        # Register sub-agents
        self._register_sub_agents()
        
        # Initialize Twilio Media Streams handler
        self.twilio_handler = TwilioMediaStreamsHandler(self.gemini_client)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = True
        self.websocket_task = None
    
    def _register_sub_agents(self):
        """Register all sub-agents with the Gemini client."""
        logger.info("Registering sub-agents...")
        
        # Get all agents
        agents = get_all_agents()
        
        # Get function declarations
        declarations = get_function_declarations()
        
        # Register each function with its corresponding handler
        function_map = {
            "manage_calendar": agents["calendar"],
            "lookup_information": agents["data_lookup"],
            "customer_service": agents["customer_service"],
            "send_notification": agents["notification"],
            "calculate": agents["calculator"],
        }
        
        for declaration in declarations:
            fn_name = declaration["name"]
            if fn_name in function_map:
                agent = function_map[fn_name]
                
                # Create wrapper handler that captures the agent instance
                def make_handler(agent_instance):
                    async def handler(args):
                        return await agent_instance.execute(args)
                    return handler
                
                # Register with Gemini client
                handler = make_handler(agent)
                self.gemini_client.register_function(declaration, handler)
                logger.info(f"Registered function: {fn_name} -> {agent.name}")
        
        logger.info(f"Registered {len(function_map)} sub-agents")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Shutdown signal received, stopping agent...")
        self.running = False
    
    async def start_async(self):
        """Start the phone call agent (async)."""
        try:
            # Start WebSocket server for Media Streams in background
            self.websocket_task = asyncio.create_task(
                self.twilio_handler.start_websocket_server(
                    host='0.0.0.0',
                    port=5001
                )
            )
            
            # Give WebSocket server time to start
            await asyncio.sleep(2)
            
            logger.info("All services started successfully")
            logger.info("Ready to receive calls!")
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error during operation: {e}")
        finally:
            await self.shutdown_async()
    
    async def shutdown_async(self):
        """Shutdown the agent and cleanup (async)."""
        logger.info("Shutting down agent...")
        
        # Cancel WebSocket task
        if self.websocket_task:
            self.websocket_task.cancel()
            try:
                await self.websocket_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect Gemini
        if self.gemini_client.is_connected:
            await self.gemini_client.disconnect()
        
        logger.info("Agent stopped.")
    
    def start(self):
        """Start the phone call agent (sync wrapper)."""
        logger.info("Starting phone call agent...")
        
        # Start Flask server in a separate thread
        server_thread = threading.Thread(
            target=self.twilio_handler.run_server,
            daemon=True
        )
        server_thread.start()
        
        # Wait a moment for Flask server to start
        time.sleep(2)
        
        # Option to make outbound call
        if hasattr(Config, 'AUTO_CALL') and Config.AUTO_CALL:
            try:
                logger.info(f"Making outbound call to {Config.TARGET_PHONE_NUMBER}...")
                call_sid = self.twilio_handler.make_call()
                logger.info(f"Call initiated successfully. Call SID: {call_sid}")
            except Exception as e:
                logger.error(f"Error making call: {e}")
        else:
            logger.info("Waiting for incoming calls (set AUTO_CALL=true in config to make outbound calls)")
        
        # Run async event loop
        try:
            asyncio.run(self.start_async())
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error in event loop: {e}")


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("Phone Call Agent with Gemini Live Audio")
    logger.info("Features: Native Voice, Google Search, Agentic System")
    logger.info("=" * 60)
    
    agent = PhoneCallAgent()
    agent.start()


if __name__ == '__main__':
    main()

