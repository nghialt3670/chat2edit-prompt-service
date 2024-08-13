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

    await inpaint_objects(canvas, object_idxs)

    canvas.objects = [obj for i, obj in enumerate(canvas.objects) if i not in object_idxs]

    return canvas
