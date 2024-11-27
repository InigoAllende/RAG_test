FROM python:3.12-slim-bookworm

# Install pre-requisites
RUN apt-get update \
    && apt-get install -y libpq-dev gcc
RUN pip install poetry

# Copy production code to container
COPY poetry.lock pyproject.toml /app/
COPY ./src /app/src

WORKDIR /app

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

ENV PYTHONPATH "${PYTHONPATH}:/app/src"

CMD uvicorn src.main:app