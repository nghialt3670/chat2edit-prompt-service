import base64 as b64
from copy import deepcopy
from typing import Any, List, Literal, Optional, Tuple, TypeVar, Union
from uuid import uuid4

from core.providers.fabric.fabric_exemplars import create_fabric_exemplars
from core.providers.fabric.models import (FabricCanvas, FabricFilter,
                                          FabricImage, FabricRect,
                                          FabricTextbox)
from core.providers.fabric.models.fabric_filter import (BlurFilter,
                                                        BrightnessFilter,
                                                        ContrastFilter,
                                                        GrayscaleFilter,
                                                        InvertFilter,
                                                        NoiseFilter,
                                                        PixelateFilter,
                                                        SaturationFilter)
from core.providers.fabric.models.fabric_group import FabricGroup
from core.providers.provider import Provider, prompt_function
from models.phase import Message
from schemas.file import File

CompositeImage = TypeVar("CompositeImage", FabricCanvas, FabricImage, None)
ImageObject = TypeVar("ImageObject", FabricImage, None)
Textbox = TypeVar("Textbox", FabricTextbox, None)
Box = TypeVar("Box", FabricRect, None)

FABRIC_CONTEXT_VALUE_TYPES = (
    FabricCanvas,
    FabricGroup,
    FabricImage,
    FabricTextbox,
    FabricRect,
    List[FabricImage],
    str,
    int,
    float,
    bool,
)
FABRIC_TYPE_TO_ALIAS = {FabricCanvas: "image", FabricRect: "box"}
FABRIC_FILTER_NAME_TYPE = Literal[
    "Grayscale",
    "Invert",
    "Brightness",
    "Blur",
    "Contrast",
    "Noise",
    "Pixelate",
    "Saturation",
]
ADJUSTABLE_FILTER_NAME_SET = {
    "Brightness",
    "Blur",
    "Contrast",
    "Noise",
    "Pixelate",
    "Saturation",
}
FILTERABLE_OBJECT_TYPE = Union[CompositeImage, ImageObject]
CANVAS_OBJECT_TYPE = Union[CompositeImage, ImageObject, Textbox]


class FabricProvider(Provider):
    def __init__(self) -> None:
        super().__init__(
            lang_to_exemplars=create_fabric_exemplars(),
            context_value_types=FABRIC_CONTEXT_VALUE_TYPES,
            type_to_alias=FABRIC_TYPE_TO_ALIAS,
        )

    def convert_file_to_objects(self, file: File) -> List[Any]:
        if file.content_type.startswith("image/"):
            base64 = b64.b64encode(file.buffer).decode()
            data_url = f"data:{file.content_type};base64,{base64}"
            image = FabricImage(src=data_url, filename=file.name)
            return [FabricCanvas(backgroundImage=image)]

        elif file.name.endswith(".fcanvas"):
            canvas = FabricCanvas.model_validate_json(file.buffer)
            is_query_rect = lambda x: isinstance(x, FabricRect) and x.is_query
            query_rects = [obj for obj in canvas.objects if is_query_rect(obj)]
            [canvas.objects.remove(rect) for rect in query_rects]
            return [canvas] + query_rects

        raise NotImplementedError()

    def convert_object_to_file(self, obj: Any) -> File:
        if isinstance(obj, FabricCanvas):
            buffer = obj.model_dump_json().encode()
            filename = obj.backgroundImage.filename + ".fcanvas"
            return File(
                buffer=buffer,
                name=filename,
                content_type="application/json",
            )

        elif isinstance(obj, FabricImage):
            canvas = FabricCanvas(backgroundImage=obj)
            buffer = canvas.model_dump_json().encode()
            filename = (obj.filename or f"{uuid4()}.png") + ".fcanvas"
            return File(
                buffer=buffer,
                name=filename,
                content_type="application/json",
            )

        raise NotImplementedError()

    @prompt_function(
        index=0,
        description="Segments image objects based on a short and concise prompt such as 'cat', 'dog', 'green house', etc.",
    )
    async def segment_image_objects_by_prompt(
        self, image: CompositeImage, prompt: str
    ) -> List[ImageObject]:
        objects = await image.segment_image_objects_by_prompt(prompt)

        n_objects = len(objects)
        image_varname = self.get_varname(image)
        feedback_text = f"Segmented {n_objects} `{prompt}` in `{image_varname}`."

        if n_objects == 0:
            self._set_feedback("warning", feedback_text)
        elif n_objects == 1:
            self._set_feedback("info", feedback_text)
        else:
            annotated_image_varname = f"annotated_{image_varname}"
            annotated_image = self._annotate_detections(image, objects)
            self._update_context(annotated_image_varname, annotated_image)
            self._set_feedback("warning", feedback_text, [annotated_image_varname])

        return objects

    @prompt_function(
        index=1,
        description="Segments image objects within specified boxes in the given image.",
    )
    async def segment_image_objects_by_boxes(
        self,
        image: CompositeImage,
        boxes: List[Box],
    ) -> List[ImageObject]:
        tuple_boxes = [box.get_box() for box in boxes]
        return await image.segment_image_objects_by_boxes(tuple_boxes)

    @prompt_function(
        index=2,
        description="Replaces image objects in the given image based on a detailed prompt that describes the object to replace.",
    )
    async def replace_image_objects_by_prompt(
        self, image: CompositeImage, objects: List[ImageObject], prompt: str
    ) -> CompositeImage:
        copied_image = deepcopy(image)
        await copied_image.inpaint_image_objects_by_prompt(objects, prompt)
        return copied_image

    @prompt_function(
        index=3,
        description="Applies a specified filter to an image or, if provided, to its child elements.",
    )
    async def apply_filter_to_image_or_children(
        self,
        image: CompositeImage,
        filter_name: FABRIC_FILTER_NAME_TYPE,
        filter_value: Optional[float] = None,
        children: Optional[List[FILTERABLE_OBJECT_TYPE]] = None,
    ) -> CompositeImage:
        feedback_text = None

        if filter_value:
            if not filter_name in ADJUSTABLE_FILTER_NAME_SET:
                feedback_text = f"In `apply_filter` function, parameter `filter_value`, if provided, cannot be used with the filter `{filter_name}` as it does not support value adjustments."

            if filter_value < -1.0 or filter_value > 1.0:
                feedback_text = "In `apply_filter` function, parameter `filter_value`, if provided, must be between -1.0 and 1.0."

        elif filter_name in ADJUSTABLE_FILTER_NAME_SET:
            feedback_text = f"In `apply_filter` function, parameter `filter_value` is required for the filter `{filter_name}` as it supports value adjustments."

        if feedback_text:
            self._set_feedback("error", feedback_text)
            return None

        filt = self._create_filter(filter_name, filter_value)
        copied_image = deepcopy(image)
        copied_image.apply_filter(filt, children)
        return copied_image

    @prompt_function(
        index=4,
        description="Rotates an image or, if provided, its child elements by a specified angle.",
    )
    async def rotate_image_or_children(
        self,
        image: CompositeImage,
        angle: float,
        children: Optional[List[CANVAS_OBJECT_TYPE]] = None,
    ) -> CompositeImage:
        copied_image = deepcopy(image)

        if children:
            angles = [angle] * len(children)
            await copied_image.rotate_objects(children, angles)
        else:
            copied_image.backgroundImage.rotate(angle)

        return copied_image

    @prompt_function(
        index=5,
        description="Flips an image or, if provided, its child elements along the specified axis (x or y).",
    )
    async def flip_image_or_children(
        self,
        image: CompositeImage,
        axis: Literal["x", "y"],
        children: Optional[List[CANVAS_OBJECT_TYPE]] = None,
    ) -> CompositeImage:
        copied_image = deepcopy(image)

        if children:
            axes = [axis] * len(children)
            await copied_image.flip_objects(children, axes)
        else:
            copied_image.backgroundImage.flip(axis)

        return copied_image

    @prompt_function(
        index=6, description="Removes specified child elements from the image."
    )
    async def remove_children(
        self,
        image: CompositeImage,
        children: List[CANVAS_OBJECT_TYPE],
    ) -> CompositeImage:
        copied_image = deepcopy(image)
        await copied_image.remove_objects(children)
        return copied_image

    @prompt_function(
        index=7,
        description="Moves specified child elements to new positions. The number of children must match the number of destinations",
    )
    async def move_children(
        self,
        image: CompositeImage,
        children: List[CANVAS_OBJECT_TYPE],
        destinations: List[Tuple[int, int]],
    ) -> CompositeImage:
        if len(children) != len(destinations):
            feedback_text = (
                f"In `move_children` function, the length of `children` ({len(children)}) "
                f"does not match the length of `destinations` ({len(destinations)}). "
                "Each child must have a corresponding destination."
            )
            self._set_feedback("error", feedback_text)
            return None

        copied_image = deepcopy(image)
        await copied_image.move_objects(children, destinations)
        return copied_image

    @prompt_function(
        index=8,
        description="Scales specified child elements by the provided factors. The number of children must match the number of factors.",
    )
    async def scale_children(
        self,
        image: CompositeImage,
        children: List[CANVAS_OBJECT_TYPE],
        factors: List[float],
    ) -> CompositeImage:
        if len(children) != len(factors):
            feedback_text = (
                f"In `scale_children` function, the length of `children` ({len(children)}) "
                f"does not match the length of `factors` ({len(factors)}). "
                "Each child must have a corresponding scale factor."
            )
            self._set_feedback("error", feedback_text)
            return None

        copied_image = deepcopy(image)
        await copied_image.scale_objects(children, factors)
        return copied_image

    @prompt_function(
        index=9,
        description="Creates a textbox with the specified content, font, and color properties.",
    )
    async def create_textbox(
        self,
        content: str,
        font_family: str,
        font_size: int,
        font_weight: str,
        font_style: str,
        color: str,
    ) -> Textbox:
        return FabricTextbox(
            text=content,
            fontFamily=font_family,
            fontSize=font_size,
            fontWeight=font_weight,
            fontStyle=font_style,
            fill=color,
        )

    @prompt_function(
        index=10,
        description="Retrieves the position of each child element in the provided list.",
    )
    async def get_children_position(
        self, children: List[CANVAS_OBJECT_TYPE]
    ) -> List[Tuple[int, int]]:
        return [(child.left, child.top) for child in children]

    @prompt_function(
        index=11,
        description="Sends a response to the user with a specified text and optional attachments, this is a special function used to interact with the user.",
    )
    async def response_to_user(
        self, text: str, attachments: List[Union[CompositeImage, ImageObject]] = []
    ) -> None:
        id_to_varname = {id(v): k for k, v in self._context.items()}
        varnames = [id_to_varname[id(att)] for att in attachments]
        self._response = Message(
            src="llm", type="response", text=text, varnames=varnames
        )

    def _annotate_detections(
        self, canvas: FabricCanvas, objects: List[FabricImage]
    ) -> FabricCanvas:
        copied_canvas = deepcopy(canvas)

        for idx, obj in enumerate(objects):
            obj_box = FabricRect(
                left=obj.left,
                top=obj.top,
                width=obj.width,
                height=obj.height,
                stroke="red",
                strokeWidth=canvas.backgroundImage.height // 16,
                selectable=False,
                fill="transparent",
            )
            obj_idx = FabricTextbox(
                text=f"{idx}",
                left=obj.left,
                top=obj.top,
                fontSize=canvas.backgroundImage.height // 8,
                selectable=False,
                fill="red",
            )
            copied_canvas.objects.append(obj_box)
            copied_canvas.objects.append(obj_idx)

        return copied_canvas

    def _create_filter(
        self, filter_name: FABRIC_FILTER_NAME_TYPE, filter_value: Optional[float]
    ) -> FabricFilter:
        if filter_name == "Blur":
            return BlurFilter(blur=filter_value)
        if filter_name == "Brightness":
            return BrightnessFilter(brightness=filter_value)
        if filter_name == "Contrast":
            return ContrastFilter(contrast=filter_value)
        if filter_name == "Noise":
            return NoiseFilter(noise=filter_value)
        if filter_name == "Saturation":
            return SaturationFilter(saturation=filter_value)
        if filter_name == "Pixelate":
            return PixelateFilter(blocksize=filter_value * 10)
        if filter_name == "Grayscale":
            return GrayscaleFilter()
        if filter_name == "Invert":
            return InvertFilter()
