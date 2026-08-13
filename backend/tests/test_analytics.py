import os
import sys
import pytest

# Add src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from database import (
    _get_connection,
    record_call_start,
    update_call_student,
    record_call_end,
    get_call_analytics,
)


@pytest.fixture(autouse=True)
def setup_db():
    conn = _get_connection()
    conn.close()


def test_call_analytics_recording():
    # Record a successful call
    call_id_1 = "test-call-succ-001"
    record_call_start(call_id_1, user_id="anita", student_name="Anita", channel="browser", direction="outbound")
    update_call_student(call_id_1, user_id="anita", student_name="Anita")
    end_res_1 = record_call_end(call_id_1, status="success", failure_reason=None, exercises_completed=2, duration_seconds=60)

    assert end_res_1["status"] == "success"
    assert end_res_1["exercises_completed"] == 2

    # Record a failed call
    call_id_2 = "test-call-fail-002"
    record_call_start(call_id_2, user_id="vikram", student_name="Vikram", channel="sip", direction="inbound")
    end_res_2 = record_call_end(call_id_2, status="failed", failure_reason="incomplete_task", exercises_completed=0, duration_seconds=15)

    assert end_res_2["status"] == "failed"
    assert end_res_2["failure_reason"] == "incomplete_task"

    # Compute analytics
    analytics = get_call_analytics()

    assert analytics["total_calls"] >= 2
    assert analytics["successful_calls"] >= 1
    assert analytics["failed_calls"] >= 1
    assert analytics["success_rate_percent"] >= 0.0
    assert len(analytics["recent_calls"]) >= 2
