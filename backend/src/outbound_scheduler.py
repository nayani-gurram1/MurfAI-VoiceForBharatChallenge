"""
Day 6 Advanced — Outbound Call Scheduler with Outcome Handling.

Schedules daily English practice calls for enrolled students and handles
every telephony outcome that inbound calls never face:

  • NO_ANSWER  → retry up to 2 times (1 hour apart), then give up for the day
  • BUSY       → retry up to 3 times (15 minutes apart)
  • VOICEMAIL  → leave a pre-recorded audio drop, do not retry
  • HANGUP     → if call lasted < 5 s, flag as potential opt-out and retry once

Usage:
    # Call a single student right now
    uv run python src/outbound_scheduler.py --phone +919876543210 --user rahul

    # Run the daily scheduled batch (reads SCHEDULED_STUDENTS list)
    uv run python src/outbound_scheduler.py --batch
"""

import argparse
import asyncio
import logging
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from dotenv import load_dotenv
from livekit import api

# Add src directory to path so database can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import is_opted_out

load_dotenv(".env.local")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger("outbound_scheduler")


# ---------------------------------------------------------------------------
# Outcome definitions
# ---------------------------------------------------------------------------


class CallOutcome(str, Enum):
    """Possible telephony outcomes for an outbound call attempt."""

    ANSWERED = "ANSWERED"
    NO_ANSWER = "NO_ANSWER"
    BUSY = "BUSY"
    VOICEMAIL = "VOICEMAIL"
    HANGUP_IMMEDIATE = "HANGUP_IMMEDIATE"  # < 5 s call
    ERROR = "ERROR"


@dataclass
class RetryPolicy:
    max_retries: int
    delay_seconds: int
    action: str = "RETRY"  # RETRY | VOICEMAIL_DROP | FLAG_OPT_OUT | GIVE_UP


# ---------------------------------------------------------------------------
# Retry rules — one per outcome  (Day 6 Advanced Requirement)
# ---------------------------------------------------------------------------

RETRY_POLICIES: dict[CallOutcome, RetryPolicy] = {
    CallOutcome.NO_ANSWER: RetryPolicy(
        max_retries=2,
        delay_seconds=3600,  # 1 hour
        action="RETRY",
    ),
    CallOutcome.BUSY: RetryPolicy(
        max_retries=3,
        delay_seconds=900,  # 15 minutes
        action="RETRY",
    ),
    CallOutcome.VOICEMAIL: RetryPolicy(
        max_retries=0,
        delay_seconds=0,
        action="VOICEMAIL_DROP",  # Leave pre-recorded message
    ),
    CallOutcome.HANGUP_IMMEDIATE: RetryPolicy(
        max_retries=1,
        delay_seconds=1800,  # 30 minutes
        action="FLAG_OPT_OUT",  # Flag for potential opt-out + one retry
    ),
    CallOutcome.ERROR: RetryPolicy(
        max_retries=1,
        delay_seconds=300,  # 5 minutes
        action="RETRY",
    ),
}


# ---------------------------------------------------------------------------
# Scheduled students list (hard-coded for Day 6 demo; swap for DB read)
# ---------------------------------------------------------------------------

SCHEDULED_STUDENTS = [
    {"user_id": "rahul", "phone": "+919876543210"},
    {"user_id": "priya", "phone": "+919123456789"},
    # Add more enrolled learners here
]


# ---------------------------------------------------------------------------
# Core: place one SIP outbound call
# ---------------------------------------------------------------------------


async def _place_sip_call(
    lk: api.LiveKitAPI,
    phone_number: str,
    user_id: str,
    room_name: str,
    sip_trunk_id: str,
) -> tuple[CallOutcome, str]:
    """
    Dials out over SIP and returns (CallOutcome, participant_id | error_msg).
    In a real deployment you would hook into LiveKit webhook events to detect
    NO_ANSWER / BUSY / VOICEMAIL via call status callbacks.
    For the Day 6 demo we treat a successful API call as ANSWERED.
    """
    from datetime import timedelta

    sip_request = api.CreateSIPParticipantRequest(
        sip_trunk_id=sip_trunk_id,
        sip_call_to=phone_number,
        room_name=room_name,
        participant_identity=f"phone-{phone_number}",
        participant_name=user_id,
        play_ringtone=True,
        wait_until_answered=True,
        max_call_duration=timedelta(seconds=300),
        media_encryption=api.SIP_MEDIA_ENCRYPT_DISABLE,
    )
    try:
        participant = await lk.sip.create_sip_participant(sip_request)
        logger.info(
            "SIP call initiated — participant_id=%s", participant.participant_id
        )
        return CallOutcome.ANSWERED, participant.participant_id
    except Exception as exc:
        err = str(exc)
        logger.error("SIP call failed: %s", err)
        # Map common SIP error strings to structured outcomes
        if "busy" in err.lower():
            return CallOutcome.BUSY, err
        if "no answer" in err.lower() or "timeout" in err.lower():
            return CallOutcome.NO_ANSWER, err
        if "voicemail" in err.lower():
            return CallOutcome.VOICEMAIL, err
        return CallOutcome.ERROR, err


async def _dev_webrtc_session(
    lk: api.LiveKitAPI,
    phone_number: str,
    user_id: str,
    room_name: str,
    api_key: str,
    api_secret: str,
) -> tuple[CallOutcome, str]:
    """WebRTC dev-mode fallback — prints a browser answer link."""
    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity(f"user-{user_id}")
        .with_name(user_id)
        .with_grants(api.VideoGrants(room_join=True, room=room_name))
        .to_jwt()
    )
    url = f"http://localhost:3000?room={room_name}&token={token}"
    print("\n" + "=" * 64)
    print(f"  OUTBOUND PRACTICE CALL  >  {user_id} ({phone_number})")
    print(f"  Room: {room_name}")
    print(f"  Answer in browser: {url}")
    print("=" * 64 + "\n")
    return CallOutcome.ANSWERED, url


# ---------------------------------------------------------------------------
# Outcome handler
# ---------------------------------------------------------------------------


async def _handle_outcome(
    outcome: CallOutcome, user_id: str, phone_number: str, attempt: int
) -> None:
    """Log and act on each telephony outcome."""
    policy = RETRY_POLICIES.get(outcome)

    if outcome == CallOutcome.ANSWERED:
        logger.info(
            "✅  ANSWERED  — %s (%s) — session handed to agent",
            user_id,
            phone_number,
        )

    elif outcome == CallOutcome.NO_ANSWER:
        if attempt <= (policy.max_retries if policy else 0):
            logger.warning(
                "📵  NO_ANSWER  — %s — attempt %d/%d — retrying in %ds",
                user_id,
                attempt,
                policy.max_retries,
                policy.delay_seconds,
            )
            await asyncio.sleep(policy.delay_seconds)
            await place_outbound_call(phone_number, user_id, attempt=attempt + 1)
        else:
            logger.warning(
                "📵  NO_ANSWER  — %s — max retries reached, giving up for today",
                user_id,
            )

    elif outcome == CallOutcome.BUSY:
        if attempt <= (policy.max_retries if policy else 0):
            logger.warning(
                "📞  BUSY  — %s — retrying in %ds (attempt %d/%d)",
                user_id,
                policy.delay_seconds,
                attempt,
                policy.max_retries,
            )
            await asyncio.sleep(policy.delay_seconds)
            await place_outbound_call(phone_number, user_id, attempt=attempt + 1)
        else:
            logger.warning("📞  BUSY  — %s — max retries reached", user_id)

    elif outcome == CallOutcome.VOICEMAIL:
        logger.info("📼  VOICEMAIL  — %s — leaving audio drop message", user_id)
        # In a real system: play a pre-recorded WAV drop via SIP REFER
        print(
            f"[VOICEMAIL DROP] Leaving message for {user_id}: "
            "'\u0928\u092e\u0938\u094d\u0924\u0947! This is Tara from VoiceForBharat Education. "
            "We tried to reach you for your daily English practice. "
            "Call us back or we will try again tomorrow. "
            "To opt out, reply STOP to this number.'"
        )

    elif outcome == CallOutcome.HANGUP_IMMEDIATE:
        logger.warning(
            "⚡  IMMEDIATE HANGUP  — %s — flagging as potential opt-out", user_id
        )
        print(
            f"[FLAG] {user_id} hung up immediately. "
            "After confirmation, will be marked for opt-out review."
        )
        if attempt == 1:
            logger.info("Retrying once in 30 minutes...")
            await asyncio.sleep(policy.delay_seconds)
            await place_outbound_call(phone_number, user_id, attempt=2)

    elif outcome == CallOutcome.ERROR:
        logger.error("❌  ERROR  — %s — %s", user_id, phone_number)
        if attempt <= (policy.max_retries if policy else 0):
            await asyncio.sleep(policy.delay_seconds)
            await place_outbound_call(phone_number, user_id, attempt=attempt + 1)


# ---------------------------------------------------------------------------
# Main entrypoint: place_outbound_call
# ---------------------------------------------------------------------------


async def place_outbound_call(
    phone_number: str,
    user_id: str | None = None,
    attempt: int = 1,
) -> None:
    """Place an outbound practice call with full outcome handling."""
    user_id = (user_id or phone_number).strip().lower()

    # ── Pre-flight: honour opt-out list ──────────────────────────────────────
    if is_opted_out(user_id):
        logger.warning("CANCELLED: '%s' is opted out — skipping outbound call", user_id)
        print(f"\n[CANCELLED] {phone_number} — student '{user_id}' is opted out.")
        return

    logger.info(
        "Placing outbound call to %s (user=%s, attempt=%d)",
        phone_number,
        user_id,
        attempt,
    )

    livekit_url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    sip_trunk_id = os.getenv("SIP_TRUNK_ID")

    if not all([livekit_url, api_key, api_secret]):
        logger.error("Missing LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET")
        return

    room_name = f"outbound-{uuid.uuid4().hex[:8]}"

    async with api.LiveKitAPI(
        url=livekit_url, api_key=api_key, api_secret=api_secret
    ) as lk:
        # Create room with outbound metadata so agent.py knows the call type
        await lk.room.create_room(
            api.CreateRoomRequest(name=room_name, metadata='{"outbound": true}')
        )

        # Dispatch agent worker explicitly
        agent_name = os.getenv("AGENT_NAME", "my-agent")
        try:
            await lk.agent_dispatch.create_dispatch(
                api.CreateAgentDispatchRequest(
                    agent_name=agent_name,
                    room=room_name,
                    metadata='{"outbound": true}',
                )
            )
        except Exception as e:
            logger.warning("Agent dispatch notice: %s", e)

        if sip_trunk_id:
            outcome, _detail = await _place_sip_call(
                lk, phone_number, user_id, room_name, sip_trunk_id
            )
        else:
            outcome, _detail = await _dev_webrtc_session(
                lk, phone_number, user_id, room_name, api_key, api_secret
            )

    # Dispatch outcome handler (handles retries automatically)
    await _handle_outcome(outcome, user_id, phone_number, attempt)


# ---------------------------------------------------------------------------
# Batch scheduler: calls every enrolled student
# ---------------------------------------------------------------------------


async def run_daily_batch() -> None:
    """Run scheduled calls for all enrolled, non-opted-out students."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    logger.info("=== Daily outbound batch started at %s ===", now)
    logger.info("Scheduled students: %d", len(SCHEDULED_STUDENTS))

    tasks = [place_outbound_call(s["phone"], s["user_id"]) for s in SCHEDULED_STUDENTS]
    await asyncio.gather(*tasks, return_exceptions=True)

    logger.info("=== Daily outbound batch completed ===")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tara Outbound Scheduler — place daily English practice calls."
    )
    parser.add_argument(
        "--phone",
        type=str,
        default="+919876543210",
        help="Phone number to call (E.164 format, e.g. +919876543210)",
    )
    parser.add_argument(
        "--user",
        type=str,
        default="rahul",
        help="Student user ID / name for opt-out lookup",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run the full daily scheduled batch for all enrolled students",
    )
    args = parser.parse_args()

    if args.batch:
        asyncio.run(run_daily_batch())
    else:
        asyncio.run(place_outbound_call(args.phone, args.user))
