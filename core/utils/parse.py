import ast
from typing import List


def parse_program(program_str: str) -> List[str]:
    tree = ast.parse(program_str)
    blocks = []
    for node in tree.body:
        code = ast.unparse(node)
        blocks.append(code)
    return blocks
