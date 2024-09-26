from pydantic import BaseModel, Field


class EnvSchema(BaseModel):
    MONGO_URI: str = Field(...)
    OPENAI_API_KEY: str = Field(...)
    GOOGLE_API_KEY: str = Field(...)
    ML_SERVICE_API_BASE_URL: str = Field(...)
    ML_SERVICE_API_VERSION: str = Field(...)
    ATTACHMENT_SERVICE_API_BASE_URL: str = Field(...)
