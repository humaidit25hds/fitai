from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine

from app.models.user import User
from app.models.workout import Workout
from app.models.meal import Meal
from app.models.activity import Activity

from app.routers.auth import router as auth_router
from app.routers.profile import router as profile_router
from app.routers.workout import router as workout_router
from app.routers.meal import router as meal_router
from app.routers.ai import router as ai_router
from app.routers.activity import router as activity_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="FitAI API",
    description="AI-powered fitness and nutrition platform",
    version="1.0.0"
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://localhost",
        "http://localhost",
        "capacitor://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(workout_router)
app.include_router(meal_router)
app.include_router(ai_router)
app.include_router(activity_router)


@app.get("/")
def root():
    return {
        "message": "FitAI backend is running!"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "FitAI API"
    }