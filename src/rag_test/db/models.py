from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Recipe(Base):
    """ Ideally recipes would use a different primary key, but it was simpler to use the title in order to avoid duplicates from the dataset."""
    __tablename__ = "recipe"

    title = Column(String, primary_key=True, nullable=False)
    ingredients = Column(String, nullable=False)
    instructions = Column(String, nullable=False)
