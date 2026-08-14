import logging
import time

from dotenv import load_dotenv
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
)
from livekit.plugins import deepgram, google, murf, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from database import (
    create_escalation_request,
    delete_student,
    lookup_or_create_student,
    record_call_end,
    record_call_start,
    save_student,
    update_call_student,
)
from database import (
    opt_out_student as db_opt_out_student,
)
from maths_agent import MathsSpecialist
from prompt import SYSTEM_PROMPT
from tools import fetch_reading_exercise, lookup_word_meaning

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self, room_name: str = "anonymous") -> None:
        super().__init__(instructions=SYSTEM_PROMPT)
        self.room_name = room_name
        self.exercises_completed = 0
        self.was_opted_out = False
        self.identified_user = "anonymous"
        self.identified_name = "Learner"

    # ── Day 4 & Day 6: Memory & Opt-out tools ────────────────────────────

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
        self.identified_user = profile["user_id"]
        self.identified_name = profile["name"]
        update_call_student(self.room_name, self.identified_user, self.identified_name)

        if profile.get("opted_out"):
            return (
                f"STUDENT OPTED OUT! Name: {profile['name']}. "
                f"Inform them politely that they have opted out of automated calls."
            )

        topics = (
            ", ".join(profile["topics_covered"])
            if profile["topics_covered"]
            else "basic words and phonics practice"
        )
        mistakes = (
            ", ".join(profile["common_mistakes"])
            if profile["common_mistakes"]
            else "none"
        )

        if is_returning:
            return (
                f"RETURNING STUDENT FOUND IN DATABASE! "
                f"Name: {profile['name']}, Level: {profile['current_level']}, "
                f"Topics practiced last time: {topics}, Tricky words: {mistakes}. "
                f"Greet them warmly: 'नमस्ते! Welcome back {profile['name']}! "
                f"Last time we practiced {topics}.'"
            )
        return (
            f"NEW STUDENT REGISTERED! Name: {profile['name']}. "
            f"Greet them warmly for their very first session!"
        )

    @function_tool
    async def opt_out_student(self, context: RunContext, user_id: str):
        """Opt out a student from receiving daily outbound practice calls.
        Call this when the user says 'stop calling me', 'opt out', or 'un-subscribe'.

        Args:
            user_id: The student's name or ID.
        """
        logger.info(f"Opting out student from daily calls: {user_id}")
        self.was_opted_out = True
        success = db_opt_out_student(user_id.strip().lower())
        if success:
            return f"Success! {user_id} has been unsubscribed from all daily outbound calls."
        return f"Could not find an active subscription for {user_id}, but marked as opted out."

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
        Call this when the student asks for a new word, agrees to practice ('okay', 'yes', 'sure', 'haan'),
        says 'give me a word', 'let's practice', 'mujhe ek word do', or 'what should I read?'.

        Args:
            level: Student's reading level — 'beginner', 'intermediate', or 'advanced'.
            topic: Topic for the exercise, e.g. 'animals', 'fruits', 'colors', 'body', 'numbers', 'school', 'family', 'nature', 'science', 'environment'.
        """
        logger.info(f"Fetching exercise for level={level}, topic={topic}")
        exercise = await fetch_reading_exercise(level, topic)

        if exercise.get("error"):
            return (
                f"Sorry, I couldn't find an exercise right now. {exercise['message']}"
            )

        self.exercises_completed += 1

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

        Args:
            word: The English word to look up (e.g. 'cat', 'elephant', 'river', 'teacher').
        """
        logger.info(f"Looking up word meaning: {word}")
        result = await lookup_word_meaning(word)

        if result.get("error"):
            return result["message"]

        phonetic = f" (said as: {result['phonetic']})" if result.get("phonetic") else ""
        part = (
            f" It is a {result['part_of_speech']}."
            if result.get("part_of_speech")
            else ""
        )
        example = f" Example: {result['example']}" if result.get("example") else ""

        return (
            f"From the live dictionary ({result['fetched_at']}): "
            f"'{word}'{phonetic} means: {result['definition']}.{part}{example} "
            f"Source: {result['data_source']}."
        )

    # ── Day 7: Human Help & Escalation tool ──────────────────────────────

    @function_tool
    async def create_escalation(
        self,
        context: RunContext,
        user_id: str,
        student_name: str,
        reason: str,
        urgency: str = "medium",
        summary: str = "",
        user_consent: bool = True,
    ):
        """Create a human help request ticket for a student needing human assistance.
        ONLY call this after asking for explicit permission from the student and receiving consent.

        Args:
            user_id: Student ID or handle.
            student_name: Student display name.
            reason: Reason for human help ('frustrated_learner' or 'teacher_assistance_requested').
            urgency: Urgency level ('low', 'medium', 'high', or 'emergency').
            summary: Short summary (Who, What happened, What was checked, Urgency). NO passwords or PII!
            user_consent: True if student explicitly granted permission, False otherwise.
        """
        logger.info(
            f"Creating escalation for {student_name} ({user_id}) - Reason: {reason}, Consent: {user_consent}"
        )
        if not user_consent:
            return "Consent was NOT granted by the student. No human help request was created."

        result = create_escalation_request(
            user_id=user_id,
            student_name=student_name,
            reason=reason,
            urgency=urgency,
            summary=summary,
            user_consent=user_consent,
        )

        ref_id = result["ref_id"]
        if result.get("is_duplicate_updated"):
            return (
                f"Existing request updated! Reference ID: {ref_id}. "
                f"Inform the user: 'I updated your existing request ({ref_id}) for a VoiceForBharat teacher. "
                f"A teacher will review this within 24 to 48 hours. In the meantime, we can keep practicing!'"
            )

        return (
            f"Human help request created! Reference ID: {ref_id}. "
            f"Inform the user: 'I have submitted your request (Reference ID: {ref_id}) to the VoiceForBharat teacher support team. "
            f"A teacher will review it within 24 to 48 hours. In the meantime, we can continue practicing whenever you feel ready!'"
        )

    # ── Day 9: Specialist Agent Handoff tool ──────────────────────────────

    @function_tool
    async def transfer_to_maths_specialist(
        self,
        context: RunContext,
    ):
        """Transfer the student to Ganit, the Maths Practice Specialist.
        Call this tool when the student asks for:
        - Maths practice or numbers ("maths karo", "numbers practice", "can we do maths?")
        - Counting, addition, subtraction practice
        - Any arithmetic questions beyond what a reading buddy should handle

        Do NOT call this for reading, phonics, vocabulary, or pronunciation requests.
        Before calling this tool, say: 'मैं आपको Ganit से connect करती हूँ, our maths specialist! One moment!'
        """
        logger.info(
            f"Handing off to MathsSpecialist for student: {self.identified_name} ({self.identified_user})"
        )
        specialist = MathsSpecialist(
            student_name=self.identified_name,
            student_level="beginner",
        )
        await context.session.update_agent(specialist)
        return (
            f"HANDOFF COMPLETE. Student '{self.identified_name}' has been connected to Ganit, "
            f"the Maths Practice Specialist. Ganit will introduce themselves and start maths practice."
        )


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    start_time = time.time()
    room_name = ctx.room.name

    assistant = Assistant(room_name=room_name)

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(model="gemini-flash-lite-latest"),
        tts=murf.TTS(
            voice="en-IN-anisha",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=1),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    await ctx.connect()

    # Determine channel & direction
    has_sip = any(
        getattr(p, "kind", None) == "participant_kind_sip"
        for p in ctx.room.remote_participants.values()
    )
    channel = "sip" if has_sip else "browser"

    is_outbound = "outbound" in room_name.lower() or (
        ctx.room.metadata and "outbound" in ctx.room.metadata.lower()
    )
    direction = "outbound" if is_outbound else "inbound"

    # Record Call Start in SQLite
    record_call_start(
        call_id=room_name,
        user_id="anonymous",
        student_name="Learner",
        channel=channel,
        direction=direction,
    )

    # Register Shutdown Callback for Day 8 Call Analytics
    async def _on_shutdown():
        duration = int(time.time() - start_time)
        status = "success" if assistant.exercises_completed >= 1 else "failed"
        reason = (
            None
            if status == "success"
            else ("opted_out" if assistant.was_opted_out else "incomplete_task")
        )
        logger.info(
            f"Call finished [{room_name}] - Status: {status}, Exercises: {assistant.exercises_completed}, Duration: {duration}s"
        )
        record_call_end(
            call_id=room_name,
            status=status,
            failure_reason=reason,
            exercises_completed=assistant.exercises_completed,
            duration_seconds=duration,
        )

    ctx.add_shutdown_callback(_on_shutdown)

    await session.start(
        agent=assistant,
        room=ctx.room,
    )

    if is_outbound:
        # Mandatory Day 6 Outbound Call Opening (Who, Why, How to Opt Out)
        await session.say(
            "नमस्ते! This is Tara calling from VoiceForBharat Education. "
            "This is your scheduled daily 2-minute English reading practice call! "
            "If you don't want to receive these daily calls, just say 'stop calling me' or 'opt out'. "
            "What is your name so we can start today's practice?",
            allow_interruptions=True,
        )
    else:
        # Standard Inbound Opening
        await session.say(
            "नमस्ते! Hello! I am Tara, your reading buddy from VoiceForBharat. Tell me your name so I can look you up!",
            allow_interruptions=True,
        )


if __name__ == "__main__":
    cli.run_app(server)
