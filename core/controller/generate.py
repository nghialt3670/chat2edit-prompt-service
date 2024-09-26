import time
import traceback
from typing import List

from core.controller.execute import execute
from core.controller.helpers import extract_thinking_commands
from core.controller.prompt import HELPER_PROMPT, create_prompt
from core.llms.llm import LLM
from core.providers.provider import Provider
from models.db.chat_phase import ChatPhase
from models.db.context_message import ContextMessage
from models.db.prompt_phase import PromptPhase

MAX_HELPS = 2


async def generate(
    request: ContextMessage,
    phases: List[ChatPhase],
    llm: LLM,
    provider: Provider,
    max_prompt_phases: int,
) -> ChatPhase:
    new_phase = ChatPhase(request=request)

    while len(new_phase.prompt_phases) < max_prompt_phases:
        prompt_phase = PromptPhase()
        new_phase.prompt_phases.append(prompt_phase)

        prompt = create_prompt(
            functions=provider.get_functions(),
            exemplars=provider.get_exemplars(),
            phases=phases + [new_phase],
        )
        prompt_messages = [prompt]
        commands = None

        while not commands and len(prompt_messages) < MAX_HELPS:
            try:
                start = time.time()
                llm_response = await llm(prompt_messages)
                prompt_messages.append(llm_response)
                prompt_phase.responses.append(llm_response)
                prompt_phase.durations.append(time.time() - start)
            except Exception:
                prompt_phase.tracebacks.append(traceback.format_exc())
                break

            try:
                _, commands = extract_thinking_commands(prompt_phase.responses[-1])
            except Exception:
                prompt_phase.tracebacks.append(traceback.format_exc())
                prompt_messages.append(HELPER_PROMPT)

        if not commands:
            break

        prompt_phase.execution = await execute(commands, provider)

        if prompt_phase.execution.response:
            new_phase.response = prompt_phase.execution.response
            break

    return new_phase
