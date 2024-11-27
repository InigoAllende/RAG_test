from http import HTTPStatus
from fastapi import APIRouter, Response

from rag_test.api.models import MealRecommendationRequest, MealRecommendationResponse
from rag_test.recommender.recommender import DOCSTORE, rag_pipeline

router = APIRouter()


@router.post("/recommend_recipe",
             status_code=HTTPStatus.OK, 
             response_model=MealRecommendationResponse,
             description="This endpoint suggests a meal recipe based on the inputted ingredients. The response content will be Markdown formatted",
             responses={HTTPStatus.BAD_REQUEST: {"description": "Returned when the given ingredients are not valid for any recipe."}})
def recommend_recipe(request: MealRecommendationRequest):
    recommendation = rag_pipeline(request.ingredients)
    return MealRecommendationResponse(recipe_instruction=recommendation)
