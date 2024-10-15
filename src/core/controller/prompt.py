import inspect
from typing import Callable, Iterable

from core.controller.helpers import extract_thinking_commands
from models.phase import ChatPhase, Message

PROMPT_TEMPLATE = """Only use these functions:

{functions}

Some examples:

{exemplars}

Follow the examples to produce your next thinking and commands (give answer in plain text):

{phases}
"""

HELPER_PROMPT = """
Please response in this format:
THINKING: <YOUR_THINKING>
COMMANDS:
<COMMAND_0>
<COMMAND_1>
...
<COMMAND_n>"""


def create_prompt(
    functions: Iterable[Callable],
    exemplars: Iterable[ChatPhase],
    phases: Iterable[ChatPhase],
) -> str:
    return PROMPT_TEMPLATE.format(
        functions="\n".join(format_function(f) for f in functions),
        exemplars="\n\n".join(
            f"Example {i + 1}:\n{format_phase(phase)}"
            for i, phase in enumerate(exemplars)
        ),
        phases="\n".join(format_phase(p) for p in phases),
    )


def format_function(function: Callable) -> str:
    return f"async def {function.__name__}{inspect.signature(function)}".replace("~", "")


def format_observation(message: Message) -> str:
    src, type, text, varnames, *rest = message.__dict__.values()
    return (
        f'{src}_{type}("{text}"'
        + (f', attachments=[{", ".join(varnames)}]' if varnames else "")
        + ")"
    )


def format_phase(phase: ChatPhase) -> str:
    observation = format_observation(phase.request)
    result = f"OBSERVATION: {observation}\n"

    for prompt_phase in phase.prompt_phases:
        if not prompt_phase.answers:
            break

        thinking, _ = extract_thinking_commands(prompt_phase.answers[-1])
        commands = prompt_phase.execution.commands
        result += f"THINKING: {thinking}\n"
        result += "COMMANDS:\n" + "\n".join(commands) + "\n"

        if feedback := prompt_phase.execution.feedback:
            observation = format_observation(feedback)
            result += f"OBSERVATION: {observation}\n"

    return result[:-1]
