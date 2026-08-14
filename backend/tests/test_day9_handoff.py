"""
Day 9 – Unit tests for MathsSpecialist agent handoff.
Tests problem generation, answer checking, and handback-to-Tara tool.
No live LiveKit connection needed (tests tool logic only).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from unittest.mock import AsyncMock, MagicMock


# ── Helpers ──────────────────────────────────────────────────────────────

def make_context():
    """Build a minimal fake RunContext with a session stub."""
    ctx = MagicMock()
    ctx.session = MagicMock()
    ctx.session.update_agent = AsyncMock()
    return ctx


# ── MathsSpecialist tests ─────────────────────────────────────────────────

class TestMathsSpecialist:
    def setup_method(self):
        from maths_agent import MathsSpecialist
        self.agent = MathsSpecialist(student_name="Nayani", student_level="beginner")

    @pytest.mark.asyncio
    async def test_give_maths_problem_addition(self):
        ctx = make_context()
        result = await self.agent.give_maths_problem(ctx, level="beginner", operation="addition")
        assert "Addition problem" in result
        assert "plus" in result
        assert self.agent.problems_attempted == 1

    @pytest.mark.asyncio
    async def test_give_maths_problem_subtraction(self):
        ctx = make_context()
        result = await self.agent.give_maths_problem(ctx, level="beginner", operation="subtraction")
        assert "Subtraction problem" in result
        assert "minus" in result
        assert self.agent.problems_attempted == 1

    @pytest.mark.asyncio
    async def test_give_maths_problem_counting(self):
        ctx = make_context()
        result = await self.agent.give_maths_problem(ctx, level="beginner", operation="counting")
        assert "?" in result
        assert self.agent.problems_attempted == 1

    @pytest.mark.asyncio
    async def test_give_maths_problem_number_spelling(self):
        ctx = make_context()
        result = await self.agent.give_maths_problem(ctx, level="beginner", operation="number_spelling")
        assert "spelling" in result.lower() or "number" in result.lower()
        assert self.agent.problems_attempted == 1

    @pytest.mark.asyncio
    async def test_check_answer_correct(self):
        ctx = make_context()
        # Set up a known problem
        await self.agent.give_maths_problem(ctx, level="beginner", operation="addition")
        correct = self.agent._current_problem["answer"]
        problem_id = self.agent._current_problem["id"]
        result = await self.agent.check_answer(ctx, problem_id=problem_id, student_answer=correct)
        assert self.agent.problems_correct == 1
        assert "correct" in result.lower() or "शाबाश" in result or "Excellent" in result

    @pytest.mark.asyncio
    async def test_check_answer_wrong(self):
        ctx = make_context()
        await self.agent.give_maths_problem(ctx, level="beginner", operation="addition")
        problem_id = self.agent._current_problem["id"]
        result = await self.agent.check_answer(ctx, problem_id=problem_id, student_answer="99999")
        assert self.agent.problems_correct == 0
        assert "correct answer" in result.lower() or "answer is" in result.lower()

    @pytest.mark.asyncio
    async def test_check_answer_no_active_problem(self):
        ctx = make_context()
        result = await self.agent.check_answer(ctx, problem_id="none", student_answer="5")
        assert "don't have" in result.lower() or "no active" in result.lower() or "new one" in result.lower()

    @pytest.mark.asyncio
    async def test_handback_to_tara_summary(self):
        ctx = make_context()
        await self.agent.give_maths_problem(ctx, level="beginner", operation="addition")
        correct = self.agent._current_problem["answer"]
        problem_id = self.agent._current_problem["id"]
        await self.agent.check_answer(ctx, problem_id=problem_id, student_answer=correct)
        result = await self.agent.handback_to_tara(ctx)
        assert "HANDBACK TO TARA" in result
        assert "1 out of 1" in result
        assert "Nayani" in result

    @pytest.mark.asyncio
    async def test_handback_no_problems_attempted(self):
        ctx = make_context()
        result = await self.agent.handback_to_tara(ctx)
        assert "HANDBACK TO TARA" in result
        assert "just started" in result.lower()
