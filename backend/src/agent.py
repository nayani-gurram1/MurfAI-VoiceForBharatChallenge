import logging
from typing import Optional

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
    inference,
    tokenize,
    room_io,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

from prompt import SYSTEM_PROMPT
from database import lookup_or_create_student, save_student, delete_student


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)

    @function_tool
    async def lookup_student(
        self,
        context: RunContext,
        user_id: str,
    ):
        """Look up a student by their name or ID in the database.
        If they are a new student, automatically saves their new record in SQLite!
        ALWAYS call this tool as soon as the user tells you their name.

        Args:
            user_id: The student's name (used as their unique identifier).
        """
        logger.info(f"Looking up or creating student: {user_id}")
        profile, is_returning = lookup_or_create_student(user_id)

        topics = ", ".join(profile["topics_covered"]) if profile["topics_covered"] else "basic words"
        mistakes = ", ".join(profile["common_mistakes"]) if profile["common_mistakes"] else "none"

        if is_returning:
            return (
                f"RETURNING STUDENT FOUND IN DATABASE! "
                f"Name: {profile['name']}, "
                f"Level: {profile['current_level']}, "
                f"Topics practiced last time: {topics}, "
                f"Tricky words: {mistakes}. "
                f"Greet them back warmly by name: 'Welcome back {profile['name']}! Last time we practiced {topics}. Shall we continue?'"
            )
        else:
            return (
                f"NEW STUDENT REGISTERED AND SAVED TO DATABASE! "
                f"Name: {profile['name']}. "
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
            current_level: The student's reading level (beginner, intermediate, advanced).
            topics_covered: Comma-separated list of topics practiced.
            common_mistakes: Comma-separated list of words or sounds they struggle with.
            language_preference: The student's preferred language mix.
        """
        logger.info(f"Updating student profile: {user_id}")

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
            f"Student profile updated in SQLite for {result['name']}! "
            f"Level: {result['current_level']}, "
            f"Topics: {', '.join(result['topics_covered'])}."
        )

    @function_tool
    async def forget_student(
        self,
        context: RunContext,
        user_id: str,
    ):
        """Delete a student's record when they ask to be forgotten.

        Args:
            user_id: The student's name or ID to delete.
        """
        logger.info(f"Deleting student record: {user_id}")
        deleted = delete_student(user_id.strip().lower())

        if deleted:
            return f"Done! I have completely deleted all records for '{user_id}' from SQLite."
        else:
            return f"No record found for '{user_id}' to delete."


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(
            model="gemini-flash-lite-latest",
        ),
        tts=murf.TTS(
            voice="en-IN-anisha",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
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
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    await ctx.connect()

    agent_greeting = (
        "Hello! I am Tara, your reading buddy. "
        "What is your name? Tell me your name so I can look you up!"
    )
    logger.info(f"Saying greeting: {agent_greeting}")
    await session.say(agent_greeting, allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(server)
