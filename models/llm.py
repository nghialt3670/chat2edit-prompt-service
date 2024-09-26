from enum import Enum


class LLM(str, Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
