from app.config import settings
from app.gemini_client import generate_text


def generate_nutrition_tip_with_flash(
    goal: str
):

    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.

The user's fitness goal is:

{goal}

Generate ONE concise nutrition or recovery tip.

Requirements:

- 2 to 4 sentences.
- Practical and easy to follow.
- Align it with the user's fitness goal.
- Encourage balanced nutrition.
- Mention hydration, protein, recovery, sleep, or balanced meals when relevant.
- Do not prescribe medication.
- Do not provide medical diagnosis.
- Do not recommend dangerous dieting.
- Return plain text only.
"""

    response = generate_text(
        settings.GEMINI_NUTRITION_MODEL,
        prompt
    )

    return response