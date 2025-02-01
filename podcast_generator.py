import os
import requests
from typing import Optional, Tuple, Dict
import streamlit as st
from pathlib import Path
import json

class CyberPodcastGenerator:
    """
    A cyberpunk-themed podcast generator using ElevenLabs API.
    Includes enhanced error handling and rate limit detection.
    """
    
    def __init__(self):
        self.ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_92500cf9f7ff2cc0b71f41588509df08730001b51d6e47e7")
        self.VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "m5qndnI7u4OAdXhH0Mr5")
        self.API_BASE_URL = "https://api.elevenlabs.io/v1"
        
    def _get_headers(self) -> Dict[str, str]:
        """Generate headers for API requests."""
        return {
            "xi-api-key": self.ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
    
    def _check_api_quota(self) -> Tuple[bool, str]:
        """
        Check API quota status before making synthesis request.
        Returns (is_quota_available, message)
        """
        try:
            url = f"{self.API_BASE_URL}/user/subscription"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if character quota is exceeded
                if 'character_count' in data and 'character_limit' in data:
                    remaining = data['character_limit'] - data['character_count']
                    if remaining <= 0:
                        return False, "Character quota exceeded. Please upgrade your ElevenLabs subscription."
                
                return True, "Quota available"
            else:
                return False, "Unable to verify API quota status"
                
        except Exception as e:
            return False, f"Error checking API quota: {str(e)}"
    
    def _prepare_voice_settings(self) -> Dict:
        """Configure voice settings for the podcast."""
        return {
            "stability": 0.75,
            "similarity_boost": 0.75,
            "style": 0.5,
            "use_speaker_boost": True
        }
    
    def _format_text_for_podcast(self, summaries: Dict[str, str]) -> str:
        """Format the text content for podcast narration."""
        formatted_text = []
        
        # Add intro
        formatted_text.append("Initializing Neural Audio Interface...")
        formatted_text.append("Welcome to your Quantum Research Synopsis.")
        
        # Process each section with character count monitoring
        total_chars = 0
        for section, content in summaries.items():
            section_text = f"Section: {section}\n\n{content}\n\nNeural Processing Complete."
            total_chars += len(section_text)
            
            # Check if we're approaching free tier limits (approx 2500 chars)
            if total_chars > 2000:
                formatted_text.append("Content truncated to respect free tier limitations.")
                break
                
            formatted_text.append(section_text)
        
        # Add outro
        formatted_text.append("Terminating Quantum Audio Stream. Thank you for accessing this neural interface.")
        
        return "\n\n".join(formatted_text)
    
    def _handle_api_error(self, response: requests.Response) -> str:
        """Handle API errors and provide user-friendly messages."""
        try:
            error_data = response.json()
            if 'detail' in error_data:
                if 'Free Tier' in str(error_data['detail']):
                    return """
                    Free tier usage limit reached. To continue using the service:
                    1. Upgrade to a paid ElevenLabs subscription
                    2. Update your API key in the environment variables
                    3. Try again with a smaller text input
                    """
                return str(error_data['detail'])
            return f"API Error: Status code {response.status_code}"
        except:
            return f"Unexpected API error: Status code {response.status_code}"
    
    def generate_podcast(self, summaries: Dict[str, str], progress_callback=None) -> Optional[str]:
        """
        Generate a podcast from the provided summaries with enhanced error handling.
        
        Args:
            summaries: Dictionary of section summaries
            progress_callback: Optional callback for progress updates
        
        Returns:
            str: Path to the generated audio file
        """
        try:
            if progress_callback:
                progress_callback("CHECKING NEURAL INTERFACE STATUS...", 10)
            
            # Check API quota before proceeding
            quota_available, quota_message = self._check_api_quota()
            if not quota_available:
                raise Exception(f"API Quota Check Failed: {quota_message}")
            
            if progress_callback:
                progress_callback("INITIALIZING NEURAL AUDIO SYNTHESIS...", 20)
            
            # Prepare the content
            formatted_text = self._format_text_for_podcast(summaries)
            
            # Configure the API request
            url = f"{self.API_BASE_URL}/text-to-speech/{self.VOICE_ID}"
            data = {
                "text": formatted_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": self._prepare_voice_settings()
            }
            
            if progress_callback:
                progress_callback("ENGAGING QUANTUM VOICE SYNTHESIS...", 40)
            
            # Make API request
            response = requests.post(url, json=data, headers=self._get_headers())
            
            if response.status_code != 200:
                error_message = self._handle_api_error(response)
                raise Exception(error_message)
            
            if progress_callback:
                progress_callback("STABILIZING NEURAL WAVEFORMS...", 60)
            
            # Generate output filename
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_filename = output_dir / "quantum_synopsis.mp3"
            
            # Save the audio file
            with open(output_filename, "wb") as audio_file:
                audio_file.write(response.content)
            
            if progress_callback:
                progress_callback("FINALIZING QUANTUM AUDIO STREAM...", 80)
            
            # Verify file creation
            if not output_filename.exists():
                raise Exception("Neural Audio Synthesis Failed: Output not detected")
            
            return str(output_filename)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Quantum Network Disruption: {str(e)}")
        except Exception as e:
            raise Exception(f"Neural Audio Synthesis Failed: {str(e)}")

def generate_podcast(summaries: Dict[str, str]) -> Optional[str]:
    """
    Main interface function to generate podcast from summaries.
    Matches the interface expected by the Streamlit app.
    """
    generator = CyberPodcastGenerator()
    
    def progress_update(message: str, progress: int):
        st.markdown(f"🎙️ {message}")
        if 'progress' in st.session_state:
            st.session_state.progress.progress(progress)
    
    return generator.generate_podcast(summaries, progress_callback=progress_update)
