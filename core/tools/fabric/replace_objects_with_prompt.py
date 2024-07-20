from typing import List

from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.schemas.fabric.fabric_object import FabricObject


def replace_objects_with_prompt(
    canvas: FabricCanvas, objects: List[FabricObject], prompt: str
) -> FabricCanvas:
    raise NotImplementedError()
