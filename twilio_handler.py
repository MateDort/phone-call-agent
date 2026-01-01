"""Twilio integration for phone calls and webhooks."""
import logging
from flask import Flask, request, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.base.exceptions import TwilioException
from config import Config
from conversation_manager import ConversationManager
from speech_handler import SpeechHandler
import os

logger = logging.getLogger(__name__)


class TwilioHandler:
    """Handles Twilio phone call operations."""
    
    def __init__(self, conversation_manager: ConversationManager, speech_handler: SpeechHandler):
        """Initialize Twilio handler.
        
        Args:
            conversation_manager: Conversation manager instance
            speech_handler: Speech handler instance
        """
        self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.conversation_manager = conversation_manager
        self.speech_handler = speech_handler
        self.app = Flask(__name__)
        self._setup_routes()
        self.active_call_sid = None
    
    def _setup_routes(self):
        """Set up Flask routes for Twilio webhooks."""
        
        @self.app.route('/webhook/voice', methods=['POST'])
        def voice_webhook():
            """Handle incoming voice webhook from Twilio."""
            try:
                response = VoiceResponse()
                
                # Get greeting if first interaction
                greeting = self.conversation_manager.get_greeting()
                
                if greeting:
                    # Generate audio for greeting
                    try:
                        audio_path = self.speech_handler.text_to_speech(greeting)
                        # Serve audio file
                        audio_url = f"{Config.WEBHOOK_BASE_URL}/audio/{os.path.basename(audio_path)}"
                        response.play(audio_url)
                    except Exception as e:
                        logger.error(f"Error generating greeting audio: {e}")
                        response.say(greeting, voice='alice')
                
                # Set up Gather to collect user speech
                gather = Gather(
                    input='speech',
                    action='/webhook/gather',
                    method='POST',
                    speech_timeout='auto',
                    language='en-US'
                )
                response.append(gather)
                
                # If no input, redirect to gather
                response.redirect('/webhook/gather', method='POST')
                
                return Response(str(response), mimetype='text/xml')
            except Exception as e:
                logger.error(f"Error in voice_webhook: {e}")
                raise
        
        @self.app.route('/webhook/gather', methods=['POST'])
        def gather_webhook():
            """Handle speech input from user."""
            response = VoiceResponse()
            
            # Get speech result from Twilio
            speech_result = request.form.get('SpeechResult', '').strip()
            
            if speech_result:
                logger.info(f"User said: {speech_result}")
                
                # Process user message and get response
                try:
                    agent_response = self.conversation_manager.process_user_message(speech_result)
                    logger.info(f"Agent responding: {agent_response}")
                except Exception as e:
                    logger.error(f"Error processing user message: {e}")
                    agent_response = "I'm sorry, I encountered an error processing your message."
                
                # Generate audio for response
                try:
                    audio_path = self.speech_handler.text_to_speech(agent_response)
                    audio_url = f"{Config.WEBHOOK_BASE_URL}/audio/{os.path.basename(audio_path)}"
                    response.play(audio_url)
                except Exception as e:
                    logger.error(f"Error generating response audio: {e}")
                    # Fallback to Twilio TTS
                    response.say(agent_response, voice='alice')
            
            # Continue gathering input
            gather = Gather(
                input='speech',
                action='/webhook/gather',
                method='POST',
                speech_timeout='auto',
                language='en-US'
            )
            response.append(gather)
            
            # If no input, redirect back
            response.redirect('/webhook/gather', method='POST')
            
            return Response(str(response), mimetype='text/xml')
        
        @self.app.route('/webhook/status', methods=['POST'])
        def status_webhook():
            """Handle call status updates."""
            call_sid = request.form.get('CallSid')
            call_status = request.form.get('CallStatus')
            logger.info(f"Call {call_sid} status: {call_status}")
            
            if call_status in ['completed', 'failed', 'busy', 'no-answer']:
                # Reset conversation on call end
                self.conversation_manager.reset()
                self.active_call_sid = None
            
            return Response('', mimetype='text/xml')
        
        @self.app.route('/audio/<filename>', methods=['GET'])
        def serve_audio(filename):
            """Serve audio files."""
            try:
                audio_path = self.speech_handler.temp_dir / filename
                if audio_path.exists():
                    with open(audio_path, 'rb') as f:
                        audio_data = f.read()
                    return Response(
                        audio_data,
                        mimetype='audio/wav',
                        headers={'Content-Disposition': f'inline; filename={filename}'}
                    )
                else:
                    return Response('Audio file not found', status=404)
            except Exception as e:
                logger.error(f"Error serving audio: {e}")
                return Response('Error serving audio', status=500)
    
    def make_call(self, to_number: str = None, from_number: str = None) -> str:
        """Make an outbound call.
        
        Args:
            to_number: Phone number to call (defaults to config)
            from_number: Twilio phone number to call from (defaults to config)
        
        Returns:
            Call SID
        """
        to_number = to_number or Config.TARGET_PHONE_NUMBER
        from_number = from_number or Config.TWILIO_PHONE_NUMBER
        
        webhook_url = f"{Config.WEBHOOK_BASE_URL}/webhook/voice"
        status_callback = f"{Config.WEBHOOK_BASE_URL}/webhook/status"
        
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=from_number,
                url=webhook_url,
                status_callback=status_callback,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                method='POST'
            )
            
            self.active_call_sid = call.sid
            logger.info(f"Call initiated: {call.sid} to {to_number}")
            return call.sid
            
        except TwilioException as e:
            logger.error(f"Twilio error making call: {e}")
            raise
        except Exception as e:
            logger.error(f"Error making call: {e}")
            raise
    
    def run_server(self, port: int = None, debug: bool = False):
        """Run Flask webhook server.
        
        Args:
            port: Port to run server on (defaults to config)
            debug: Enable debug mode
        """
        port = port or Config.WEBHOOK_PORT
        logger.info(f"Starting webhook server on port {port}")
        self.app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
