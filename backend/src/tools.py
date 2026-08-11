"""
Day 5 Tools for Tara — Learning & Literacy track.

Tool 1: fetch_reading_exercise  — hand-built local dataset (no public API available)
Tool 2: lookup_word_meaning     — calls the FREE Dictionary API (dictionaryapi.dev)
                                  Real internet data, no API key needed.
"""

import logging
from datetime import datetime, timezone

import httpx

from exercises import get_exercise

logger = logging.getLogger("agent.tools")

DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
DICT_TIMEOUT = 5.0  # seconds — graceful failure after this


async def fetch_reading_exercise(level: str, topic: str) -> dict:
    """
    Fetch a reading exercise from the hand-built local dataset.
    Returns a dict with: word, sentence, hint, level, topic, data_source.
    Falls back gracefully if level/topic is not found.
    """
    exercise = get_exercise(level, topic)
    if exercise is None:
        return {
            "error": True,
            "message": f"No exercise found for level '{level}' and topic '{topic}'. Try beginner + animals.",
        }

    exercise["data_source"] = "local curated dataset (hand-built)"
    exercise["fetched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return exercise


async def lookup_word_meaning(word: str) -> dict:
    """
    Look up the meaning, pronunciation, and an example sentence for a word
    using the Free Dictionary API (dictionaryapi.dev).
    Real-time internet data. No API key required.
    Falls back gracefully if the API is down or word is not found.
    """
    url = DICT_API.format(word=word.strip().lower())
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    try:
        async with httpx.AsyncClient(timeout=DICT_TIMEOUT) as client:
            response = await client.get(url)

        if response.status_code == 404:
            return {
                "error": True,
                "message": f"The word '{word}' was not found in the dictionary. Try a simpler word.",
            }

        if response.status_code != 200:
            return {
                "error": True,
                "message": f"Dictionary service returned an error (status {response.status_code}). Please try again in a moment.",
            }

        data = response.json()
        entry = data[0]
        phonetic = entry.get("phonetic", "")
        meanings = entry.get("meanings", [])

        if not meanings:
            return {
                "error": True,
                "message": f"No meanings found for '{word}'.",
            }

        first_meaning = meanings[0]
        part_of_speech = first_meaning.get("partOfSpeech", "")
        definitions = first_meaning.get("definitions", [])
        if not definitions:
            return {"error": True, "message": f"No definition found for '{word}'."}

        definition = definitions[0].get("definition", "")
        example = definitions[0].get("example", "")

        return {
            "word": word,
            "phonetic": phonetic,
            "part_of_speech": part_of_speech,
            "definition": definition,
            "example": example,
            "data_source": "Free Dictionary API (dictionaryapi.dev) — live internet data",
            "fetched_at": fetched_at,
        }

    except httpx.TimeoutException:
        return {
            "error": True,
            "message": (
                f"The dictionary took too long to respond for the word '{word}'. "
                "My internet is slow right now. Let me tell you what I know: "
                f"'{word}' is an English word. Try looking it up in your textbook!"
            ),
        }
    except Exception as exc:
        logger.error(f"Dictionary API error for '{word}': {exc}")
        return {
            "error": True,
            "message": (
                f"I couldn't reach the dictionary right now. "
                f"But don't worry — let's keep practicing the word '{word}' anyway!"
            ),
        }
