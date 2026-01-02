"""Main entry point for elderly care phone agent with Gemini Live Audio."""
import asyncio
import logging
import signal
import sys
import threading
import time
from config import Config
from database import Database
from gemini_live_client import GeminiLiveClient
from twilio_media_streams import TwilioMediaStreamsHandler
from sub_agents_elderly import get_all_agents, get_function_declarations
from reminder_checker import ReminderChecker
from translations import format_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ElderlyPhoneAgent:
    """Elderly care phone agent with Gemini Live Audio and local database."""
    
    def __init__(self):
        """Initialize the elderly care phone agent."""
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        
        if not Config.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is required")
            sys.exit(1)
        
        logger.info("Initializing elderly care phone agent...")
        
        # Initialize database
        self.db = Database("elderly_care.db")
        logger.info("Database initialized")
        
        # Initialize Gemini Live client
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        
        system_instruction = format_text(
            'elderly_system_instruction',
            Config.LANGUAGE,
            current_time=current_time,
            current_date=current_date
        )
        
        self.gemini_client = GeminiLiveClient(
            api_key=Config.GEMINI_API_KEY,
            system_instruction=system_instruction
        )
        
        # Register sub-agents
        self._register_sub_agents()
        
        # Initialize reminder checker (will be passed to Twilio handler)
        self.reminder_checker = ReminderChecker(
            db=self.db,
            call_trigger=self._trigger_reminder_call,
            gemini_client=self.gemini_client
        )
        
        # Initialize Twilio handler with reminder checker for call status tracking
        self.twilio_handler = TwilioMediaStreamsHandler(
            self.gemini_client,
            reminder_checker=self.reminder_checker
        )
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = True
        self.websocket_task = None
        self.reminder_task = None
    
    def _register_sub_agents(self):
        """Register all sub-agents with the Gemini client."""
        logger.info("Registering sub-agents...")
        
        # Get all agents (pass database)
        agents = get_all_agents(self.db)
        
        # Get function declarations
        declarations = get_function_declarations()
        
        # Register each function with its handler
        function_map = {
            "manage_reminder": agents["reminder"],
            "lookup_user_info": agents["user_bio"],
            "lookup_contact": agents["contacts"],
            "send_notification": agents["notification"],
        }
        
        for declaration in declarations:
            fn_name = declaration["name"]
            if fn_name in function_map:
                agent = function_map[fn_name]
                
                # Create wrapper handler
                def make_handler(agent_instance):
                    async def handler(args):
                        return await agent_instance.execute(args)
                    return handler
                
                # Register with Gemini client
                handler = make_handler(agent)
                self.gemini_client.register_function(declaration, handler)
                logger.info(f"Registered function: {fn_name} -> {agent.name}")
            elif fn_name == "get_current_time":
                # Special handler for get_current_time
                async def get_time_handler(args):
                    from datetime import datetime
                    now = datetime.now()
                    current_time = now.strftime("%I:%M %p")
                    current_date = now.strftime("%A, %B %d, %Y")
                    return {
                        "time": current_time,
                        "date": current_date,
                        "message": f"The current time is {current_time} on {current_date}"
                    }
                
                self.gemini_client.register_function(declaration, get_time_handler)
                logger.info(f"Registered function: {fn_name} -> time utility")
        
        logger.info(f"Registered {len(function_map)} sub-agents")
    
    async def _trigger_reminder_call(self, reminder: dict):
        """Trigger an outbound call for a reminder.
        
        Args:
            reminder: Reminder dictionary from database
        """
        logger.info(f"Triggering reminder call for: {reminder['title']}")
        
        try:
            # Make outbound call via Twilio with reminder message
            reminder_message = f"You have a reminder: {reminder['title']}"
            call_sid = self.twilio_handler.make_call(reminder_message=reminder_message)
            logger.info(f"Reminder call initiated: {call_sid}")
            
        except Exception as e:
            logger.error(f"Error making reminder call: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Shutdown signal received, stopping agent...")
        self.running = False
        self.reminder_checker.stop()
    
    async def start_async(self):
        """Start the phone call agent (async)."""
        try:
            # Start reminder checker in background
            self.reminder_task = asyncio.create_task(self.reminder_checker.start())
            logger.info("Reminder checker started")
            
            # Start WebSocket server for Media Streams in background
            self.websocket_task = asyncio.create_task(
                self.twilio_handler.start_websocket_server(
                    host='0.0.0.0',
                    port=Config.WEBSOCKET_PORT
                )
            )
            
            # Give WebSocket server time to start
            await asyncio.sleep(2)
            
            logger.info("=" * 60)
            logger.info("Elderly Care Phone Agent Ready!")
            logger.info("=" * 60)
            logger.info("Features:")
            logger.info("  ✓ Medication & task reminders (automatic calls)")
            logger.info("  ✓ Family & friends contacts with birthdays")
            logger.info("  ✓ User biographical information")
            logger.info("  ✓ Google Search for current info")
            logger.info("  ✓ Natural voice conversations")
            logger.info("=" * 60)
            logger.info("Waiting for calls...")
            
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
        
        # Stop reminder checker
        self.reminder_checker.stop()
        
        # Cancel tasks
        if self.reminder_task:
            self.reminder_task.cancel()
            try:
                await self.reminder_task
            except asyncio.CancelledError:
                pass
        
        if self.websocket_task:
            self.websocket_task.cancel()
            try:
                await self.websocket_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect Gemini
        if self.gemini_client.is_connected:
            await self.gemini_client.disconnect()
        
        # Close database
        self.db.close()
        
        logger.info("Agent stopped.")
    
    def start(self):
        """Start the phone call agent (sync wrapper)."""
        logger.info("Starting elderly care phone agent...")
        
        # Start Flask server in a separate thread
        server_thread = threading.Thread(
            target=self.twilio_handler.run_server,
            daemon=True
        )
        server_thread.start()
        
        
        # Wait for Flask server to start
        time.sleep(2)
        
        
        # Option to make outbound call
        if hasattr(Config, 'AUTO_CALL') and Config.AUTO_CALL:
            try:
                logger.info(f"Making outbound call to {Config.TARGET_PHONE_NUMBER}...")
                call_sid = self.twilio_handler.make_call()
                logger.info(f"Call initiated successfully. Call SID: {call_sid}")
            except Exception as e:
                logger.error(f"Error making call: {e}")
        
        # Run async event loop
        try:
            asyncio.run(self.start_async())
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error in event loop: {e}")


def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("  ELDERLY CARE PHONE AGENT")
    print("  Powered by Gemini Live Audio")
    print("=" * 60)
    print("\nFeatures:")
    print("  🔔 Smart Reminders - Automatic calls for medications & tasks")
    print("  👥 Family Contacts - Quick access to loved ones")
    print("  📖 Personal Bio - Your life story at your fingertips")
    print("  🔍 Google Search - Current weather, news, and info")
    print("  🎤 Natural Voice - Just talk like you would to a friend")
    print("=" * 60 + "\n")
    
    agent = ElderlyPhoneAgent()
    agent.start()


if __name__ == '__main__':
    main()

