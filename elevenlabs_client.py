import requests
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class ElevenLabsClient:
    """Client for ElevenLabs Text-to-Speech API."""
    
    def __init__(self, api_key: str, voice_id: str = "EXAVIT9mxAsU4AKpD7Kx", model_id: str = "eleven_turbo_v2_5"):
        """Initialize ElevenLabs client.
        
        Args:
            api_key: ElevenLabs API key
            voice_id: ID of the voice to use (default: Bella)
            model_id: ID of the model to use (default: turbo v2.5)
        """
        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.base_url = "https://api.elevenlabs.io/v1"
        
    def generate_speech(self, text: str, output_path: str) -> bool:
        """Generate speech from text and save to file.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            logger.warning("ElevenLabs API key not provided")
            return False
            
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                return True
            else:
                logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error calling ElevenLabs API: {e}")
            return False

