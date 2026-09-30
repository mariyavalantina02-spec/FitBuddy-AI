import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "FitBuddy")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    GEMINI_WORKOUT_MODEL = os.getenv(
        "GEMINI_WORKOUT_MODEL",
        "gemini-3.8-flash"
    )

    GEMINI_NUTRITION_MODEL = os.getenv(
        "GEMINI_NUTRITION_MODEL",
        "gemini-3.8-flash"
    )

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./fitbuddy.db"
    )


settings = Settings()