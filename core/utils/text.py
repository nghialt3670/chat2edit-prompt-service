import re


def dedent(text: str) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join([re.sub(r"^ {1,4}", "", line) for line in lines])
