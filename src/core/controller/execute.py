import ast
import inspect
import textwrap
import time
import traceback
from typing import Any, Coroutine, Dict, Iterable, Tuple

from core.providers.provider import Provider
from models.phase import Execution, Message

DEFAULT_FEEDBACK = Message(
    src="system", type="info", text="Commands executed successfully"
)

WRAPPER_FUNCTION_TEMPLATE = """
async def __wrapper_func(__context):
{command}
    
    for k, v in locals().items():
        if k != "__context":
            __context[k] = v
"""


async def execute(
    commands: Iterable[str],
    provider: Provider,
) -> Execution:
    execution = Execution(feedback=DEFAULT_FEEDBACK)
    provider.set_execution(execution)
    context_dict = provider.get_context_dict()

    for cmd in commands:
        start = time.time()
        try:
            processed_cmd = preprocess_command(cmd, context_dict)
            function = create_wrapper_function(WRAPPER_FUNCTION_TEMPLATE, processed_cmd)
            await function(context_dict)

        except Exception as e:
            execution.feedback = Message(src="system", type="error", text=str(e))
            execution.traceback = traceback.format_exc()

        execution.durations.append(time.time() - start)
        execution.commands.append(cmd)

        if execution.feedback.type != "info" or execution.response:
            break

    return execution


def adjust_offsets(command: str, start: int, end: int) -> Tuple[int, int]:
    # Convert the command to bytes and find the corresponding byte positions
    command_bytes = command.encode("utf-8")
    start_bytes = len(command_bytes[:start].decode("utf-8"))
    end_bytes = len(command_bytes[:end].decode("utf-8"))

    return start_bytes, end_bytes


def preprocess_command(
    command: str, context: Dict[str, Any], context_name: str = "__context"
) -> str:
    def replace_var(var):
        # If it is a defined coroutine function (already in context)
        if var in context and inspect.iscoroutinefunction(context[var]):
            return f"await {context_name}['{var}']"

        return f"{context_name}['{var}']"

    processed_command = command
    while True:
        replacements = []
        for node in ast.walk(ast.parse(processed_command, mode="exec")):
            if not isinstance(node, ast.Name) or node.id == context_name:
                continue

            # Adjust the offsets when the commands contains utf-8 characters
            start, end = adjust_offsets(command, node.col_offset, node.end_col_offset)
            replacements.append((start, end, replace_var(processed_command[start:end])))

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
) -> Coroutine:
    local_vars = {}
    exec(
        template.format(command=textwrap.indent(command, "    ")),
        globals(),
        local_vars,
    )
    return local_vars[func_name]
