import warnings
from copy import deepcopy
from typing import List

from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.schemas.fabric.fabric_image import FabricImage
from core.schemas.fabric.fabric_object import FabricObject
from core.tools.fabric.helpers import get_object_idxs
from core.tools.fabric.inpaint_objects import inpaint_objects


async def remove_objects(
    canvas: FabricCanvas, objects: List[FabricObject]
) -> FabricCanvas:
    object_idxs = get_object_idxs(canvas, objects)
    canvas = deepcopy(canvas)

    not_inpainted_objects = []
    for i in object_idxs:
        obj = canvas.objects[i]
        canvas.objects.pop(i)
        if isinstance(obj, FabricImage) and not obj.inpainted:
            not_inpainted_objects.append(obj)

    await inpaint_objects(canvas, not_inpainted_objects)
    return canvas
