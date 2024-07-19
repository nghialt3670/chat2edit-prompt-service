import inspect
from typing import Any, Callable, Iterable, List, Optional, Union

from chat2edit.models.chat_cycle import ChatCycle
from chat2edit.models.chat_message import ChatMessage
from chat2edit.models.exec_message import ExecMessage

OBSERVATION_TEMPLATE = "observation: {observation}\n"
THINKING_TEMPLATE = "thinking: {thinking}\n"
COMMANDS_TEMPLATE = "commands:\n{commands}\n"


def create_prompt(
    main_cycles: Iterable[ChatCycle],
    functions: Optional[Callable],
    exemplars: Optional[Iterable[Iterable[ChatCycle]]] = None,
) -> Any:
    prompt = ""
    if functions is not None:
        function_declarations = _create_function_declarations(functions)
        prompt += _format_function_declarations(function_declarations)
    if exemplars is not None:
        prompt += _format_exemplars(exemplars)
    prompt += _format_main_cycles(main_cycles)
    return prompt


def _format_main_cycles(main_cycles: Iterable[ChatCycle]) -> str:
    formatted_main_flow = "Conv between you, user and system:\n"
    formatted_main_flow += _format_chat_cycles(main_cycles)
    formatted_main_flow += "\n...\n"
    formatted_main_flow += "Produce your next thinking and commands:"
    return formatted_main_flow


def _create_function_declarations(functions: Iterable[Callable]) -> List[str]:
    return [
        f"{func.__name__}{inspect.signature(func)}".replace("~", "")
        for func in functions
    ]


def _format_function_declarations(function_declarations: Iterable[str]) -> str:
    formatted_function_declarations = "Only use these functions:\n"
    formatted_function_declarations += "\n".join(function_declarations)
    formatted_function_declarations += "\n\n"
    return formatted_function_declarations


def _format_exemplars(exemplars: Iterable[Iterable[ChatCycle]]) -> str:
    formatted_exemplars = ""
    for i, exemplar in enumerate(exemplars):
        formatted_exemplars += f"Example {i + 1}:\n"
        formatted_exemplars += _format_chat_cycles(exemplar)
        formatted_exemplars += "\n"

    return formatted_exemplars


def _format_observation(message: Union[ChatMessage, ExecMessage]) -> str:
    observation = None
    if isinstance(message, ChatMessage):
        observation = f"user_request(text='{message.text}', images=[{', '.join(message.attachment_varnames)}])"
    else:
        if message.attachment_varnames:
            observation = f"system_{message.status}('{message.text}', images=[{', '.join(message.attachment_varnames)}])"
        else:
            observation = f"system_{message.status}('{message.text}')"
    return OBSERVATION_TEMPLATE.format(observation=observation)


def _format_thinking(thinking: str) -> str:
    return THINKING_TEMPLATE.format(thinking=thinking)


def _format_commands(commands: Iterable[str]) -> str:
    commands = "\n".join(commands)
    return COMMANDS_TEMPLATE.format(commands=commands)


def _format_chat_cycles(chat_cycles: Iterable[ChatCycle]) -> str:
    formatted_cycles = ""
    for chat_cycle in chat_cycles:
        formatted_cycles += _format_observation(chat_cycle.req_message)
        for prompt_cycle in chat_cycle.prompt_cycles:
            thinking = prompt_cycle.thinking
            commands = prompt_cycle.exec_message.executed_commands
            formatted_cycles += _format_thinking(thinking)
            formatted_cycles += _format_commands(commands)
            if not prompt_cycle.exec_message.response:
                formatted_cycles += _format_observation(prompt_cycle.exec_message)
    return formatted_cycles
