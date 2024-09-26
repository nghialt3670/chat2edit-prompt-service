import os

from dotenv import load_dotenv

from schemas.env_schema import EnvSchema

load_dotenv()

ENV = EnvSchema(
    MONGO_URI=os.getenv("MONGO_URI"),
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
    GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY"),
    ML_SERVICE_API_BASE_URL=os.getenv("ML_SERVICE_API_BASE_URL"),
    ML_SERVICE_API_VERSION=os.getenv("ML_SERVICE_API_VERSION"),
    ATTACHMENT_SERVICE_API_BASE_URL=os.getenv("ATTACHMENT_SERVICE_API_BASE_URL"),
)
