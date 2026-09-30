import json
import re

from app.config import settings
from app.gemini_client import generate_text


def extract_json(text: str):

    text = text.strip()

    if text.startswith("```"):

        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\s*```$",
            "",
            text
        )

    start = text.find("{")

    end = text.rfind("}")

    if start != -1 and end != -1:

        return text[
            start:end + 1
        ]

    return text


def update_workout_plan(
    original_plan: str,
    feedback: str,
    goal: str,
    intensity: str
):

    prompt = f"""
You are FitBuddy.

You need to update an existing 7-day fitness plan.

Fitness goal:

{goal}

Workout intensity:

{intensity}


ORIGINAL PLAN:

{original_plan}


USER FEEDBACK:

{feedback}


Create a revised 7-day workout plan.

Return ONLY valid JSON.

Use this structure:

{{
    "summary": "Describe what changed",

    "days": [

        {{
            "day": "Day 1",

            "focus": "Workout focus",

            "warmup": "Warmup",

            "exercises": [

                {{
                    "name": "Exercise name",
                    "sets": 3,
                    "reps": "10",
                    "rest": "60 seconds"
                }}

            ],

            "cooldown": "Cooldown/recovery"
        }}

    ],

    "safety_note": "General safety note"
}}

Rules:

1. Return exactly 7 days.
2. Incorporate reasonable user feedback.
3. Preserve the user's main fitness goal.
4. Respect requested intensity.
5. Include recovery where appropriate.
6. Do not diagnose medical conditions.
7. Do not prescribe medications.
8. If feedback is unsafe, adapt it conservatively.
"""

    response = generate_text(
        settings.GEMINI_WORKOUT_MODEL,
        prompt
    )

    try:

        parsed = json.loads(
            extract_json(response)
        )

        return json.dumps(
            parsed,
            indent=2
        )

    except json.JSONDecodeError:

        return response