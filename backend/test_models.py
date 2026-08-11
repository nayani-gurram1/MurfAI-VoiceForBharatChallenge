import asyncio

from dotenv import load_dotenv
from livekit.agents import llm as llm_module
from livekit.plugins import google

load_dotenv(".env.local")

MODELS_TO_TEST = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-2.0-pro-exp",
    "gemini-3.5-flash-lite",
    "gemini-2.5-pro",
]


async def _check_model(model_name):
    try:
        llm = google.LLM(model=model_name)
        chat_ctx = llm_module.ChatContext()
        chat_ctx.add_message(role="user", content="Hi")
        stream = llm.chat(chat_ctx=chat_ctx)

        async for _chunk in stream:
            pass  # Just consume to see if it errors

        print(f"[SUCCESS] {model_name} works!")
        return model_name
    except Exception as e:
        err_str = str(e)
        if "404" in err_str or "Not Found" in err_str:
            print(f"[FAILED] {model_name}: 404 Not Found")
        elif "429" in err_str or "Too Many Requests" in err_str:
            print(f"[FAILED] {model_name}: 429 Quota Exceeded")
        else:
            print(f"[FAILED] {model_name}: {err_str}")
    return None


async def main():
    working_models = []
    print("Testing models...")
    for model in MODELS_TO_TEST:
        res = await _check_model(model)
        if res:
            working_models.append(res)

    print("\n--- RESULTS ---")
    if working_models:
        print(f"Working models: {working_models}")
    else:
        print("NO MODELS WORKING (ALL RATE LIMITED OR NOT FOUND)")


if __name__ == "__main__":
    asyncio.run(main())
