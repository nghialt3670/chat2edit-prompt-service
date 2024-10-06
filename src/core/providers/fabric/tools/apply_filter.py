from copy import deepcopy
from typing import List, Literal, Optional

from core.providers.fabric.models.fabric_canvas import FabricCanvas
from core.providers.fabric.models.fabric_filter import (
    BlurFilter,
    BrightnessFilter,
    ContrastFilter,
    GrayscaleFilter,
    InvertFilter,
    NoiseFilter,
    PixelateFilter,
    SaturationFilter,
)
from core.providers.fabric.models.fabric_image import FabricImage
from core.providers.fabric.tools.helpers import get_object_idxs


def apply_filter(
    canvas: FabricCanvas,
    filter_name: Literal[
        "Grayscale", "Invert", "Brightness", "Blur", "Contrast", "Noise", "Pixelate", "Saturation"
    ],
    filter_value: Optional[float] = None,
    objects: Optional[List[FabricImage]] = None,
) -> FabricCanvas:
    filt = None

    if filter_value:
        filter_value -= 1
    if filter_name == "Grayscale":
        filt = GrayscaleFilter()
    elif filter_name == "Invert":
        filt = InvertFilter()
    elif filter_name == "Brightness":
        filt = BrightnessFilter(brightness=filter_value)
    elif filter_name == "Blur":
        filt = BlurFilter(blur=filter_value)
    elif filter_name == "Contrast":
        filt = ContrastFilter(contrast=filter_value)
    elif filter_name == "Noise":
        filt = NoiseFilter(noise=filter_value)
    elif filter_name == "Pixelate":
        filt = PixelateFilter(blocksize=filter_value * 10)
    elif filter_name == "Saturation":
        filt = SaturationFilter(saturation=filter_value)
    else:
        raise ValueError(f"Invalid filter name: {filter_name}")

    if objects:
        object_idxs = get_object_idxs(canvas, objects)
        for i in object_idxs:
            obj = canvas.objects[i]
            if isinstance(obj, FabricImage):
                obj.apply_filter(filt)
    else:
        canvas = deepcopy(canvas)
        canvas.backgroundImage.apply_filter(filt)
        for obj in canvas.objects:
            if isinstance(obj, FabricImage):
                obj.apply_filter(filt)

    return canvas
