import ast
import textwrap
import time
import traceback
from typing import Callable, Iterable, Tuple

from core.providers.provider import UNEXPECTED_ERROR_OCCURRED_TEMPLATE, Provider
from models.phase import Execution, Message

DEFAULT_FEEDBACK = Message(
    src="system", type="info", text="Commands executed successfully."
)

UNEXPECTED_ERROR_OCCURRED_TEMPLATE = (
    "Unexpected error occurred while executing `{c}` command: `{e}`."
)

WRAPPER_FUNCTION_TEMPLATE = """
async def __wrapper_func(__ctx__):
{command}
    
    for k, v in locals().items():
        if k != "__ctx__":
            __ctx__[k] = v
"""


async def execute(
    commands: Iterable[str],
    provider: Provider,
) -> Execution:
    execution = Execution(feedback=DEFAULT_FEEDBACK)
    context = provider.get_context()

    for cmd in commands:
        start = time.time()
        end = None

        try:
            processed_cmd = preprocess_command(cmd)
            function = create_wrapper_function(WRAPPER_FUNCTION_TEMPLATE, processed_cmd)

            await function(context)

            execution.feedback = provider.get_feedback() or DEFAULT_FEEDBACK
            execution.response = provider.get_response()

            provider.clear_feedback()

        except Exception as e:
            feedback_text = UNEXPECTED_ERROR_OCCURRED_TEMPLATE.format(c=cmd, e=e)
            error_feedback = Message(src="system", type="error", text=feedback_text)
            execution.feedback = provider.get_feedback() or error_feedback
            execution.traceback = traceback.format_exc()

        finally:
            end = time.time()

        duration = end - start
        execution.commands.append(cmd)
        execution.durations.append(duration)

        if execution.feedback.type != "info" or execution.response:
            break

    return execution


def adjust_offsets(command: str, start: int, end: int) -> Tuple[int, int]:
    # Convert the command to bytes and find the corresponding byte positions
    command_bytes = command.encode("utf-8")
    start_bytes = len(command_bytes[:start].decode("utf-8"))
    end_bytes = len(command_bytes[:end].decode("utf-8"))

    return start_bytes, end_bytes


def preprocess_command(command: str, context_name: str = "__ctx__") -> str:
    processed_command = command
    while True:
        replacements = []
        for node in ast.walk(ast.parse(processed_command, mode="exec")):
            if not isinstance(node, ast.Name) or node.id == context_name:
                continue

            # Adjust the offsets when the commands contains utf-8 characters
            start, end = adjust_offsets(command, node.col_offset, node.end_col_offset)

            varname = processed_command[start:end]
            processed_varname = f"{context_name}['{varname}']"

            replacements.append((start, end, processed_varname))

        if not replacements:
            break

        # Apply replacements in reverse order to avoid messing up indices
        for start, end, replacement in sorted(replacements, reverse=True):
            processed_command = (
                processed_command[:start] + replacement + processed_command[end:]
            )

    return processed_command


def create_wrapper_function(
    template: str, command: str, func_name: str = "__wrapper_func"
) -> Callable:
    local_vars = {}
    exec(
        template.format(command=textwrap.indent(command, "    ")),
        globals(),
        local_vars,
    )
    return local_vars[func_name]
