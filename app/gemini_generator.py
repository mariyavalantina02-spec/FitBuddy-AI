import json
import re

from app.config import settings
from app.gemini_client import generate_text


def extract_json(text: str):

    text = text.strip()

    # Remove Markdown code fences if Gemini adds them
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


def generate_workout_gemini(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str
):

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a personalized 7-day workout plan.

User information:

Name: {username}

Age: {age}

Weight: {weight} kg

Fitness goal: {goal}

Workout intensity: {intensity}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "summary": "Short personalized summary",

    "days": [

        {{
            "day": "Day 1",

            "focus": "Workout focus",

            "warmup": "5-10 minute warmup",

            "exercises": [

                {{
                    "name": "Exercise name",
                    "sets": 3,
                    "reps": "10",
                    "rest": "60 seconds"
                }}

            ],

            "cooldown": "Cooldown or recovery guidance"
        }}

    ],

    "safety_note": "General safety note"
}}

Important requirements:

1. Exactly 7 days.
2. Every day must have a focus.
3. Every day must have a warmup.
4. Every day must have exercises or appropriate recovery activity.
5. Every day must have cooldown/recovery guidance.
6. Respect the requested intensity.
7. Align the plan with the fitness goal.
8. Include reasonable recovery.
9. Keep exercises practical.
10. Do not diagnose medical conditions.
11. Do not prescribe medication.
12. Do not claim the plan is medical advice.
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