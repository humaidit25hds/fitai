from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi import Depends
import os
import json

from app.database import get_db
from app.models.user import User


load_dotenv()


router = APIRouter(
    prefix="/api/ai",
    tags=["AI Coach"]
)


# =========================================================
# CHAT REQUEST
# =========================================================

class ChatRequest(BaseModel):
    message: str
    user_id: int | None = None


# =========================================================
# FITAI COACH INSTRUCTION
# =========================================================

FITAI_COACH_INSTRUCTION = """
You are FitAI Coach, a friendly and modern AI fitness assistant.

Your job is to give practical, simple and motivating guidance about:

- workouts
- exercise
- nutrition
- calories
- protein
- healthy eating
- weight management
- fitness habits
- recovery

IMPORTANT RESPONSE STYLE:

1. Keep answers concise and useful.
2. Do not give extremely long explanations unless the user asks for detail.
3. Use a clean, modern structure.
4. Use emojis sparingly.
5. Use short headings.
6. Use bullet points and numbered lists where useful.
7. Avoid unnecessary repetition.
8. Give clear actionable steps.
9. Avoid unrealistic promises about weight loss or muscle gain.
10. Encourage gradual progress and consistency.
11. Never claim to diagnose medical conditions.
12. If the user describes serious pain, injury, illness, or concerning symptoms, recommend consulting a qualified healthcare professional.
13. Add a short safety note only when relevant.
14. Do not start every answer with "Sure!" or "Absolutely!"
15. Speak naturally, like a helpful personal fitness coach.

PERSONALIZATION:

When user profile information is provided, use it to make your advice more relevant.

Respect the user's stated fitness goal.

For calorie and nutrition questions, consider their target calories and macro targets.

Do not expose database details or technical implementation details to the user.

Do not assume information that is not provided.

Use Markdown.
"""


# =========================================================
# AI CHAT
# =========================================================

@router.post("/chat")
def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is missing from backend/.env"
        )

    try:

        # -------------------------------------------------
        # Get user's profile
        # -------------------------------------------------

        user = None

        if request.user_id is not None:

            user = (
                db.query(User)
                .filter(User.id == request.user_id)
                .first()
            )

        # -------------------------------------------------
        # Build profile context
        # -------------------------------------------------

        profile_context = ""

        if user:

            profile_context = f"""
USER FITNESS PROFILE:

Name: {user.name}
Age: {user.age}
Gender: {user.gender}
Height: {user.height} cm
Weight: {user.weight} kg
Activity level: {user.activity}
Goal: {user.goal}

BMR: {round(user.bmr or 0)} kcal/day
Maintenance calories: {round(user.maintenance_calories or 0)} kcal/day
Target calories: {round(user.target_calories or 0)} kcal/day

Daily protein target: {round(user.protein or 0)} g
Daily carbohydrate target: {round(user.carbs or 0)} g
Daily fat target: {round(user.fat or 0)} g

Use this information when it is relevant to the user's question.
"""

        else:

            profile_context = """
USER FITNESS PROFILE:

No profile information is currently available.

Give general fitness guidance and avoid assuming personal measurements.
"""

        # -------------------------------------------------
        # Create Gemini client
        # -------------------------------------------------

        client = genai.Client(
            api_key=api_key
        )

        # -------------------------------------------------
        # Send profile + user question
        # -------------------------------------------------

        prompt = f"""
{profile_context}

USER QUESTION:

{request.message}
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=FITAI_COACH_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=800
            )
        )

        return {
            "answer": response.text
        }

    except Exception as error:

        print("\n========== GEMINI CHAT ERROR ==========")
        print(type(error).__name__)
        print(str(error))
        print("=======================================\n")

        raise HTTPException(
            status_code=500,
            detail=f"Gemini error: {str(error)}"
        )


# =========================================================
# FOOD SCANNER
# =========================================================

class FoodNutrition(BaseModel):
    food_name: str
    calories: float
    protein: float
    carbs: float
    fat: float


@router.post("/scan-food")
async def scan_food(
    image: UploadFile = File(...)
):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is missing from backend/.env"
        )

    if not image.content_type:
        raise HTTPException(
            status_code=400,
            detail="Could not determine image type."
        )

    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an image file."
        )

    try:

        image_bytes = await image.read()

        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Image is too large. Please use an image smaller than 10 MB."
            )

        client = genai.Client(
            api_key=api_key
        )

        prompt = """
Analyze the food shown in this image for a fitness application.

Identify the most likely main food or meal.

Estimate the nutrition for the visible serving/portion.

Return ONLY valid JSON:

{
  "food_name": "name of food",
  "calories": number,
  "protein": number,
  "carbs": number,
  "fat": number
}

Rules:

- calories are kcal.
- protein, carbs and fat are grams.
- Use reasonable estimates based on the visible portion.
- Do not pretend the values are exact.
- If multiple foods are visible, describe them as a combined meal.
- Do not include markdown.
- Do not include explanations outside the JSON.
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=image.content_type
                ),
                prompt
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=300,
                response_mime_type="application/json",
                response_schema=FoodNutrition
            )
        )

        if getattr(response, "parsed", None):

            result = response.parsed

            if isinstance(result, FoodNutrition):
                nutrition = result.model_dump()
            else:
                nutrition = dict(result)

        else:

            raw_text = response.text.strip()

            nutrition = json.loads(raw_text)

        return {
            "success": True,
            "nutrition": nutrition
        }

    except HTTPException:
        raise

    except Exception as error:

        print("\n========== GEMINI FOOD SCANNER ERROR ==========")
        print(type(error).__name__)
        print(str(error))
        print("===============================================\n")

        raise HTTPException(
            status_code=500,
            detail=f"Food scanner error: {str(error)}"
        )