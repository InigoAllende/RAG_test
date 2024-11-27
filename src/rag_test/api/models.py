from pydantic import BaseModel


class MealRecommendationRequest(BaseModel):
    ingredients: str


class MealRecommendationResponse(BaseModel):
    recipe_instruction: str
