from typing import Iterable, List

from core.providers.fabric.models.fabric_canvas import FabricCanvas
from core.providers.fabric.models.fabric_object import FabricObject


def get_object_idxs(canvas: FabricCanvas, objects: List[FabricObject]) -> List[int]:
    object_idxs = [canvas.objects.index(obj) for obj in objects]
    return [idx for idx in object_idxs if idx != -1]
