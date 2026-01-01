"""Speech processing: Text-to-Speech using ElevenLabs with macOS fallback."""
import subprocess
import os
import logging
import tempfile
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)

# Try to import ElevenLabs client
try:
    from elevenlabs_client import ElevenLabsClient
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    ElevenLabsClient = None


class SpeechHandler:
    """Handles text-to-speech conversion using ElevenLabs with macOS fallback."""
    
    def __init__(self, elevenlabs_client: ElevenLabsClient = None, temp_dir: str = None):
        """Initialize speech handler.
        
        Args:
            elevenlabs_client: Optional ElevenLabs client instance
            temp_dir: Directory for temporary audio files
        """
        self.elevenlabs_client = elevenlabs_client
        self.temp_dir = Path(temp_dir or Config.AUDIO_TEMP_DIR)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.audio_format = Config.AUDIO_FORMAT
    
    def text_to_speech(self, text: str, output_path: str = None) -> str:
        """Convert text to speech using ElevenLabs with macOS say command as fallback.
        
        Args:
            text: Text to convert to speech
            output_path: Optional path for output file. If None, creates temp file.
        
        Returns:
            Path to the generated audio file
        """
        if output_path is None:
            # Create temporary file (always .wav as our final target)
            temp_file = tempfile.NamedTemporaryFile(
                suffix=f'.{self.audio_format}',
                dir=self.temp_dir,
                delete=False
            )
            final_output_path = temp_file.name
            temp_file.close()
        else:
            final_output_path = str(output_path)
        
        # Try ElevenLabs first
        if self.elevenlabs_client:
            # Use .mp3 for ElevenLabs temp file
            mp3_temp = final_output_path.replace(f'.{self.audio_format}', '.mp3')
            try:
                success = self.elevenlabs_client.generate_speech(text, mp3_temp)
                if success:
                    # Convert MP3 to WAV for Twilio
                    self._convert_to_wav(mp3_temp, final_output_path)
                    # Clean up MP3
                    if os.path.exists(mp3_temp):
                        os.remove(mp3_temp)
                    logger.info("ElevenLabs TTS succeeded")
                    return final_output_path
            except Exception as e:
                logger.warning(f"ElevenLabs TTS failed: {e}. Falling back to 'say'...")
                if os.path.exists(mp3_temp):
                    os.remove(mp3_temp)
        
        # Fallback to macOS 'say' command
        return self._text_to_speech_say(text, final_output_path)

    def _text_to_speech_say(self, text: str, final_output_path: str) -> str:
        """Fallback TTS using macOS 'say' command."""
        # Create a temp .aiff file for 'say' command
        aiff_path = final_output_path.replace(f'.{self.audio_format}', '.aiff')
        
        try:
            # Use macOS say command to generate AIFF audio
            subprocess.run(
                ['say', '-v', 'Samantha', '-o', aiff_path, text],
                check=True,
                capture_output=True,
                timeout=30
            )
            
            # Convert AIFF to WAV format for Twilio compatibility
            self._convert_to_wav(aiff_path, final_output_path)
            
            # Clean up AIFF file
            if os.path.exists(aiff_path):
                os.remove(aiff_path)
            
            logger.info("macOS 'say' TTS succeeded")
            return final_output_path
            
        except subprocess.TimeoutExpired:
            logger.error("say command timed out")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"say command failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in _text_to_speech_say: {e}")
            raise
    
    def _convert_to_wav(self, input_path: str, output_path: str):
        """Convert audio file to WAV format using afconvert.
        
        Args:
            input_path: Path to input audio file
            output_path: Path to output WAV file
        """
        try:
            # Use afconvert (macOS built-in) to convert to WAV
            # -f WAVE specifies WAV format
            # -d LEI16 specifies 16-bit little-endian integer
            subprocess.run(
                ['afconvert', '-f', 'WAVE', '-d', 'LEI16', input_path, output_path],
                check=True,
                capture_output=True,
                timeout=10
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"afconvert failed: {e}")
            # Try alternative: use ffmpeg if available
            try:
                subprocess.run(
                    ['ffmpeg', '-i', input_path, '-y', output_path],
                    check=True,
                    capture_output=True,
                    timeout=10
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error("Both afconvert and ffmpeg failed")
                raise
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files."""
        try:
            for file in self.temp_dir.glob('*'):
                if file.is_file():
                    file.unlink()
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {e}")
