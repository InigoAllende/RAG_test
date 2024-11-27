from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str

    INITIAL_DATA_PATH: str


settings = Settings()
