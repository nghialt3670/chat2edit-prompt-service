from core.llms.google_llm import GoogleLLM
from core.llms.llm import LLM
from core.llms.openai_llm import OpenAILLM
from models.llm import LLM as LLMType


def get_llm(type: LLMType) -> LLM:
    if type == LLMType.GEMINI_1_5_FLASH:
        return GoogleLLM("gemini-1.5-flash")

    if type == LLMType.GPT_3_5_TURBO:
        return OpenAILLM("gpt-3.5-turbo")

    raise ValueError(f"Invalid LLM type: {type}")
