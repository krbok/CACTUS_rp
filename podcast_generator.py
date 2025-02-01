# from gtts import gTTS
# import os

# def generate_podcast(summary, output_filename="output.mp3"):
#     try:
#         # Convert text to speech
#         tts = gTTS(text=summary, lang="en", slow=False)
#         tts.save(output_filename)

#         # Validate if file is created
#         if os.path.exists(output_filename):
#             return output_filename
#         else:
#             raise Exception("⚠️ Audio file generation failed.")

#     except Exception as e:
#         return f"❌ Podcast generation failed: {e}"

# # Example Usage
# if __name__ == "__main__":
#     test_summary = "This is a test podcast generation using gTTS."
#     result = generate_podcast(test_summary)
#     print("Generated Podcast:", result)


import requests

# Replace these values with your actual API key and Voice ID
API_KEY = "your-elevenlabs-api-key"  # Your ElevenLabs API key
VOICE_ID = "m5qndnI7u4OAdXhH0Mr5"  # Your generated Voice ID

# Set the URL for the ElevenLabs Text-to-Speech API
url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

# Set the request headers
headers = {
    "xi-api-key": "sk_c581842e50a2c5902a7748398952455e22c0c5e4058d3ac1",
    "Content-Type": "application/json"
}

# Set the text you want to convert to speech
data = {
    
    "model_id": "eleven_multilingual_v2"  # Change if you have a different model ID
}

# Send the request to ElevenLabs API
response = requests.post(url, json=data, headers=headers)

# Check the response status
if response.status_code == 200:
    # Save the audio content to an MP3 file
    with open("output.mp3", "wb") as f:
        f.write(response.content)
    print("Audio saved as output.mp3")
else:
    print(f"Error: {response.json()}")