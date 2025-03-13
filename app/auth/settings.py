from pydantic import ConfigDict
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    model_config = ConfigDict(from_attributes=True, env_prefix="AUTH_")

    ALGORITHM: str = os.getenv("ALGORITHM_TOKEN")
    SECRET_KEY: str = os.getenv("SECRET_KEY_TOKEN")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


settings = Settings()
