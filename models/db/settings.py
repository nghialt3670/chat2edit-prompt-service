from pydantic import BaseModel, Field

from models.language import Language
from models.llm import LLM
from models.provider import Provider


class Settings(BaseModel):
    llm: LLM = Field(default=LLM.GEMINI_1_5_FLASH)
    language: Language = Field(default=Language.EN)
    provider: Provider = Field(default=Provider.FABRIC)
    text_max_length: int = Field(ge=100, lt=500, default=200)
    max_attachments: int = Field(ge=1, lt=10, default=5)
    max_chat_phases: int = Field(ge=10, le=20, default=15)
    max_prompt_phases: int = Field(ge=1, le=5, default=3)

    class Config:
        use_enum_values = True
