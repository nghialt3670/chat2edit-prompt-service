import ast
from typing import List, Tuple


def extract_thinking_commands(text: str) -> Tuple[str, List[str]]:
    text = text.replace("thinking:", "$")
    text = text.replace("commands:", "$")
    text = text.replace("observation:", "$")
    parts = [part.strip() for part in text.split("$")]
    parts = [part for part in parts if part]
    thinking, commands = parts[0], parts[1]
    return thinking, parse_program(commands)


def parse_program(program_str: str) -> List[str]:
    tree = ast.parse(program_str)
    blocks = []
    for node in tree.body:
        code = ast.unparse(node)
        blocks.append(code)
    return blocks
