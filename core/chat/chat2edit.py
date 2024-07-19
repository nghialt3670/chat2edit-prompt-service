import re
import textwrap
import traceback
from typing import List, Optional, Tuple

from chat2edit.execute.execute_commands import execute_commands
from chat2edit.llms.llm import LLM
from chat2edit.models.chat_message import ChatMessage
from chat2edit.models.conv import Conv
from chat2edit.models.prompt_cycle import PromptCycle
from chat2edit.prompting.create_prompt import create_prompt
from chat2edit.utils.parse import parse_program
from chat2edit.utils.text_processing import dedent
from logger.loggers import CONSOLE_LOGGER, FILE_LOGGER

CODE_EXTRACT_PATTERN = re.compile(r"```python([\s\S]+?)```")
THINKING_AND_COMMANDS_EXTRACT_PATTERN = re.compile(
    r"(\w+):\s*(.*?)(?=\n\w+:|$)", re.DOTALL
)


class Chat2Edit:
    def __init__(
        self, llm: LLM, max_chat_cycles: int, prompt_limit: int, helper_prompt: str
    ) -> None:
        self.llm = llm
        self.max_chat_cycles = max_chat_cycles
        self.prompt_limit = prompt_limit
        self.helper_prompt = helper_prompt

    def __call__(self, req_message: ChatMessage, conv: Conv, provider: str) -> Conv:
        functions = provider.get_functions()
        exemplars = provider.get_exemplars()
        conv.add_req_message(req_message)
        if len(conv.chat_cycles) >= self.max_chat_cycles:
            exemplars = None
        prompt_count = 0
        while prompt_count < self.prompt_limit and not conv.should_terminate():
            prompt_cycle = PromptCycle()
            curr_chat_cycles = conv.get_last_complete_cycles(self.max_chat_cycles)
            prompt_cycle.prompt = create_prompt(curr_chat_cycles, functions, exemplars)
            FILE_LOGGER.info("PROMPT:\n" + prompt_cycle.prompt)
            messages = [prompt_cycle.prompt]
            while (
                not prompt_cycle.commands or not prompt_cycle.thinking
            ) and prompt_count < self.prompt_limit:
                try:
                    prompt_cycle.answer = self.llm(messages)
                    FILE_LOGGER.info("ANSWER:\n" + prompt_cycle.answer)
                    prompt_count += 1
                except Exception as e:
                    CONSOLE_LOGGER.error(traceback.format_exc())
                    prompt_cycle.set_error(str(e))
                    break
                try:
                    thinking, commands = self._extract_thinkings_and_commands(
                        prompt_cycle.answer
                    )
                    prompt_cycle.thinking = thinking
                    prompt_cycle.commands = commands
                except Exception as e:
                    CONSOLE_LOGGER.error(traceback.format_exc())
                    prompt_cycle.set_error(str(e))
                if not self.helper_prompt:
                    break
                messages.append(prompt_cycle.answer)
                messages.append(self.helper_prompt)
            if prompt_cycle.commands:
                try:
                    prompt_cycle.exec_message = execute_commands(
                        prompt_cycle.commands, conv.context, [provider]
                    )
                except Exception as e:
                    CONSOLE_LOGGER.error(traceback.format_exc())
            conv.add_prompt_cycle(prompt_cycle)
        return conv

    def _preprocess_answer(self, answer: str) -> str:
        return dedent(answer)

    def _extract_thinkings_and_commands(self, text: str) -> List[Tuple[str, List[str]]]:
        text = text.replace("thinking:", "$")
        text = text.replace("commands:", "$")
        text = text.replace("observation:", "$")
        parts = [part.strip() for part in text.split("$")]
        parts = [part for part in parts if part]
        thinking, commands = parts[0], parts[1]
        return thinking, parse_program(commands)

    def _extract_code(self, text: str) -> str:
        matches = CODE_EXTRACT_PATTERN.findall(text)
        if matches:
            return matches[0].strip()
        return text
