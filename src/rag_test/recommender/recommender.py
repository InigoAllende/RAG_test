import json

from fastapi import HTTPException
from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from sqlalchemy import text

from rag_test.db.db import engine

CONTEXT_PROMPT = """
            Given the following context, suggest a recipe with the ingredients.
            The goal is to create a meal recipe off of a list of ingredients. 
            Behave as an API would, returning a JSON with the following fields: `status_code` and `recipe_instructions`. 
            Return 200 if it's possible to create a recipe with the ingredients and 400 if the ingredients canot be used for cooking.
            If not all of the ingredients can be used for cooking, use only those elegible.
            The field `recipe_instructions` should be formatted using `Markdown` and should have the following sections: `Recipe title`, `Ingredients` and `Preparation`.
            
            These are some existing recipes that we want to prioritize, suggest them if any of the ingredients are present in it. Remember to format them using Markdown: 
                {% for document in documents %}
                    Recipe:
                    {{ document.content }}
                {% endfor %}
            
            Question: What can we prepare with the following ingredients: {{ ingredients }}
        """


DOCSTORE = InMemoryDocumentStore()


def rag_pipeline(content: str) -> str:
    # This automatically fetches the OPENAI_API_KEY from the env variables. 
    pipe = Pipeline()
    pipe.add_component("retriever", InMemoryBM25Retriever(document_store=DOCSTORE))
    pipe.add_component("context_prompt", PromptBuilder(template=CONTEXT_PROMPT))
    pipe.add_component(
        "llm",
        OpenAIGenerator(
            model="gpt-4o",
            generation_kwargs={"response_format": {"type": "json_object"}},
        ),
    )
    pipe.connect("retriever", "context_prompt.documents")
    pipe.connect("context_prompt", "llm")

    response = pipe.run(
        {"retriever": {"query": content}, "context_prompt": {"ingredients": content}}
    )

    response_content = json.loads(response["llm"]["replies"][0])

    if response_content["status_code"] == 200:
        return response_content["recipe_instructions"]

    raise HTTPException(
        status_code=400,
        detail=f"Could not create a recipe following the ingredients provided: '{content}'. Please use a different input.",
    )


def initialize_rag_documents():
    with engine.connect() as connection:
        # fetch contents of `recipe` table
        recipes = connection.execute(text("SELECT * FROM recipe"))
        # create a document for each entry
        documents = []
        for recipe in recipes.fetchall():
            # it's possible to pass a dataframe ( maybe worth it?)
            documents.append(
                Document(
                    content=f"{recipe.title}; {recipe.ingredients}; {recipe.instructions}"
                )
            )

        DOCSTORE.write_documents(documents=documents)
