import os
import sys

# Ensure src directory is in Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from database import (
    _get_connection,
    create_escalation_request,
    get_open_escalations,
    get_escalation_by_id,
    sanitize_summary,
)


def test_sanitize_summary():
    """Verify private PII information (passwords, OTPs, card numbers) is sanitized."""
    raw = "User password=secret123 and OTP 482910 with card 1234-5678-9012-3456"
    sanitized = sanitize_summary(raw)
    assert "secret123" not in sanitized
    assert "[REDACTED]" in sanitized
    assert "1234-5678-9012-3456" not in sanitized


def test_create_escalation_with_consent():
    """Verify creating an escalation request when user consent is granted."""
    _get_connection()
    res = create_escalation_request(
        user_id="test_student",
        student_name="Test Student",
        reason="frustrated_learner",
        urgency="high",
        summary="Student is crying and struggling with basic words",
        user_consent=True,
    )

    assert res["ref_id"].startswith("ESC-")
    assert res["user_consent"] is True
    assert res["urgency"] == "high"
    assert res["status"] == "open"

    fetched = get_escalation_by_id(res["ref_id"])
    assert fetched is not None
    assert fetched["student_name"] == "Test Student"


def test_duplicate_escalation_prevention():
    """Verify duplicate open requests update the existing ticket instead of creating a duplicate."""
    _get_connection()
    res1 = create_escalation_request(
        user_id="dup_user",
        student_name="Dup User",
        reason="teacher_assistance_requested",
        urgency="medium",
        summary="First request for teacher callback",
        user_consent=True,
    )

    res2 = create_escalation_request(
        user_id="dup_user",
        student_name="Dup User",
        reason="teacher_assistance_requested",
        urgency="high",
        summary="Follow up call asking for urgent response",
        user_consent=True,
    )

    assert res2["is_duplicate_updated"] is True
    assert res2["ref_id"] == res1["ref_id"]
    assert "Follow-up update" in res2["summary"]
