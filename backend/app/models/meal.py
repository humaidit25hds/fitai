from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime

from app.database import Base


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    meal_type = Column(String, nullable=False)
    food_name = Column(String, nullable=False)
    calories = Column(Float, default=0)
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fat = Column(Float, default=0)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )