from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.workout import Workout


router = APIRouter(
    prefix="/api/workouts",
    tags=["Workouts"]
)


class WorkoutCreate(BaseModel):
    user_id: int
    exercise: str
    reps: int
    sets: int = 1
    duration: float = 0
    calories: float = 0


@router.post("/")
def create_workout(
    workout: WorkoutCreate,
    db: Session = Depends(get_db)
):
    new_workout = Workout(
        user_id=workout.user_id,
        exercise=workout.exercise,
        reps=workout.reps,
        sets=workout.sets,
        duration=workout.duration,
        calories=workout.calories
    )

    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)

    return {
        "message": "Workout saved successfully",
        "workout_id": new_workout.id
    }


@router.get("/{user_id}")
def get_workouts(
    user_id: int,
    db: Session = Depends(get_db)
):
    workouts = (
        db.query(Workout)
        .filter(Workout.user_id == user_id)
        .order_by(Workout.created_at.desc())
        .all()
    )

    return [
        {
            "id": workout.id,
            "exercise": workout.exercise,
            "reps": workout.reps,
            "sets": workout.sets,
            "duration": workout.duration,
            "calories": workout.calories,
            "created_at": workout.created_at
        }
        for workout in workouts
    ]