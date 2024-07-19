import warnings
from copy import deepcopy
from typing import List

from core.tools.image_editing.inpaint_objects import inpaint_objects
from core.tools.image_editing.types import Image, Object
from core.tools.image_editing.utils import get_object_idxs


async def remove_objects(image: Image, objects: List[Object]) -> Image:
    object_idxs = get_object_idxs(image, objects)
    
    if -1 in object_idxs:
        raise RuntimeError("cant remove object being not within the image")
    
    canvas = deepcopy(image)
    
    removed_objects = [
        canvas.objects[idx] for idx in range(len(canvas.objects)) if idx in set(object_idxs)
    ]
    canvas.objects = [
        obj for idx, obj in enumerate(canvas.objects) if idx not in object_idxs
    ]
    await inpaint_objects(canvas, removed_objects)
    return canvas
