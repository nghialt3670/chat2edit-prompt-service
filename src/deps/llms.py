from core.llms.google_llm import GoogleLLM
from core.llms.llm import LLM
from core.llms.openai_llm import OpenAILLM
from schemas.llm import LLM as LLMType


def get_llm(type: LLMType) -> LLM:
    if type == "gemini-1.5-flash":
        return GoogleLLM("gemini-1.5-flash")

    if type == "gpt-3.5-turbo":
        return OpenAILLM("gpt-3.5-turbo")

    raise ValueError(f"Invalid LLM type: {type}")
