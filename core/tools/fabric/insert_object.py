from copy import deepcopy
from typing import Tuple

from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.schemas.fabric.fabric_object import FabricObject


def insert_object(
    canvas: FabricCanvas, obj: FabricObject, dest: Tuple[int, int]
) -> FabricCanvas:
    canvas = deepcopy(canvas)
    copied_obj = deepcopy(obj)
    copied_obj.left = dest[0]
    copied_obj.top = dest[1]
    canvas.objects.append(copied_obj)
    return canvas
