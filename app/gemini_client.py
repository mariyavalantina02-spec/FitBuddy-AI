from functools import lru_cache

from google import genai

from app.config import settings


@lru_cache(maxsize=1)
def get_client():

    if not settings.GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add your Gemini API key to the .env file."
        )

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY
    )

    return client


def generate_text(
    model: str,
    prompt: str
):

    client = get_client()

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    text = getattr(
        response,
        "text",
        None
    )

    if not text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return text.strip()