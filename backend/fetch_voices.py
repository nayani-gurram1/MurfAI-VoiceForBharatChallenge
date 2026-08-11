import os

import requests
from dotenv import load_dotenv

load_dotenv(".env.local")

api_key = os.getenv("MURF_API_KEY")
url = "https://api.murf.ai/v1/speech/voices?model=FALCON"

headers = {"api-key": api_key, "Accept": "application/json"}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    voices = response.json()
    # The API might return a dict like {"voices": [...]} or a flat list.
    if isinstance(voices, dict) and "voices" in voices:
        voice_list = voices["voices"]
    else:
        voice_list = voices

    print(f"Total voices: {len(voice_list)}")
    if len(voice_list) > 0:
        print("First voice structure:")
        print(voice_list[0])

    print("\nIndian Voices:")
    for v in voice_list:
        if isinstance(v, dict) and any(
            isinstance(val, str) and "IN" in val.upper() for val in v.values()
        ):
            print(
                f"ID: {v.get('voiceId') or v.get('voice_id')}, Name: {v.get('displayName') or v.get('name')}, Locale: {v.get('locale')}"
            )
else:
    print(f"Failed to fetch voices: {response.text}")
