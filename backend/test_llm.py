import asyncio

from dotenv import load_dotenv
from livekit.plugins import google

load_dotenv(".env.local")


async def test_llm():
    llm = google.LLM(model="gemini-2.5-flash")
    print(f"Gemini 2.5 flash initialized successfully: {llm}")
    llm_lite = google.LLM(model="gemini-flash-lite-latest")
    print(f"Gemini flash lite initialized successfully: {llm_lite}")


asyncio.run(test_llm())
