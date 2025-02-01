import requests
import os
from typing import Optional

def generate_podcast(summary: str, output_filename: str = "output.mp3") -> Optional[str]:
    """
    Generate a podcast from text using ElevenLabs API.
    
    Args:
        summary (str): The text content to convert to speech
        output_filename (str): The desired output filename
        
    Returns:
        str: Path to the generated audio file if successful, None if failed
    """
    try:
        # ElevenLabs API Configuration
        ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_170668631500ba5f690d17b3e63a35470395613624c1501e")
        VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "m5qndnI7u4OAdXhH0Mr5")
        
        # API endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        
        # Request headers
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Request payload
        data = {
            "text": summary,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        # Make API request
        response = requests.post(url, json=data, headers=headers)
        
        # Check response status
        if response.status_code == 200:
            # Save the audio file
            with open(output_filename, "wb") as audio_file:
                audio_file.write(response.content)
            
            # Verify file was created
            if os.path.exists(output_filename):
                return output_filename
            else:
                raise Exception("Audio file not created after successful API response")
        else:
            error_message = response.json().get('detail', {}).get('message', 'Unknown error')
            raise Exception(f"ElevenLabs API error: {error_message}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(f"Podcast generation failed: {str(e)}")
