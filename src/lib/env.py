import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Environment(BaseModel):
    MONGO_URI: str = Field(...)
    OPENAI_API_KEY: str = Field(...)
    GOOGLE_API_KEY: str = Field(...)
    ML_SERVICE_API_BASE_URL: str = Field(...)
    ML_SERVICE_API_VERSION: str = Field(...)


ENV = Environment(
    MONGO_URI=os.getenv("MONGO_URI"),
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
    GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY"),
    ML_SERVICE_API_BASE_URL=os.getenv("ML_SERVICE_API_BASE_URL"),
    ML_SERVICE_API_VERSION=os.getenv("ML_SERVICE_API_VERSION"),
)
