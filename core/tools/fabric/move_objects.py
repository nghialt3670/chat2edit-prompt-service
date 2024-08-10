from copy import deepcopy
from typing import List, Tuple

from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.schemas.fabric.fabric_image import FabricImage
from core.schemas.fabric.fabric_object import FabricObject
from core.tools.fabric.helpers import get_object_idxs
from core.tools.fabric.inpaint_objects import inpaint_objects


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
