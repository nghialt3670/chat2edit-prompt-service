import os
from typing import Iterable, Optional

import google.generativeai as genai
from core.llms.llm import LLM
from google.generativeai import GenerationConfig

SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]


class GoogleLLM(LLM):
    def __init__(
        self,
        model_name: str,
        *,
        system_message: Optional[str] = None,
        stop_words: Optional[Iterable[str]] = None,
        max_out_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[int] = None,
    ) -> None:
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.generation_config = GenerationConfig(
            stop_sequences=stop_words,
            max_output_tokens=max_out_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
        )
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config,
            system_instruction=system_message,
        )

    async def __call__(self, messages: Iterable[str]) -> str:
        if len(messages) % 2 == 0:
            raise ValueError("Messages length must be odd")
        history = [
            {"role": "user" if i % 2 == 0 else "model", "parts": message}
            for i, message in enumerate(messages[:-1])
        ]
        chat = self.model.start_chat(history=history)
        response = await chat.send_message_async(
            messages[-1], safety_settings=SAFETY_SETTINGS
        )
        return response.text
