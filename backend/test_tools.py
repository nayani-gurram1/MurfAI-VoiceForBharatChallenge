import asyncio

from tools import fetch_reading_exercise, lookup_word_meaning


async def test():
    print("=== Exercise Tool (Local Dataset) ===")
    ex = await fetch_reading_exercise("beginner", "animals")
    print(ex)
    print()
    print("=== Dictionary Tool (Live Internet API) ===")
    meaning = await lookup_word_meaning("elephant")
    print(meaning)
    print()
    print("=== Graceful Failure Test ===")
    bad = await lookup_word_meaning("xyznonexistentword123")
    print(bad)


asyncio.run(test())
