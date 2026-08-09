import asyncio
from dotenv import load_dotenv
from livekit.plugins import google

load_dotenv(".env.local")

async def test_llm():
    llm = google.LLM(model="gemini-2.5-flash")
    print("Gemini 2.5 flash initialized successfully!")
    llm_lite = google.LLM(model="gemini-flash-lite-latest")
    print("Gemini flash lite initialized successfully!")

asyncio.run(test_llm())
