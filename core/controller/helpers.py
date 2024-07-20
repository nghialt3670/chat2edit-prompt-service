from typing import Any, List, Tuple


def get_id(obj: Any) -> str:
    raise NotImplementedError()


def extract_thinking_commands(text: str) -> Tuple[str, List[str]]:
    raise NotImplementedError()
