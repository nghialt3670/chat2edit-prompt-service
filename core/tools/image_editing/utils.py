from typing import List
from core.tools.image_editing.types import Image, Object


def get_object_idxs(image: Image, objects: List[Object]) -> List[int]:
    return [image.objects.index(obj) for obj in objects]