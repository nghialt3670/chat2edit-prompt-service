import inspect
from typing import Any, Dict, Iterable

from core.providers.exec_signal import ExecSignal
from core.providers.provider import Provider
from database.models.conversation.exec_message import ExecMessage


FUNCTION = """
async def __temp_func(context):
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
    async_func_names = [f.__name__ for f in provider.get_functions() if inspect.iscoroutinefunction(f)]
    
    for command in commands:
        executed_commands.append(command)
        
        for name in async_func_names:
            if name in command:
                command = command.replace(name, f"await {name}")
                break
            
        for k in context.keys():
            if k in command:
                command = command.replace(k, f"context['{k}']")
                
        try:
            local_vars = {}
            exec(FUNCTION.format(command=command), globals(), local_vars)
            temp_func = local_vars["__temp_func"]
            await temp_func(context)
            
        except Exception as e:
            signal = ExecSignal(status="error", text=str(e))
            break

        signal = provider.get_signal() 
        provider.clear_signal()

        if signal.status in {"warning", "error"}:
            break
    
    return ExecMessage(
        status=signal.status,
        commands=executed_commands,
        text=signal.text,
        varnames=signal.varnames,
        response=signal.response,
    )
