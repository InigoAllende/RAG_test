import os
from typing import Tuple

from sqlalchemy import Connection, create_engine, text

from rag_test.config import settings
from rag_test.db.models import Base

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


def _parse_recipe(file_path: str) -> Tuple[str, str, str]:
    """
    Parses a recipe file and extracts the title, ingredients, and instructions.
    This code assumes that the format for the text files is consistent. That is the title is always at the top.
    And the `ingredients` and `instructions` sections are preceded by the words `ingredients` and `instructions` always.
    """
    with open(file_path, "r") as file:
        lines = file.readlines()

    section = None
    title = None
    ingredients, instructions = [], []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line:  # line is not blank
            if title is None:
                title = stripped_line
            elif stripped_line.lower().startswith("ingredients:"):
                section = "ingredients"
                continue
            elif line.lower().startswith("instructions:"):
                section = "instructions"
                continue

            if section == "ingredients":
                ingredients.append(stripped_line)
            elif section == "instructions":
                instructions.append(stripped_line)

    ingredients_str = ", ".join(ingredients).strip()
    instructions_str = ", ".join(instructions).strip()

    return title, ingredients_str, instructions_str


def _store_recipe(db_conn: Connection, title: str, ingredients: str, instructions: str):
    """Stores a recipe in the database if the title does not already exist."""
    query = text(
        """INSERT INTO recipe(title, ingredients, instructions) 
        VALUES(:title, :ingredients, :instructions) 
        ON CONFLICT (title) DO NOTHING"""
    )

    db_conn.execute(
        query,
        {"title": title, "ingredients": ingredients, "instructions": instructions},
    )


def _load_initial_datasets(connection: Connection):
    path = settings.INITIAL_DATA_PATH
    if not path or not os.path.exists(path):
        raise FileNotFoundError(
            f"The path {path} does not exist. Ensure that the environment variable is set and uses a valid path/"
        )

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            try:
                title, ingredients, instructions = _parse_recipe(file_path)
                _store_recipe(connection, title, ingredients, instructions)
                print(f"Inserted recipe '{title}' into the database.")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
                break


def initialize_database():
    """Check if tables exist before creating them. And try to populate the tables with the given datasets"""
    with engine.connect() as connection:
        if not engine.dialect.has_table(connection, "recipe"):
            Base.metadata.create_all(engine)

        _load_initial_datasets(connection)
        connection.commit()


initialize_database()
