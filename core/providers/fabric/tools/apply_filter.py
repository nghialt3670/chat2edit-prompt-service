from copy import deepcopy
from typing import List, Literal, Optional

from core.providers.fabric.models.fabric_canvas import FabricCanvas
from core.providers.fabric.models.fabric_image import FabricImage
from core.providers.fabric.tools.helpers import get_object_idxs


def apply_filter(
    canvas: FabricCanvas,
    filter_name: Literal[
        "Grayscale", "Invert", "Brightness", "Blur", "Contrast", "Noise", "Pixelate"
    ],
    filter_value: Optional[float] = None,
    objects: Optional[List[FabricImage]] = None,
) -> FabricCanvas:
    filt = None
    if filter_value:
        filter_value -= 1
    if filter_name == "Grayscale":
        filt = {"type": "Grayscale", "mode": "average"}
    elif filter_name == "Invert":
        filt = {"type": "Invert"}
    elif filter_name == "Brightness":
        filt = {"type": "Brightness", "brightness": filter_value}
    elif filter_name == "Blur":
        filt = {"type": "Blur", "blur": filter_value}
    elif filter_name == "Contrast":
        filt = {"type": "Contrast", "contrast": filter_value}
    elif filter_name == "Noise":
        filt = {"type": "Noise", "noise": filter_value}
    elif filter_name == "Pixelate":
        filt = {"type": "Pixelate", "blocksize": filter_value * 10}
    else:
        raise ValueError()

    if objects:
        object_idxs = get_object_idxs(canvas, objects)
        for i in object_idxs:
            obj = canvas.objects[i]
            obj.filters.append(filt)
    else:
        canvas = deepcopy(canvas)
        canvas.backgroundImage.filters.append(filt)
        for obj in canvas.objects:
            if isinstance(obj, FabricImage):
                obj.filters.append(filt)

    return canvas
