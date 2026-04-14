from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "super-secret-key-for-local-dev"
    ALGORITHM: str = "HS256"


settings = Settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
