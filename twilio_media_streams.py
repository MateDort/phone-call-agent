"""Twilio Media Streams integration for real-time audio with Gemini Live."""
import asyncio
import json
import base64
import logging
import websockets
import sys
import audioop  # audioop-lts package provides the 'audioop' module for Python 3.13+
from typing import Optional
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from twilio.rest import Client
from config import Config
from gemini_live_client import GeminiLiveClient

logger = logging.getLogger(__name__)


class TwilioMediaStreamsHandler:
    """Handles Twilio Media Streams WebSocket connection with Gemini Live."""
    
    def __init__(self, gemini_client: GeminiLiveClient):
        """Initialize handler.
        
        Args:
            gemini_client: GeminiLiveClient instance
        """
        self.gemini_client = gemini_client
        self.twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.app = Flask(__name__)
        self._setup_routes()
        
        # WebSocket state
        self.websocket_server = None
        self.active_connections = {}
        
    def _setup_routes(self):
        """Set up Flask routes for Twilio webhooks."""
        
        @self.app.route('/webhook/voice', methods=['POST'])
        def voice_webhook():
            """Handle incoming call - start media stream."""
            try:
                response = VoiceResponse()
                
                # Optional: Play a brief greeting
                response.say("Hello, connecting you now", voice='Polly.Joanna')
                
                # Connect to Media Streams WebSocket
                # WebSocket runs on port 5001 with its own ngrok URL
                connect = Connect()
                if Config.WEBSOCKET_URL:
                    # Use configured WebSocket URL (from separate ngrok tunnel)
                    websocket_url = Config.WEBSOCKET_URL.replace("https://", "").replace("http://", "")
                    stream = Stream(url=f'wss://{websocket_url}/media-stream')
                else:
                    # Fallback: assume same domain (won't work with separate tunnels)
                    websocket_base = Config.WEBHOOK_BASE_URL.replace("https://", "").replace("http://", "")
                    stream = Stream(url=f'wss://{websocket_base}/media-stream')
                connect.append(stream)
                response.append(connect)
                
                
                return Response(str(response), mimetype='text/xml')
                
            except Exception as e:
                logger.error(f"Error in voice_webhook: {e}")
                response = VoiceResponse()
                response.say("Sorry, an error occurred")
                return Response(str(response), mimetype='text/xml')
        
        @self.app.route('/webhook/status', methods=['POST'])
        def status_webhook():
            """Handle call status updates."""
            call_sid = request.form.get('CallSid')
            call_status = request.form.get('CallStatus')
            logger.info(f"Call {call_sid} status: {call_status}")
            
            if call_status in ['completed', 'failed', 'busy', 'no-answer']:
                # Cleanup connection
                if call_sid in self.active_connections:
                    del self.active_connections[call_sid]
            
            return Response('', mimetype='text/xml')
    
    async def handle_media_stream(self, websocket):
        """Handle WebSocket connection from Twilio Media Streams.
        
        Args:
            websocket: WebSocket connection
        """
        # Note: 'path' parameter removed - websockets library no longer passes it in newer versions
        call_sid = None
        stream_sid = None
        
        try:
            logger.info("Media stream connected")
            
            
            # Connect to Gemini Live
            await self.gemini_client.connect()
            
            
            # Set up audio callback to send Gemini's audio back to Twilio
            async def send_audio_to_twilio(audio_data: bytes):
                """Send Gemini's audio response back to caller."""
                try:
                    # Gemini outputs audio/pcm at 24kHz by default, Twilio expects μ-law at 8kHz
                    # Step 1: Resample from 24kHz to 8kHz
                    pcm_8k, _ = audioop.ratecv(
                        audio_data,
                        2,      # sample width (16-bit = 2 bytes)
                        1,      # channels (mono)
                        24000,  # input rate (24kHz from Gemini)
                        8000,   # output rate (8kHz for Twilio)
                        None    # state
                    )
                    
                    # Step 2: Convert Linear PCM to μ-law
                    ulaw_audio = audioop.lin2ulaw(pcm_8k, 2)
                    
                    # Encode audio as base64
                    audio_base64 = base64.b64encode(ulaw_audio).decode('utf-8')
                    
                    # Send to Twilio
                    media_message = {
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {
                            "payload": audio_base64
                        }
                    }
                    await websocket.send(json.dumps(media_message))
                    
                except Exception as e:
                    logger.error(f"Error sending audio to Twilio: {e}")
            
            self.gemini_client.on_audio_response = send_audio_to_twilio
            
            # Process messages from Twilio
            async for message in websocket:
                try:
                    data = json.loads(message)
                    event = data.get('event')
                    
                    if event == 'start':
                        # Stream started
                        call_sid = data['start']['callSid']
                        stream_sid = data['start']['streamSid']
                        self.active_connections[call_sid] = {
                            'stream_sid': stream_sid,
                            'websocket': websocket
                        }
                        logger.info(f"Stream started: {stream_sid} for call {call_sid}")
                    
                    elif event == 'media':
                        # #region agent log
                        import time as time_module
                        with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                            f.write(json.dumps({"location":"twilio_media_streams.py:169","message":"Media event received from Twilio","data":{"payload_length":len(data['media']['payload'])},"timestamp":int(time_module.time()*1000),"sessionId":"debug-session","hypothesisId":"H3,H5"})+"\n")
                        # #endregion
                        
                        # Audio from caller
                        payload = data['media']['payload']
                        
                        # Decode from base64
                        audio_data = base64.b64decode(payload)
                        
                        # Convert μ-law (8kHz) to Linear PCM 24kHz
                        # Twilio sends μ-law at 8kHz, Gemini expects PCM at 24kHz
                        try:
                            # Step 1: Convert μ-law to linear PCM (still 8kHz)
                            pcm_8k = audioop.ulaw2lin(audio_data, 2)  # 2 = 16-bit samples
                            
                            # Step 2: Resample from 8kHz to 24kHz
                            pcm_24k, _ = audioop.ratecv(
                                pcm_8k,
                                2,      # sample width (16-bit = 2 bytes)
                                1,      # channels (mono)
                                8000,   # input rate (8kHz from Twilio)
                                24000,  # output rate (24kHz for Gemini)
                                None    # state
                            )
                            
                            # #region agent log
                            import time as time_module
                            with open('/Users/matedort/phone-call-agent/.cursor/debug.log', 'a') as f:
                                f.write(json.dumps({"location":"twilio_media_streams.py:196","message":"Audio converted, sending to Gemini","data":{"pcm_24k_length":len(pcm_24k)},"timestamp":int(time_module.time()*1000),"sessionId":"debug-session","hypothesisId":"H3,H5"})+"\n")
                            # #endregion
                            
                            # Send to Gemini with correct format
                            await self.gemini_client.send_audio(
                                pcm_24k,
                                mime_type="audio/pcm;rate=24000"
                            )
                        except Exception as e:
                            logger.error(f"Error converting audio: {e}")
                            raise
                    
                    elif event == 'stop':
                        # Stream ended
                        logger.info(f"Stream stopped: {stream_sid}")
                        break
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from Twilio: {e}")
                except Exception as e:
                    logger.error(f"Error processing Twilio message: {e}")
            
        except websockets.exceptions.ConnectionClosed:
            logger.info("Media stream connection closed")
        except Exception as e:
            logger.error(f"Error in media stream handler: {e}")
        finally:
            # Cleanup
            await self.gemini_client.disconnect()
            if call_sid and call_sid in self.active_connections:
                del self.active_connections[call_sid]
    
    async def start_websocket_server(self, host: str = '0.0.0.0', port: int = 5001):
        """Start WebSocket server for Media Streams.
        
        Args:
            host: Host to bind to
            port: Port for WebSocket server
        """
        logger.info(f"Starting Media Streams WebSocket server on {host}:{port}")
        
        self.websocket_server = await websockets.serve(
            self.handle_media_stream,
            host,
            port
        )
        
        logger.info(f"WebSocket server running on ws://{host}:{port}")
        
        # Keep server running
        await asyncio.Future()  # Run forever
    
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
            call = self.twilio_client.calls.create(
                to=to_number,
                from_=from_number,
                url=webhook_url,
                status_callback=status_callback,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                method='POST'
            )
            
            logger.info(f"Call initiated: {call.sid} to {to_number}")
            return call.sid
            
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
        try:
            self.app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
        except Exception as e:
            raise


class AudioConverter:
    """Utilities for audio format conversion between Twilio and Gemini."""
    
    @staticmethod
    def mulaw_to_pcm(mulaw_data: bytes) -> bytes:
        """Convert μ-law audio to PCM.
        
        Args:
            mulaw_data: μ-law encoded audio
            
        Returns:
            PCM audio data
        """
        # TODO: Implement μ-law to PCM conversion
        # For now, returning as-is
        # May need audioop library: audioop.ulaw2lin(mulaw_data, 2)
        return mulaw_data
    
    @staticmethod
    def pcm_to_mulaw(pcm_data: bytes) -> bytes:
        """Convert PCM audio to μ-law.
        
        Args:
            pcm_data: PCM audio data
            
        Returns:
            μ-law encoded audio
        """
        # TODO: Implement PCM to μ-law conversion
        # For now, returning as-is
        # May need audioop library: audioop.lin2ulaw(pcm_data, 2)
        return pcm_data
    
    @staticmethod
    def resample_audio(audio_data: bytes, from_rate: int, to_rate: int) -> bytes:
        """Resample audio between different sample rates.
        
        Args:
            audio_data: Input audio
            from_rate: Source sample rate
            to_rate: Target sample rate
            
        Returns:
            Resampled audio
        """
        # TODO: Implement resampling using scipy or librosa
        # For now, returning as-is
        return audio_data

