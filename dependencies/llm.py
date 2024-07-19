from core.llms.google_llm import GoogleLLM
from core.llms.openai_llm import OpenAILLM


def get_llm():
    return GoogleLLM("gemini-1.5-flash")
