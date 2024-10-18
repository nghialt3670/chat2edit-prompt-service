import ast
from multiprocessing import context
import textwrap
import time
import traceback
from typing import Any, Callable, Dict, Iterable, Tuple

from core.providers.provider import UNEXPECTED_ERROR_OCCURRED_TEMPLATE, Provider
from models.phase import Execution, Message

DEFAULT_FEEDBACK = Message(
    src="system", type="info", text="Commands executed successfully."
)

UNEXPECTED_ERROR_OCCURRED_TEMPLATE = (
    "Unexpected error occurred while executing command `{c}`: `{t}: {e}`."
)

WRAPPER_FUNCTION_TEMPLATE = """
async def __wrapper_func__(__ctx__):
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
            processed_cmd = preprocess_command(cmd, context)
            function = create_wrapper_function(WRAPPER_FUNCTION_TEMPLATE, processed_cmd)

            await function(context)

            execution.feedback = provider.get_feedback() or DEFAULT_FEEDBACK
            execution.response = provider.get_response()

            provider.clear_feedback()

        except Exception as e:
            feedback_text = UNEXPECTED_ERROR_OCCURRED_TEMPLATE.format(
                c=cmd, t=type(e).__name__, e=e
            )
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


class NameCollector(ast.NodeVisitor):
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.names = []
    
    def visit_Name(self, node):
        if node.id in self.context:
            self.names.append(node.id)
            
        self.generic_visit(node)


def preprocess_command(
    command: str, context: Dict[str, Any], context_name: str = "__ctx__"
) -> str:
    processed_command = command
    replacements = []
    curr_idx = 0
    
    tree = ast.parse(command, mode="exec")
    collector = NameCollector(context)
    collector.visit(tree)

    for name in collector.names:
        start = processed_command.find(name, curr_idx)
        
        if start == -1:
            continue

        curr_idx = start + len(name)
        varname = processed_command[start:curr_idx]
        processed_varname = f"{context_name}['{varname}']"
        replacements.append((start, curr_idx, processed_varname))

    # Apply replacements in reverse order to avoid messing up indices
    for start, end, replacement in sorted(replacements, reverse=True):
        processed_command = (
            processed_command[:start] + replacement + processed_command[end:]
        )

    return processed_command


def create_wrapper_function(
    template: str, command: str, func_name: str = "__wrapper_func__"
) -> Callable:
    local_vars = {}
    exec(
        template.format(command=textwrap.indent(command, "    ")),
        globals(),
        local_vars,
    )
    return local_vars[func_name]
