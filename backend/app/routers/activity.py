from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from app.database import get_db
from app.models.activity import Activity


router = APIRouter(
    prefix="/api/activities",
    tags=["Activities"]
)


class ActivityCreate(BaseModel):
    user_id: int
    activity_type: str
    description: str | None = None


@router.post("/")
def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db)
):

    new_activity = Activity(
        user_id=activity.user_id,
        activity_date=date.today(),
        activity_type=activity.activity_type,
        description=activity.description
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    return {
        "message": "Activity recorded successfully",
        "activity_id": new_activity.id,
        "date": new_activity.activity_date,
        "activity_type": new_activity.activity_type
    }


@router.get("/{user_id}")
def get_activities(
    user_id: int,
    db: Session = Depends(get_db)
):

    activities = (
        db.query(Activity)
        .filter(Activity.user_id == user_id)
        .order_by(Activity.activity_date.desc())
        .all()
    )

    return [
        {
            "id": activity.id,
            "user_id": activity.user_id,
            "date": activity.activity_date,
            "activity_type": activity.activity_type,
            "description": activity.description
        }
        for activity in activities
    ]