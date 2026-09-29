from sqlalchemy import Column, Integer, String, Float

from app.database import Base


class User(Base):
    __tablename__ = "users"

    # =========================
    # BASIC USER INFORMATION
    # =========================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    # =========================
    # FITNESS PROFILE
    # =========================

    age = Column(
        Integer,
        nullable=False,
        default=0
    )

    gender = Column(
        String,
        nullable=False,
        default="not_set"
    )

    height = Column(
        Float,
        nullable=False,
        default=0
    )

    weight = Column(
        Float,
        nullable=False,
        default=0
    )

    activity = Column(
        String,
        nullable=False,
        default="not_set"
    )

    goal = Column(
        String,
        nullable=False,
        default="not_set"
    )

    # =========================
    # FITNESS CALCULATIONS
    # =========================

    bmr = Column(
        Float,
        nullable=True
    )

    maintenance_calories = Column(
        Float,
        nullable=True
    )

    target_calories = Column(
        Float,
        nullable=True
    )

    protein = Column(
        Float,
        nullable=True
    )

    carbs = Column(
        Float,
        nullable=True
    )

    fat = Column(
        Float,
        nullable=True
    )