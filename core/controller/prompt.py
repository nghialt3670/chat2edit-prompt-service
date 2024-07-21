import inspect
from typing import Callable, Iterable

from core.controller.helpers import extract_thinking_commands
from database.models.conversation.chat_cycle import ChatCycle

PROMPT_TEMPLATE = """
Only use these functions:
{functions}

Some examples:
{exemplars}

Follow the examples to produce your next thinking and commands (give answer in plain text):
{chat_cycles}
"""


def create_prompt(
    cycles: Iterable[ChatCycle],
    functions: Iterable[Callable],
    exemplars: str,
) -> str:
    return PROMPT_TEMPLATE.format(
        functions="\n".join(
            f"{f.__name__}{inspect.signature(f)}".replace("~", "") for f in functions
        ),
        exemplars=exemplars,
        chat_cycles="\n".join(_format_chat_cycles(c) for c in cycles),
    )


def _format_chat_cycles(cycle: ChatCycle) -> str:
    request = cycle.request
    result = ""
    if request.varnames:
        result += f"observation: user_request(text='{request.text}', variables=[{', '.join(request.varnames)}])\n"
    else:
        result += f"observation: user_request(text='{request.text}')\n"
    for prompt_cycle in cycle.prompt_cycles:
        thinking, commands = extract_thinking_commands(prompt_cycle.answer)
        result += f"thinking: {thinking}\n"
        result += "commands:\n{}\n".format("\n".join(commands))

        exec_message = prompt_cycle.exec_message
        if exec_message.response:
            break

        if exec_message.varnames:
            result += f"observation: sys_{exec_message.status}(text='{exec_message.text}', variables=[{', '.join(exec_message.varnames)}])"
        else:
            result += (
                f"observation: sys_{exec_message.status}(text='{exec_message.text}')"
            )

    return result
