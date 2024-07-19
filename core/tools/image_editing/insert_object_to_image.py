from copy import deepcopy
from typing import Tuple
from core.tools.image_editing.types import Image, Object


def insert_object_to_image(image: Image, obj: Object, destination: Tuple[int, int]) -> Image:
    canvas = deepcopy(image)
    copied_obj = deepcopy(obj)
    copied_obj.left = destination[0]
    copied_obj.top = destination[1]
    canvas.objects.append(copied_obj)