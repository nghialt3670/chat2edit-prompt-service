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
    idxs_to_remove = get_object_idxs(canvas, objects)
    canvas = deepcopy(canvas)

    not_inpainted_objects = [
        obj
        for obj, idx in enumerate(canvas.objects)
        if idx in set(idxs_to_remove)
        and isinstance(obj, FabricImage)
        and not obj.inpainted
    ]
    canvas.objects = [
        obj for idx, obj in enumerate(canvas.objects) if idx not in set(idxs_to_remove)
    ]
    await inpaint_objects(canvas, not_inpainted_objects)
    return canvas
