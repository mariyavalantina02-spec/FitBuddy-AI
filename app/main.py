from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from app.database import init_db

from app.routes import router


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(

    title="FitBuddy",

    description=(
        "AI Fitness Plan Generator "
        "using Gemini models"
    ),

    version="1.0.0"
)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(

    "/static",

    StaticFiles(
        directory="static"
    ),

    name="static"
)


# =========================================================
# ROUTES
# =========================================================

app.include_router(
    router
)


# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
def startup():

    init_db()


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get(
    "/health",
    tags=["System"]
)
def health():

    return {

        "status": "ok",

        "service": "FitBuddy"
    }