"""
Day 6 Outbound Call Trigger Script for Tara (Learning & Literacy Track).

Places outbound practice calls to scheduled learners via:
1. LiveKit SIP Telephony (Twilio / Linphone SIP Trunking)
2. WebRTC Room Dispatch (Local/Dev testing mode)

Checks SQLite opt-out status before placing the call.
"""

import argparse
import asyncio
import logging
import os
import sys
import uuid

from dotenv import load_dotenv
from livekit import api

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import is_opted_out

load_dotenv(".env.local")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("outbound")


async def place_outbound_call(phone_number: str, user_id: str | None = None):
    user_id = user_id or phone_number.strip().lower()

    # 1. Opt-out check (Day 6 requirement)
    if is_opted_out(user_id):
        logger.warning(
            f"CANCELLED: Student '{user_id}' has opted out of daily outbound calls!"
        )
        print(
            f"\n[CANCELLED] Call to {phone_number} cancelled because student '{user_id}' is opted out."
        )
        return

    livekit_url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    sip_trunk_id = os.getenv("SIP_TRUNK_ID")

    if not all([livekit_url, api_key, api_secret]):
        logger.error(
            "Missing LIVEKIT_URL, LIVEKIT_API_KEY, or LIVEKIT_API_SECRET in .env.local"
        )
        return

    room_name = f"outbound-{uuid.uuid4().hex[:8]}"

    async with api.LiveKitAPI(
        url=livekit_url, api_key=api_key, api_secret=api_secret
    ) as lk:
        # Create outbound room with metadata
        logger.info(f"Creating outbound room '{room_name}'...")
        await lk.room.create_room(
            api.CreateRoomRequest(name=room_name, metadata='{"outbound": true}')
        )

        # Dispatch agent worker to the room
        agent_name = os.getenv("AGENT_NAME", "my-agent")
        try:
            logger.info(
                f"Dispatching agent worker '{agent_name}' to room '{room_name}'..."
            )
            await lk.agent_dispatch.create_dispatch(
                api.CreateAgentDispatchRequest(
                    agent_name=agent_name,
                    room=room_name,
                    metadata='{"outbound": true}',
                )
            )
        except Exception as e:
            logger.warning(f"Agent dispatch notice: {e}")

        if sip_trunk_id:
            # Real Telephony SIP Outbound Call (Twilio / Linphone)
            logger.info(
                f"Dialing phone number {phone_number} via SIP Trunk '{sip_trunk_id}'..."
            )
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
                    f"SIP Call initiated successfully! Participant ID: {participant.participant_id}"
                )
                print(
                    f"\n[SUCCESS] Outbound SIP Call placed to {phone_number} in room '{room_name}'!"
                )
            except Exception as e:
                logger.error(f"Failed to place SIP call: {e}")
                print(f"\n[ERROR] SIP Call error: {e}")
        else:
            # WebRTC / Development Testing Outbound Mode
            logger.info(
                "No SIP_TRUNK_ID found in .env.local. Creating WebRTC Outbound test session."
            )

            # Generate Token for participant to test in browser/Linphone
            token = (
                api.AccessToken(api_key, api_secret)
                .with_identity(f"user-{user_id}")
                .with_name(user_id)
                .with_grants(api.VideoGrants(room_join=True, room=room_name))
                .to_jwt()
            )

            print("\n" + "=" * 60)
            print(f"OUTBOUND PRACTICE CALL TRIGGERED FOR: {user_id}")
            print(f"Room Name: {room_name}")
            print(f"Phone Number: {phone_number}")
            print("Frontend URL to answer the call:")
            print(f"http://localhost:3000?room={room_name}&token={token}")
            print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Trigger an outbound practice call for Tara."
    )
    parser.add_argument(
        "--phone",
        type=str,
        default="+919876543210",
        help="Target phone number (e.g. +919876543210)",
    )
    parser.add_argument(
        "--user",
        type=str,
        default="rahul",
        help="Student user ID / name to check opt-out status",
    )
    args = parser.parse_args()

    asyncio.run(place_outbound_call(args.phone, args.user))
