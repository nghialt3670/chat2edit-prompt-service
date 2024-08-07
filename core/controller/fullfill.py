from typing import Any, Dict, List, Optional

from core.controller.execute import execute
from core.controller.helpers import extract_thinking_commands
from core.controller.prompt import create_prompt
from core.llms import LLM
from core.providers import Provider
from db.models import ChatCycle, ChatMessage, PromptCycle


async def fullfill(
    cycles: List[ChatCycle],
    context: Dict[str, Any],
    request: ChatMessage,
    llm: LLM,
    provider: Provider,
    max_prompts: int = 4,
    helper_prompt: Optional[str] = None,
) -> ChatCycle:
    curr_cycle = ChatCycle(request=request)

    functions = provider.get_functions()
    exemplars = provider.get_exemplars()

    cycles.append(curr_cycle)

    prompt_count = 0
    while prompt_count < max_prompts:
        prompt_cycle = PromptCycle()
        prompt = create_prompt(cycles, functions, exemplars)
        messages = [prompt]
        thinking = None
        commands = None

        while (not thinking or not commands) and prompt_count < max_prompts:
            try:
                prompt_cycle.answer = await llm(messages)
                prompt_count += 1
            except Exception:
                break
            try:
                thinking, commands = extract_thinking_commands(prompt_cycle.answer)
            except Exception:
                if helper_prompt:
                    messages.append(helper_prompt)
                else:
                    break

        if not thinking or not commands:
            curr_cycle.prompt_cycles.append(prompt_cycle)
            break

        exec_message = await execute(commands, context, provider)

        prompt_cycle.exec_message = exec_message
        curr_cycle.prompt_cycles.append(prompt_cycle)
        curr_cycle.response = exec_message.response

        if curr_cycle.response:
            break

    return curr_cycle
