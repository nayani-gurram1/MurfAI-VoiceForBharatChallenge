"""
Day 9 - Specialist Agent: Maths Practice Buddy
Tara hands off to this agent when a student asks for maths/numbers practice.
This agent is launched via session.update_agent() in the main Tara pipeline.
"""

import random

from livekit.agents import Agent, RunContext, function_tool

MATHS_SYSTEM_PROMPT = """
IDENTITY
You are Ganit, a friendly and patient maths buddy for young learners.
You were introduced by Tara, VoiceForBharat's reading buddy.
Your only job is maths and numbers practice — addition, subtraction, counting, and number recognition in English and Hindi.
You do NOT teach reading or pronunciation. For reading topics, say: "Tara can help you with that! I only do maths."

OBJECTIVES
A successful maths session means:
1. The student solves at least one number or arithmetic problem correctly (or tries hard).
2. The student feels encouraged, never embarrassed or judged.
3. The student learns the English name for at least one number (1-100) or a maths operation.

LANGUAGE
Always write Hindi words in Devanagari script (नमस्ते, बहुत बढ़िया, शाबाश).
Never romanize Hindi. English stays in Latin script.

OPENING (IMPORTANT)
When you start, introduce yourself warmly:
"नमस्ते! I am Ganit, your maths buddy from VoiceForBharat! Tara asked me to help you practice numbers and maths today. Let's start with something fun!"
Then immediately offer one of: counting, addition, subtraction, or number spelling.

TOOLS — WHEN AND HOW TO USE THEM
1. give_maths_problem(level, operation)
   Call this when the student asks for a maths question or agrees to practice.
   Call immediately after your opening if the student says yes or okay.

2. check_answer(problem_id, student_answer)
   Call this when the student gives an answer to a problem.

3. handback_to_tara()
   Call this ONLY when:
   - The student says they want to go back to reading practice.
   - The student asks for Tara.
   - The session is complete and the student says goodbye.

GUARDRAILS
- NEVER shame a wrong answer. Always say "Good try! The answer is X. Let's try another!"
- NEVER go beyond basic maths (1-100 addition/subtraction/counting).
- For any off-topic question: "I'm just your maths buddy! Ask Tara about that."

STYLE
Short sentences. Speak clearly and slowly. Celebrate every attempt. Always in Hinglish.
"""


class MathsSpecialist(Agent):
    """
    Day 9 Specialist Agent — Maths Practice Buddy (Ganit).
    Activated via session.update_agent() from the main Tara Assistant.
    """

    def __init__(
        self, student_name: str = "Friend", student_level: str = "beginner"
    ) -> None:
        super().__init__(instructions=MATHS_SYSTEM_PROMPT)
        self.student_name = student_name
        self.student_level = student_level
        self.problems_attempted = 0
        self.problems_correct = 0
        # Track active problem for answer checking
        self._current_problem: dict | None = None

    # ── Maths Tools ────────────────────────────────────────────────────────

    @function_tool
    async def give_maths_problem(
        self,
        context: RunContext,
        level: str,
        operation: str,
    ):
        """Generate a maths problem for the student to solve.
        Call this when the student agrees to practice or asks for a question.

        Args:
            level: Difficulty — 'beginner' (1-10), 'intermediate' (1-20), or 'advanced' (1-50).
            operation: The operation — 'addition', 'subtraction', 'counting', or 'number_spelling'.
        """
        level = level.lower().strip()
        operation = operation.lower().strip()

        # Number ranges by level
        ranges = {"beginner": (1, 10), "intermediate": (1, 20), "advanced": (1, 50)}
        lo, hi = ranges.get(level, (1, 10))

        self.problems_attempted += 1

        if operation == "counting":
            start = random.randint(lo, hi - 3)
            sequence = list(range(start, start + 4))
            missing_idx = random.randint(1, 2)
            answer = sequence[missing_idx]
            displayed = [
                str(n) if i != missing_idx else "?" for i, n in enumerate(sequence)
            ]
            problem_text = " , ".join(displayed)
            problem_id = f"count_{self.problems_attempted}"
            self._current_problem = {
                "id": problem_id,
                "answer": str(answer),
                "operation": "counting",
            }
            return (
                f"Problem ready! Counting sequence: {problem_text}. "
                f"What number goes in place of the question mark? "
                f"[Problem ID: {problem_id}, Answer: {answer}]"
            )

        elif operation == "number_spelling":
            number = random.randint(lo, hi)
            number_words = {
                1: "one",
                2: "two",
                3: "three",
                4: "four",
                5: "five",
                6: "six",
                7: "seven",
                8: "eight",
                9: "nine",
                10: "ten",
                11: "eleven",
                12: "twelve",
                13: "thirteen",
                14: "fourteen",
                15: "fifteen",
                16: "sixteen",
                17: "seventeen",
                18: "eighteen",
                19: "nineteen",
                20: "twenty",
            }
            word = number_words.get(number, str(number))
            problem_id = f"spell_{self.problems_attempted}"
            self._current_problem = {
                "id": problem_id,
                "answer": word,
                "operation": "spelling",
            }
            return (
                f"Number spelling! Say the English word for the number: {number}. "
                f"[Problem ID: {problem_id}, Answer: {word}]"
            )

        elif operation == "subtraction":
            b = random.randint(lo, hi // 2)
            a = random.randint(b, hi)
            answer = a - b
            problem_id = f"sub_{self.problems_attempted}"
            self._current_problem = {
                "id": problem_id,
                "answer": str(answer),
                "operation": "subtraction",
            }
            return (
                f"Subtraction problem! What is {a} minus {b}? "
                f"[Problem ID: {problem_id}, Answer: {answer}]"
            )

        else:  # default: addition
            a = random.randint(lo, hi)
            b = random.randint(lo, hi)
            answer = a + b
            problem_id = f"add_{self.problems_attempted}"
            self._current_problem = {
                "id": problem_id,
                "answer": str(answer),
                "operation": "addition",
            }
            return (
                f"Addition problem! What is {a} plus {b}? "
                f"[Problem ID: {problem_id}, Answer: {answer}]"
            )

    @function_tool
    async def check_answer(
        self,
        context: RunContext,
        problem_id: str,
        student_answer: str,
    ):
        """Check if the student's answer is correct and give encouraging feedback.
        Call this immediately after the student says their answer to a maths problem.

        Args:
            problem_id: The problem ID provided when the problem was given.
            student_answer: The student's spoken answer (e.g. '5', 'seven', 'fifteen').
        """
        if not self._current_problem:
            return "I don't have an active problem. Let me give you a new one!"

        correct_answer = self._current_problem.get("answer", "")
        is_correct = student_answer.strip().lower() == correct_answer.strip().lower()

        if is_correct:
            self.problems_correct += 1
            encouragements = [
                f"शाबाश! {self.student_name}, that is correct! बहुत बढ़िया! 🌟",
                f"Excellent! {self.student_name}! You are brilliant! The answer {correct_answer} is right!",
                f"वाह! Perfect answer! {correct_answer} is exactly right! You are a maths star!",
            ]
            return (
                f"{random.choice(encouragements)} "
                f"Score: {self.problems_correct} correct out of {self.problems_attempted}. "
                f"Shall we try another problem?"
            )
        else:
            return (
                f"Good try, {self.student_name}! The correct answer is {correct_answer}. "
                f"Don't worry — let's try another one! Practice makes perfect! "
                f"Score: {self.problems_correct} correct out of {self.problems_attempted}."
            )

    @function_tool
    async def handback_to_tara(
        self,
        context: RunContext,
    ):
        """Hand the conversation back to Tara (the reading buddy) when:
        - The student wants to go back to reading practice.
        - The student asks for Tara.
        - The maths session is complete and the student says goodbye or wants to stop maths.
        """
        score_summary = (
            f"The student solved {self.problems_correct} out of {self.problems_attempted} maths problems."
            if self.problems_attempted > 0
            else "The student just started maths practice."
        )
        return (
            f"HANDBACK TO TARA REQUESTED. {score_summary} "
            f"Student name: {self.student_name}. "
            f"Please tell Tara to take over and congratulate {self.student_name} on their maths practice!"
        )
