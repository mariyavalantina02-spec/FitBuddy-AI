import asyncio

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request
)

from fastapi.responses import (
    HTMLResponse
)

from app.database import (
    get_all_plans,
    get_all_users,
    get_plan,
    get_user,
    save_plan,
    save_user,
    update_plan
)

from app.gemini_flash_generator import (
    generate_nutrition_tip_with_flash
)

from app.gemini_generator import (
    generate_workout_gemini
)

from app.schemas import (
    FeedbackRequest,
    UserInput
)

from app.templates import templates

from app.updated_plan import (
    update_workout_plan
)


router = APIRouter()


# =========================================================
# HOME
# =========================================================

@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None
        }
    )


# =========================================================
# GENERATE WORKOUT
# =========================================================

@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
async def generate_workout(

    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...)
):

    try:

        # Validate input

        user_input = UserInput(

            username=username,

            user_id=user_id,

            age=age,

            weight=weight,

            goal=goal,

            intensity=intensity
        )


        # Generate both AI responses

        workout_plan, nutrition_tip = await asyncio.gather(

            asyncio.to_thread(

                generate_workout_gemini,

                user_input.username,

                user_input.age,

                user_input.weight,

                user_input.goal,

                user_input.intensity
            ),

            asyncio.to_thread(

                generate_nutrition_tip_with_flash,

                user_input.goal
            )
        )


        # Save user

        save_user(

            user_id=user_input.user_id,

            username=user_input.username,

            age=user_input.age,

            weight=user_input.weight,

            goal=user_input.goal,

            intensity=user_input.intensity
        )


        # Save original plan

        save_plan(

            user_id=user_input.user_id,

            original_plan=workout_plan,

            nutrition_tip=nutrition_tip
        )


        # Display result

        return templates.TemplateResponse(

            request=request,

            name="result.html",

            context={

                "user": user_input,

                "workout_plan": workout_plan,

                "nutrition_tip": nutrition_tip,

                "message":
                    "Your personalized 7-day plan is ready.",

                "error": None
            }
        )


    except Exception as error:

        return templates.TemplateResponse(

            request=request,

            name="index.html",

            context={

                "error": str(error)
            },

            status_code=500
        )


# =========================================================
# SUBMIT FEEDBACK
# =========================================================

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
async def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...)
):

    try:

        feedback_request = FeedbackRequest(

            user_id=user_id,

            feedback=feedback
        )


        # Find user

        user = get_user(
            feedback_request.user_id
        )


        # Find existing plan

        plan = get_plan(
            feedback_request.user_id
        )


        if not user:

            raise HTTPException(

                status_code=404,

                detail="User ID was not found."
            )


        if not plan:

            raise HTTPException(

                status_code=404,

                detail="Workout plan was not found."
            )


        # If there was a previous update,
        # use that as the current plan.

        current_plan = (

            plan.updated_plan

            if plan.updated_plan

            else plan.original_plan
        )


        # Generate updated plan

        updated_plan = await asyncio.to_thread(

            update_workout_plan,

            current_plan,

            feedback_request.feedback,

            user.goal,

            user.intensity
        )


        # Generate new tip

        nutrition_tip = await asyncio.to_thread(

            generate_nutrition_tip_with_flash,

            user.goal
        )


        # Save update

        update_plan(

            user_id=feedback_request.user_id,

            updated_plan=updated_plan,

            feedback=feedback_request.feedback,

            nutrition_tip=nutrition_tip
        )


        # Display updated result

        return templates.TemplateResponse(

            request=request,

            name="result.html",

            context={

                "user": user,

                "workout_plan": updated_plan,

                "nutrition_tip": nutrition_tip,

                "message":
                    "Your plan was updated using your feedback.",

                "error": None
            }
        )


    except HTTPException:

        raise


    except Exception as error:

        user = get_user(user_id)

        return templates.TemplateResponse(

            request=request,

            name="result.html",

            context={

                "user": user,

                "workout_plan": "",

                "nutrition_tip": "",

                "message": None,

                "error": str(error)
            },

            status_code=500
        )


# =========================================================
# ADMIN VIEW
# =========================================================

@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
async def view_all_users(
    request: Request
):

    users = get_all_users()

    plans = get_all_plans()


    plan_dictionary = {

        plan.user_id: plan

        for plan in plans
    }


    return templates.TemplateResponse(

        request=request,

        name="all_users.html",

        context={

            "users": users,

            "plans": plan_dictionary
        }
    )


# =========================================================
# JSON API
# =========================================================

@router.get(
    "/api/users"
)
async def api_users():

    users = get_all_users()

    plans = get_all_plans()


    plan_dictionary = {

        plan.user_id: plan

        for plan in plans
    }


    result = []


    for user in users:

        plan = plan_dictionary.get(
            user.user_id
        )


        result.append({

            "user_id":
                user.user_id,

            "username":
                user.username,

            "age":
                user.age,

            "weight":
                user.weight,

            "goal":
                user.goal,

            "intensity":
                user.intensity,

            "original_plan":
                plan.original_plan
                if plan
                else None,

            "updated_plan":
                plan.updated_plan
                if plan
                else None,

            "feedback":
                plan.feedback
                if plan
                else None
        })


    return {

        "users": result
    }