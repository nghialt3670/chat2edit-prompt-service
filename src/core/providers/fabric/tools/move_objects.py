from copy import deepcopy
from typing import List, Tuple

from core.providers.fabric.models.fabric_canvas import FabricCanvas
from core.providers.fabric.models.fabric_object import FabricObject
from core.providers.fabric.tools.helpers import get_object_idxs
from core.providers.fabric.tools.inpaint_objects import inpaint_objects


async def move_objects(
    canvas: FabricCanvas, objects: List[FabricObject], dest: Tuple[int, int]
) -> FabricCanvas:
    object_idxs = get_object_idxs(canvas, objects)
    canvas = deepcopy(canvas)

    await inpaint_objects(canvas, object_idxs)

    for i in object_idxs:
        obj = canvas.objects[i]
        obj.left = dest[0]
        obj.top = dest[1]

    return canvas
