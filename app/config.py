from typing import  Any
from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    MONGO_INITDB_DATABASE: str

    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str
    ACCESS_TOKEN_SECRET_KEY: str

    CLIENT_ORIGIN: str

    BREVO_SENDER_EMAIL: str
    PASSWORD: str
    API_KEY: str

    FRONTEND_URL:str
    BACKEND_URL : str

    BREVO_API_KEY:str

    class Config:
        # env_file = "./.env"
        env_file = "./../../.env"

settings = Settings()  # type: ignore
