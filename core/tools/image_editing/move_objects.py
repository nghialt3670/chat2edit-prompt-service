from copy import deepcopy
from typing import List, Tuple
from core.tools.image_editing.inpaint_objects import inpaint_objects
from core.tools.image_editing.types import Image, Object
from core.tools.image_editing.utils import get_object_idxs


async def scale_objects_vertically(image: Image, objects: List[Object], destination: Tuple[int, int]) -> Image:
    object_idxs = get_object_idxs(image, objects)
    canvas = deepcopy(image)
    
    moved_objects = []
    for i in object_idxs:
        obj = canvas.objects[i]
        obj.left = destination[0]
        obj.top = destination[1]
        moved_objects.append(obj)

    await inpaint_objects(canvas, moved_objects)    
    return canvas