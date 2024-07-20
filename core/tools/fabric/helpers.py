from typing import Iterable, List

from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.schemas.fabric.fabric_object import FabricObject


def get_object_idxs(canvas: FabricCanvas, objects: List[FabricObject]) -> List[int]:
    return [idx := canvas.objects.index(obj) for obj in objects if idx != -1]
