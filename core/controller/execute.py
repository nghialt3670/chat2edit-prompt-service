import ast
import inspect
import re
import textwrap
import traceback
from typing import Any, Coroutine, Dict, Iterable

from core.providers import ExecSignal, Provider
from db.models import ExecMessage

WRAPPER_FUNCTION_TEMPLATE = """
async def __wrapper_func(context):
{command}
    
    for k, v in locals().items():
        if k != "context":
            context[k] = v
"""


async def execute(
    commands: Iterable[str],
    context: Dict[str, Any],
    provider: Provider,
) -> ExecMessage:
    signal = None
    executed_commands = []
    provider.set_context(context)

    for command in commands:
        executed_commands.append(command)
        command = preprocess_command(command, context)

        try:
            wrapper_func = create_wrapper_function(WRAPPER_FUNCTION_TEMPLATE, command)
            await wrapper_func(context)

        except Exception as e:
            print(traceback.format_exc())
            signal = ExecSignal(status="error", text=str(e))
            break

        signal = provider.get_signal()
        provider.clear_signal()

        if signal and signal.status in {"warning", "error"}:
            break

    return ExecMessage(
        status=signal.status,
        commands=executed_commands,
        text=signal.text,
        varnames=signal.varnames,
        response=signal.response,
    )


def preprocess_command(command: str, context: Dict[str, Any]) -> str:
    pattern = re.compile(r"\b(\w+)\b")
    parsed_command = ast.parse(command, mode="exec")
    command_vars = {
        node.id for node in ast.walk(parsed_command) if isinstance(node, ast.Name)
    }

    def replace_var(match):
        varname = match.group(1)

        # If not actually a variable name (like argument name,...)
        if not varname in command_vars:
            return varname

        # If it is a defined coroutine function (already in context)
        if varname in context and inspect.iscoroutinefunction(context[varname]):
            return f"await context['{varname}']"

        return f"context['{varname}']"

    replaced_command = pattern.sub(replace_var, command)
    return replaced_command


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
