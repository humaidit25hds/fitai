from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime

from app.database import Base


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    exercise = Column(String, nullable=False)

    reps = Column(Integer, default=0)

    sets = Column(Integer, default=1)

    duration = Column(Float, default=0)

    calories = Column(Float, default=0)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )