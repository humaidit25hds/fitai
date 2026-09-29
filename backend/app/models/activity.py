from sqlalchemy import Column, Integer, String, Date
from app.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    activity_date = Column(Date, nullable=False)

    activity_type = Column(String, nullable=False)

    description = Column(String, nullable=True)