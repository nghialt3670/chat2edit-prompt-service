from copy import deepcopy
from typing import List, Tuple

from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.schemas.fabric.fabric_image import FabricImage
from core.schemas.fabric.fabric_object import FabricObject
from core.tools.fabric.inpaint_objects import inpaint_objects
from core.tools.fabric.helpers import get_object_idxs


async def move_objects(
    canvas: FabricCanvas, objects: List[FabricObject], dest: Tuple[int, int]
) -> FabricCanvas:
    object_idxs = get_object_idxs(canvas, objects)
    canvas = deepcopy(canvas)

    not_inpainted_objects = []
    for i in object_idxs:
        obj = canvas.objects[i]
        obj.left = dest[0]
        obj.top = dest[1]
        if isinstance(obj, FabricImage) and not obj.inpainted:
            not_inpainted_objects.append(obj)

    await inpaint_objects(canvas, not_inpainted_objects)
    return canvas
