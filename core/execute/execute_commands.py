import traceback
from typing import Any, Dict, Iterable

from chat2edit.models.exec_message import ExecMessage
from chat2edit.models.exec_signal import ExecSignal
from chat2edit.providers.provider import Provider
from logger.loggers import CONSOLE_LOGGER

EXEC_ESCAPE_STATUSES = {"warning", "error"}
DEFAULT_SIGNAL = ExecSignal("info", "Commands executed successfully.")


def execute_commands(
    commands: Iterable[str],
    context: Dict[str, Any],
    providers: Iterable[Provider],
) -> ExecMessage:
    functions_context = create_function_context(providers)
    exec_context = {**context, **functions_context}
    signal = DEFAULT_SIGNAL
    executed_commands = []
    for command in commands:
        executed_commands.append(command)
        try:
            exec(command, {}, exec_context)
        except Exception as e:
            CONSOLE_LOGGER.error(traceback.format_exc())
            signal = ExecSignal(status="error", text=str(e))
            break
        for provider in providers:
            provider_signal = provider.get_signal()
            if provider_signal:
                signal = provider_signal
                provider.clear_signal()
                break
        if signal.status in EXEC_ESCAPE_STATUSES:
            break
    ret_context = {
        name: value
        for name, value in exec_context.items()
        if name not in functions_context
    }
    return ExecMessage(
        status=signal.status,
        text=signal.text,
        context=ret_context,
        executed_commands=executed_commands,
        attachments=signal.attachments,
        response=signal.response,
    )


def create_function_context(providers: Iterable[Provider]) -> Dict[str, Any]:
    functions_context = {}
    for provider in providers:
        functions_context.update(
            {func.__name__: func for func in provider.get_functions()}
        )
    return functions_context
