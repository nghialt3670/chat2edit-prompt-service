import os
from typing import Iterable, List, Optional

import openai

from core.llms.llm import LLM

openai.api_key = os.getenv("OPENAI_API_KEY")


class OpenAILLM(LLM):
    def __init__(
        self,
        model_name: str,
        *,
        system_message: Optional[str] = None,
        stop_words: Optional[Iterable[str]] = None,
        max_out_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[int] = None,
    ) -> None:
        self.model_name = model_name
        self.system_message = system_message
        self.stop_words = stop_words
        self.max_out_tokens = max_out_tokens
        self.temperature = temperature
        self.top_p = top_p

    async def __call__(self, messages: List[str]) -> str:
        if len(messages) % 2 == 0:
            raise ValueError("Messages length must be odd")
        
        input_messages = self._create_input_messages(messages)
        response = await openai.ChatCompletion.acreate(
            messages=input_messages,
            model=self.model_name,
            max_tokens=self.max_out_tokens,
            stop=self.stop_words,
            top_p=self.top_p,
        )
        
        return response.choices[0].message.content

    def _create_input_messages(self, messages: Iterable[str]) -> List[str]:
        input_messages = []
        
        if self.system_message is not None:
            input_messages.append({"role": "system", "content": self.system_message})
            
        for prompt, answer in zip(messages[::2], messages[1::2]):
            input_messages.append({"role": "user", "content": prompt})
            input_messages.append({"role": "assistant", "content": answer})
            
        input_messages.append({"role": "user", "content": messages[-1]})
        
        return input_messages
