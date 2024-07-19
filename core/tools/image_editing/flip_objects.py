from copy import deepcopy
from typing import List, Literal
from core.tools.image_editing.inpaint_objects import inpaint_objects
from core.tools.image_editing.types import Image, Object
from core.tools.image_editing.utils import get_object_idxs


async def flip_objects(image: Image, objects: List[Object], axis: Literal["x", "y"]) -> Image:
    object_idxs = get_object_idxs(image, objects)
    canvas = deepcopy(image)
    
    flipped_objects = []
    for i in object_idxs:
        obj = canvas.objects[i]
        if axis == "x": obj.flipX = not obj.flipX
        else: obj.flipY = not obj.flipY
        flipped_objects.append(obj)

    await inpaint_objects(canvas, flipped_objects)    
    return canvas