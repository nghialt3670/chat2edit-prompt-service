from copy import deepcopy
from typing import List, Literal, Optional

from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.schemas.fabric.fabric_image import FabricImage
from core.schemas.fabric.fabric_object import FabricObject
from core.tools.fabric.helpers import get_object_idxs
from core.tools.fabric.inpaint_objects import inpaint_objects


async def scale_objects(
    canvas: FabricCanvas,
    objects: List[FabricObject],
    factor: float = 1.0,
    axis: Optional[Literal["x", "y"]] = None,
) -> FabricCanvas:
    object_idxs = get_object_idxs(canvas, objects)
    canvas = deepcopy(canvas)

    await inpaint_objects(canvas, object_idxs)

    for i in object_idxs:
        obj = canvas.objects[i]
        if axis == "x":
            obj.scaleX *= factor
        elif axis == "y":
            obj.scaleY *= factor
        else:
            obj.scaleX *= factor
            obj.scaleY *= factor

    return canvas
