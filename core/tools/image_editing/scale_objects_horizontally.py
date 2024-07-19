from copy import deepcopy
from typing import List
from core.tools.image_editing.inpaint_objects import inpaint_objects
from core.tools.image_editing.types import Image, Object
from core.tools.image_editing.utils import get_object_idxs


async def scale_objects_horizontally(image: Image, objects: List[Object], factor: float = 1.0) -> Image:
    object_idxs = get_object_idxs(image, objects)
    canvas = deepcopy(image)
    
    scaled_objects = []
    for i in object_idxs:
        obj = canvas.objects[i]
        obj.scaleY *= factor
        scaled_objects.append(obj)

    await inpaint_objects(canvas, scaled_objects)    
    return canvas