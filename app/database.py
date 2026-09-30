from typing import Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)

from app.config import settings


# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

connect_args = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# ---------------------------------------------------------
# BASE CLASS
# ---------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------
# USER TABLE
# ---------------------------------------------------------

class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[str] = mapped_column(
        unique=True,
        index=True
    )

    username: Mapped[str]

    age: Mapped[int]

    weight: Mapped[float]

    goal: Mapped[str]

    intensity: Mapped[str]


# ---------------------------------------------------------
# PLAN TABLE
# ---------------------------------------------------------

class Plan(Base):

    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[str] = mapped_column(
        unique=True,
        index=True
    )

    original_plan: Mapped[str]

    updated_plan: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )

    nutrition_tip: Mapped[str]

    feedback: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )


# ---------------------------------------------------------
# CREATE DATABASE
# ---------------------------------------------------------

def init_db():

    Base.metadata.create_all(
        bind=engine
    )


# ---------------------------------------------------------
# SAVE USER
# ---------------------------------------------------------

def save_user(
    user_id: str,
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str
):

    with SessionLocal() as db:

        existing_user = db.scalar(
            select(User).where(
                User.user_id == user_id
            )
        )

        if existing_user:

            existing_user.username = username
            existing_user.age = age
            existing_user.weight = weight
            existing_user.goal = goal
            existing_user.intensity = intensity

            user = existing_user

        else:

            user = User(
                user_id=user_id,
                username=username,
                age=age,
                weight=weight,
                goal=goal,
                intensity=intensity
            )

            db.add(user)

        db.commit()

        db.refresh(user)

        return user


# ---------------------------------------------------------
# SAVE PLAN
# ---------------------------------------------------------

def save_plan(
    user_id: str,
    original_plan: str,
    nutrition_tip: str
):

    with SessionLocal() as db:

        existing_plan = db.scalar(
            select(Plan).where(
                Plan.user_id == user_id
            )
        )

        if existing_plan:

            existing_plan.original_plan = original_plan
            existing_plan.updated_plan = None
            existing_plan.feedback = None
            existing_plan.nutrition_tip = nutrition_tip

            plan = existing_plan

        else:

            plan = Plan(
                user_id=user_id,
                original_plan=original_plan,
                nutrition_tip=nutrition_tip
            )

            db.add(plan)

        db.commit()

        db.refresh(plan)

        return plan


# ---------------------------------------------------------
# UPDATE PLAN
# ---------------------------------------------------------

def update_plan(
    user_id: str,
    updated_plan: str,
    feedback: str,
    nutrition_tip: str
):

    with SessionLocal() as db:

        plan = db.scalar(
            select(Plan).where(
                Plan.user_id == user_id
            )
        )

        if plan is None:
            return None

        plan.updated_plan = updated_plan
        plan.feedback = feedback
        plan.nutrition_tip = nutrition_tip

        db.commit()

        db.refresh(plan)

        return plan


# ---------------------------------------------------------
# GET USER
# ---------------------------------------------------------

def get_user(
    user_id: str
):

    with SessionLocal() as db:

        return db.scalar(
            select(User).where(
                User.user_id == user_id
            )
        )


# ---------------------------------------------------------
# GET PLAN
# ---------------------------------------------------------

def get_plan(
    user_id: str
):

    with SessionLocal() as db:

        return db.scalar(
            select(Plan).where(
                Plan.user_id == user_id
            )
        )


# ---------------------------------------------------------
# GET ALL USERS
# ---------------------------------------------------------

def get_all_users():

    with SessionLocal() as db:

        return list(
            db.scalars(
                select(User).order_by(
                    User.id.desc()
                )
            ).all()
        )


# ---------------------------------------------------------
# GET ALL PLANS
# ---------------------------------------------------------

def get_all_plans():

    with SessionLocal() as db:

        return list(
            db.scalars(
                select(Plan).order_by(
                    Plan.id.desc()
                )
            ).all()
        )