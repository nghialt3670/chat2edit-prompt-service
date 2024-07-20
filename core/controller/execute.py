from typing import Any, Dict, Iterable

from core.providers.exec_signal import ExecSignal
from core.providers.provider import Provider
from database.models.conversation.exec_message import ExecMessage

EXEC_ESCAPE_STATUSES = {"warning", "error"}
DEFAULT_SIGNAL = ExecSignal(status="info", text="Commands executed successfully.")


def execute(
    commands: Iterable[str],
    context: Dict[str, Any],
    provider: Provider,
) -> ExecMessage:
    signal = DEFAULT_SIGNAL
    executed_commands = []

    for command in commands:
        executed_commands.append(command)
        try:
            exec(command, {}, context)
        except Exception as e:
            signal = ExecSignal(status="error", text=str(e))
            break

        signal = provider.get_signal()
        context.update(provider.get_context())

        if signal.status in {"warning", "error"}:
            break

    return ExecMessage(
        status=signal.status,
        text=signal.text,
        commands=executed_commands,
        varnames=signal.varnames,
        response=signal.response,
    )
