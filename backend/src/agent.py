import logging
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    function_tool,
    tokenize,
    room_io,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

from prompt import SYSTEM_PROMPT
from database import lookup_or_create_student, save_student, delete_student
from tools import fetch_reading_exercise, lookup_word_meaning


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)

    # ── Day 4: Memory tools ───────────────────────────────────────────────

    @function_tool
    async def lookup_student(
        self,
        context: RunContext,
        user_id: str,
    ):
        """Look up a student by their name in the database to check if they have visited before.
        ALWAYS call this tool as soon as the user tells you their name.

        Args:
            user_id: The student's name (used as their unique identifier).
        """
        logger.info(f"Looking up or creating student: {user_id}")
        profile, is_returning = lookup_or_create_student(user_id)

        topics = ", ".join(profile["topics_covered"]) if profile["topics_covered"] else "basic words and phonics practice"
        mistakes = ", ".join(profile["common_mistakes"]) if profile["common_mistakes"] else "none"

        if is_returning:
            return (
                f"RETURNING STUDENT FOUND IN DATABASE! "
                f"Name: {profile['name']}, Level: {profile['current_level']}, "
                f"Topics practiced last time: {topics}, Tricky words: {mistakes}. "
                f"Greet them warmly by name: 'Welcome back {profile['name']}! "
                f"Last time we practiced {topics}.'"
            )
        return (
            f"NEW STUDENT REGISTERED! Name: {profile['name']}. "
            f"Greet them warmly for their very first session!"
        )

    @function_tool
    async def save_student(
        self,
        context: RunContext,
        user_id: str,
        name: str,
        current_level: str,
        topics_covered: str,
        common_mistakes: str,
        language_preference: str = "hinglish",
    ):
        """Update a student's learning profile AFTER they give consent.

        Args:
            user_id: The student's unique identifier (their name in lowercase).
            name: The student's display name.
            current_level: beginner, intermediate, or advanced.
            topics_covered: Comma-separated list of topics practiced today.
            common_mistakes: Comma-separated list of words or sounds they struggle with.
            language_preference: hinglish, english, or hindi.
        """
        logger.info(f"Saving student profile: {user_id}")
        topics_list = [t.strip() for t in topics_covered.split(",") if t.strip()]
        mistakes_list = [m.strip() for m in common_mistakes.split(",") if m.strip()]
        result = save_student(
            user_id=user_id.strip().lower(),
            name=name,
            language_preference=language_preference,
            current_level=current_level,
            topics_covered=topics_list,
            common_mistakes=mistakes_list,
        )
        return (
            f"Saved! {result['name']} — Level: {result['current_level']}, "
            f"Topics: {', '.join(result['topics_covered'])}."
        )

    @function_tool
    async def forget_student(self, context: RunContext, user_id: str):
        """Delete a student's record when they explicitly ask to be forgotten.

        Args:
            user_id: The student's name or ID to delete.
        """
        logger.info(f"Deleting student record: {user_id}")
        deleted = delete_student(user_id.strip().lower())
        if deleted:
            return f"Done! All records for '{user_id}' have been deleted."
        return f"No record found for '{user_id}' to delete."

    # ── Day 5: Real data tools ────────────────────────────────────────────

    @function_tool
    async def get_reading_exercise(
        self,
        context: RunContext,
        level: str,
        topic: str,
    ):
        """Fetch a reading exercise (word + sentence) for the student to practice.
        Call this when the student asks for a new word to practice, wants an exercise,
        says 'give me a word', 'let's practice', 'mujhe ek word do', or 'what should I read?'.
        Data source: hand-built local dataset (no public API exists for Indian children's literacy exercises).

        Args:
            level: Student's reading level — 'beginner', 'intermediate', or 'advanced'.
            topic: Topic for the exercise, e.g. 'animals', 'fruits', 'colors', 'body', 'numbers', 'school', 'family', 'nature', 'science', 'environment'.
        """
        logger.info(f"Fetching exercise for level={level}, topic={topic}")
        exercise = await fetch_reading_exercise(level, topic)

        if exercise.get("error"):
            return f"Sorry, I couldn't find an exercise right now. {exercise['message']}"

        return (
            f"Exercise ready! "
            f"Word: '{exercise['word']}', "
            f"Sentence: '{exercise['sentence']}', "
            f"Spelling hint: {exercise['hint']}. "
            f"Topic: {exercise['topic']}, Level: {exercise['level']}. "
            f"Data from: {exercise['data_source']} (today, {exercise['fetched_at']}). "
            f"Now ask the student to say the word aloud and spell it out!"
        )

    @function_tool
    async def lookup_word_meaning(
        self,
        context: RunContext,
        word: str,
    ):
        """Look up the real meaning, pronunciation, and an example sentence for any English word
        using the live Free Dictionary API (dictionaryapi.dev).
        Call this when the student asks 'what does X mean?', 'what is X?', or is curious about a word's meaning.
        This tool uses LIVE internet data — always tell the student when the data was fetched.

        Args:
            word: The English word to look up (e.g. 'cat', 'elephant', 'river', 'teacher').
        """
        logger.info(f"Looking up word meaning: {word}")
        result = await lookup_word_meaning(word)

        if result.get("error"):
            # Graceful spoken fallback — never go silent
            return result["message"]

        phonetic = f" (said as: {result['phonetic']})" if result.get("phonetic") else ""
        part = f" It is a {result['part_of_speech']}." if result.get("part_of_speech") else ""
        example = f" Example: {result['example']}" if result.get("example") else ""

        return (
            f"From the live dictionary ({result['fetched_at']}): "
            f"'{word}'{phonetic} means: {result['definition']}.{part}{example} "
            f"Source: {result['data_source']}."
        )


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-IN-anisha",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=1),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=False,
    )

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    await ctx.connect()

    # Immediate initial greeting
    await session.say(
        "Hello! I am Tara, your reading buddy. Tell me your name so I can look you up!",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    cli.run_app(server)
