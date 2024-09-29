from copy import deepcopy
from typing import List, Literal

from core.providers.fabric.models.fabric_canvas import FabricCanvas
from core.providers.fabric.models.fabric_image import FabricImage
from core.providers.fabric.models.fabric_object import FabricObject
from core.providers.fabric.tools.helpers import get_object_idxs
from core.providers.fabric.tools.inpaint_objects import inpaint_objects


async def shift_objects(
    canvas: FabricCanvas,
    objects: List[FabricObject],
    offset: int,
    axis: Literal["x", "y"],
) -> FabricCanvas:
    object_idxs = get_object_idxs(canvas, objects)
    canvas = deepcopy(canvas)

    await inpaint_objects(canvas, object_idxs)

    for i in object_idxs:
        obj = canvas.objects[i]
        if axis == "x":
            obj.left += offset
        elif axis == "y":
            obj.top += offset
        else:
            raise ValueError()

    return canvas
