from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.meal import Meal


router = APIRouter(
    prefix="/api/meals",
    tags=["Meals"]
)


class MealCreate(BaseModel):
    user_id: int
    meal_type: str
    food_name: str
    calories: float = 0
    protein: float = 0
    carbs: float = 0
    fat: float = 0


@router.post("/")
def create_meal(
    meal: MealCreate,
    db: Session = Depends(get_db)
):
    new_meal = Meal(
        user_id=meal.user_id,
        meal_type=meal.meal_type,
        food_name=meal.food_name,
        calories=meal.calories,
        protein=meal.protein,
        carbs=meal.carbs,
        fat=meal.fat
    )

    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)

    return {
        "message": "Meal saved successfully",
        "meal_id": new_meal.id
    }


@router.get("/{user_id}")
def get_meals(
    user_id: int,
    db: Session = Depends(get_db)
):
    meals = (
        db.query(Meal)
        .filter(Meal.user_id == user_id)
        .order_by(Meal.created_at.desc())
        .all()
    )

    return [
        {
            "id": meal.id,
            "meal_type": meal.meal_type,
            "food_name": meal.food_name,
            "calories": meal.calories,
            "protein": meal.protein,
            "carbs": meal.carbs,
            "fat": meal.fat,
            "created_at": meal.created_at
        }
        for meal in meals
    ]