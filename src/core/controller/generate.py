import time
import traceback
from typing import List

from core.controller.execute import execute
from core.controller.helpers import extract_thinking_commands
from core.controller.prompt import HELPER_PROMPT, create_prompt
from core.llms.llm import LLM
from core.providers.provider import Provider
from models.phase import ChatPhase, Message, PromptPhase

MAX_HELPS = 2


async def generate(
    request: Message,
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
            functions=provider.get_prompt_functions(),
            exemplars=provider.get_exemplars(),
            phases=phases + [new_phase],
        )
        
        prompt_phase.prompts.append(prompt)
        messages = [prompt]
        commands = None

        while not commands and len(messages) < MAX_HELPS:
            try:
                start = time.time()
                answer = await llm(messages)
                end = time.time()
                
                duration = end - start
                
                prompt_phase.durations.append(duration)
                prompt_phase.answers.append(answer)
                
                messages.append(answer)
            except Exception:
                prompt_phase.tracebacks.append(traceback.format_exc())
                break

            try:
                _, commands = extract_thinking_commands(prompt_phase.answers[-1])
            except Exception:
                prompt_phase.tracebacks.append(traceback.format_exc())
                prompt_phase.prompts.append(HELPER_PROMPT)
                messages.append(HELPER_PROMPT)

        if not commands:
            break

        prompt_phase.execution = await execute(commands, provider)

        if prompt_phase.execution.response:
            new_phase.response = prompt_phase.execution.response
            break

    return new_phase
