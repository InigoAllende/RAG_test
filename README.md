README: Include a brief README explaining:
## Running the application.

To run the application without modifications make sure the following dependencies are installed:
* [Docker](https://docs.docker.com/engine/install/)
* [Poetry](https://python-poetry.org/)
* [Python 3.12](https://www.python.org/downloads/release/python-3120/)

This project uses poetry to manage its dependencies. Using a [virtual environment](https://docs.python.org/3.12/library/venv.html) is encouraged.
Install dependencies:

```
    poetry install
```

Double check the environment variables (a `.env` example file is provided) and make sure all are set. The only 2 variables that should need to be modified are:
* `OPENAI_API_KEY`, this should be set to your personal key
* `INITIAL_DATA_PATH`, this is path should point to the folder containing the datasets for the [Retrieval Augmented Generation](https://haystack.deepset.ai/blog/rag-pipelines-from-scratch).

I like to use [direnv](https://direnv.net/) to manage the environment variables.

> **_NOTE:_**  The code uses the `gpt-4o` model. If the key does not support this, make sure the model is updated [here](src/rag_test/recommender/recommender.py).

To run the project there is a makefile that contains the necessary commands, once everything is installed:
```
    make run-local
```
Will start the postgres database in docker and the web application.

Additionally the project can be run in a container using the command
```
    make run
```

## Architecture.
The solution can be divided into 3 sections:
* API
* Database
* Recommender

### API
For the API section it is using [Fastapi](https://fastapi.tiangolo.com/) to provide the endpoint for the recipe recommendations.
Overall the functionality is rather straightforward here as there is only 1 endpoint that uses very simple validation for the request and responses.
The API endpoint expects a text input with ingredients. There is no specifics about the formats or any pre-processing of the input to help improve the response generation.

The more interesting aspect is the use of `lifespan` to initialize the application by loading the datasets into the database and the RAG docstore. This ensures that any basic data required is loaded on startup and there is no need for extra commands.

### Database
For the database I created a single table to store the recipes provided in the dataset. The table consists of 3 columns (`Title`, `Ingredients` and `Instructions`), all of which are mandatory fields.

The database section is also the one responsible for the initial loading of the datasets when the application starts. At the moment it requires a path to be provided to load the initial data.

### Recommender
The recommender uses [Haystack](https://docs.haystack.deepset.ai/docs/intro) to leverage the recipes stored in the database against an LLM model.

It is initialized on application startup by loading the recipes from the database. It uses the `InMemoryBM25Retriever` as it is the simplest to implement as it is in memory but would not be ideal for an application that needs to scale as it doesn't persist data or would not be able to manage large datasets.

It uses the following prompt to generate a response:
    
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

This prompt can be modified to adjust the behaviour. For example it would be possible to make it return multiple recipes or make it so that the ingredients used are only those specifically stated in the input.

I have experienced some problems with it as I have had instances in which the same input (i.e. "chicken") returns a recipe, as it is expected, and others it has returned the prompt for no available recipes with the given ingredients.


## Examples of how to use the API.
Right now the application only consists of 1 endpoint. This endpoint recieves a text input with ingredients for a meal and suggests a recipe based off of them. If no meal can be prepared with the ingredients it will return a 400. The documentation for the endpoint can be found `http://127.0.0.1:8000/redoc`.

An example request 

```
curl --location 'http://127.0.0.1:8000/recommend_recipe' \
--header 'Content-Type: application/json' \
--data '{"ingredients": "tofu, chicken, beef, lentils" }'
```
This request should return a recipe using the provided ingredients and, if using the dataset for `RAG` one of the recipes provided in it.

Another example request

```
curl --location 'http://127.0.0.1:8000/recommend_recipe' \
--header 'Content-Type: application/json' \
--data '{"ingredients": "straw" }'
```
This one should return a 400 response as it is not able to find a recipe that can be made using the provided ingredients.

