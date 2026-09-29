from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User


router = APIRouter(
    prefix="/api/profile",
    tags=["Profile"]
)


class ProfileCreate(BaseModel):
    user_id: int
    name: str
    age: int
    gender: str
    height: float
    weight: float
    activity: str
    goal: str


@router.post("/")
def create_profile(
    profile: ProfileCreate,
    db: Session = Depends(get_db)
):
    # Find the existing user created during registration
    user = (
        db.query(User)
        .filter(User.id == profile.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User account not found."
        )

    # Calculate BMR
    if profile.gender.lower() == "male":
        bmr = (
            10 * profile.weight
            + 6.25 * profile.height
            - 5 * profile.age
            + 5
        )
    else:
        bmr = (
            10 * profile.weight
            + 6.25 * profile.height
            - 5 * profile.age
            - 161
        )

    # Activity multipliers
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }

    multiplier = activity_multipliers.get(
        profile.activity,
        1.55
    )

    maintenance = bmr * multiplier

    # Calculate target calories
    target_calories = maintenance

    if profile.goal == "fat_loss":
        target_calories = maintenance - 400

    elif profile.goal == "weight_gain":
        target_calories = maintenance + 300

    # Calculate macros
    protein = profile.weight * 1.6

    fat = profile.weight * 0.8

    protein_calories = protein * 4

    fat_calories = fat * 9

    carbs = (
        target_calories
        - protein_calories
        - fat_calories
    ) / 4

    # Update the EXISTING registered user
    user.name = profile.name.strip()
    user.age = profile.age
    user.gender = profile.gender
    user.height = profile.height
    user.weight = profile.weight
    user.activity = profile.activity
    user.goal = profile.goal

    user.bmr = bmr
    user.maintenance_calories = maintenance
    user.target_calories = target_calories
    user.protein = protein
    user.carbs = carbs
    user.fat = fat

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile saved successfully",
        "user_id": user.id,
        "fitness": {
            "bmr": round(bmr),
            "maintenance_calories": round(maintenance),
            "target_calories": round(target_calories),
            "protein": round(protein),
            "carbs": round(carbs),
            "fat": round(fat)
        }
    }


@router.get("/{user_id}")
def get_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return {
        "id": user.id,
        "name": user.name,
        "age": user.age,
        "gender": user.gender,
        "height": user.height,
        "weight": user.weight,
        "activity": user.activity,
        "goal": user.goal,
        "fitness": {
            "bmr": round(user.bmr) if user.bmr is not None else 0,
            "maintenance_calories": (
                round(user.maintenance_calories)
                if user.maintenance_calories is not None
                else 0
            ),
            "target_calories": (
                round(user.target_calories)
                if user.target_calories is not None
                else 0
            ),
            "protein": (
                round(user.protein)
                if user.protein is not None
                else 0
            ),
            "carbs": (
                round(user.carbs)
                if user.carbs is not None
                else 0
            ),
            "fat": (
                round(user.fat)
                if user.fat is not None
                else 0
            )
        }
    }