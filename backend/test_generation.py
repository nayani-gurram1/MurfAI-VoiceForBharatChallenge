import asyncio

from dotenv import load_dotenv
from livekit.agents import llm as llm_module
from livekit.plugins import google

load_dotenv(".env.local")


async def main():
    try:
        print("Testing Google LLM generation...")
        llm = google.LLM(model="gemini-flash-lite-latest")
        chat_ctx = llm_module.ChatContext()
        chat_ctx.append(text="Say hello!", role="user")

        stream = llm.chat(chat_ctx=chat_ctx)

        print("Response: ", end="")
        async for chunk in stream:
            print(chunk.choices[0].delta.content or "", end="")
        print("\nLLM test complete.")

    except Exception as e:
        print(f"\nLLM Error during generation: {e}")


if __name__ == "__main__":
    asyncio.run(main())
