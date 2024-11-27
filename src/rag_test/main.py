from contextlib import asynccontextmanager

from fastapi import FastAPI

from rag_test.api import meal_recommender
from rag_test.db.db import initialize_database
from rag_test.recommender.recommender import initialize_rag_documents


# Register startup event to initialize the database on app start
@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    initialize_rag_documents()
    yield


app = FastAPI(
    title="Meal recommendation app",
    summary="application that provides recipe recommendations based on the supplied list of ingredients",
    lifespan=lifespan,
)
app.include_router(meal_recommender.router)
