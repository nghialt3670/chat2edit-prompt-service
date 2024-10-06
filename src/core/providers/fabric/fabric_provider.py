import base64 as b64
from copy import deepcopy
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Tuple,
    TypeVar,
    Union,
)
from uuid import uuid4

from pydantic import TypeAdapter

from core.providers.fabric.fabric_exemplars import create_fabric_exemplars
from core.providers.fabric.models import (
    FabricCanvas,
    FabricImage,
    FabricRect,
    FabricTextbox,
)
from core.providers.fabric.models.fabric_group import FabricGroup
from core.providers.fabric.tools.apply_filter import apply_filter
from core.providers.fabric.tools.detect_objects import detect_objects
from core.providers.fabric.tools.flip_objects import flip_objects
from core.providers.fabric.tools.move_objects import move_objects
from core.providers.fabric.tools.remove_objects import remove_objects
from core.providers.fabric.tools.replace_objects_with_prompt import (
    replace_objects_with_prompt,
)
from core.providers.fabric.tools.rotate_objects import rotate_objects
from core.providers.fabric.tools.scale_objects import scale_objects
from core.providers.fabric.tools.segment_object import segment_object
from core.providers.fabric.tools.shift_objects import shift_objects
from core.providers.provider import Provider
from schemas.file import File

Image = TypeVar("Image", FabricCanvas, FabricImage, None)
Object = TypeVar("Object", FabricImage, None)
Text = TypeVar("Text", FabricTextbox, None)

CONTEXT_ALLOWED_TYPES = Union[
    str,
    int,
    float,
    bool,
    Tuple[int, int, int, int],
    FabricCanvas,
    FabricGroup,
    FabricImage,
    FabricTextbox,
    FabricRect,
    List[FabricImage],
]
CONTEXT_ALLOWED_TYPES_SET = {
    str,
    int,
    float,
    bool,
    list,
    tuple,
    FabricCanvas,
    FabricGroup,
    FabricImage,
    FabricTextbox,
    FabricRect,
}
FABRIC_TYPE_TO_ALIAS = {FabricCanvas: "image", tuple: "box"}
FILTER_NAME_MAPPINGS = {
    "grayscale": "Grayscale",
    "gray": "Grayscale",
    "invert": "Invert",
    "negative": "Invert",
    "brightness": "Brightness",
    "bright": "Brightness",
    "blur": "Blur",
    "blurness": "Blur",
    "contrast": "Contrast",
    "noise": "Noise",
    "pixelate": "Pixelate",
    "pixel": "Pixelate",
}


class FabricProvider(Provider):
    def __init__(self, function_names: Iterable[str]) -> None:
        super().__init__()
        self._function_names = function_names
        self._context_adaptor = TypeAdapter(Dict[str, CONTEXT_ALLOWED_TYPES])
        self._exemplars = create_fabric_exemplars()

    def get_functions(self) -> List[Callable]:
        return [getattr(self, name) for name in self._function_names]

    def get_exemplars(self) -> str:
        if self._language == "vi":
            return self._exemplars[0]
        if self._language == "en":
            return self._exemplars[1]

        raise ValueError(f"Language {self._language} is not supported")

    def get_alias(self, obj) -> str:
        return FABRIC_TYPE_TO_ALIAS[type(obj)]

    def filter_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        is_allowed_value = lambda x: type(x) in CONTEXT_ALLOWED_TYPES_SET
        for k in {k for k, v in context.items() if not is_allowed_value(v)}:
            context.pop(k)

        return context

    def encode_context(self, context: Dict[str, Any]) -> bytes:
        return self._context_adaptor.dump_json(context)

    def decode_context(self, buffer: bytes) -> Dict[str, Any]:
        return self._context_adaptor.validate_json(buffer)

    def convert_file_to_objects(self, file: File) -> Any:
        if file.content_type.startswith("image/"):
            base64 = b64.b64encode(file.buffer).decode()
            data_url = f"data:{file.content_type};base64,{base64}"
            image = FabricImage(src=data_url, filename=file.name)
            return [FabricCanvas(backgroundImage=image)]

        elif file.name.endswith(".fcanvas"):
            canvas = FabricCanvas.model_validate_json(file.buffer)
            objects = [canvas]
            prompt_rects = [
                obj
                for obj in canvas.objects
                if isinstance(obj, FabricRect) and obj.is_prompt
            ]
            [canvas.objects.remove(rect) for rect in prompt_rects]
            objects.extend([rect.get_box() for rect in prompt_rects])
            return objects

        raise NotImplementedError(
            f"Unsupported file type for converting to obj: {file}"
        )

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

        raise ValueError(f"Unspported object type for converting to file: {type(obj)}")

    async def detect(self, image: Image, prompt: str) -> List[Object]:
        objects = await detect_objects(image, prompt)
        image_varname = self.get_varname(image)
        n_objects = len(objects)
        text = f"Detected {n_objects} `{prompt}` in `{image_varname}`"
        
        if n_objects == 0:
            self.feedback("warning", text)
        elif n_objects == 1:
            self.feedback("info", text)
        else:
            annotated_image_varname = f"annotated_{image_varname}"
            annotated_image = self._annotate_detections(image, objects)
            self.add_to_context(annotated_image_varname, annotated_image)
            self.feedback("warning", text, [annotated_image_varname])

        return objects

    async def segment(self, image: Image, box: Tuple[int, int, int, int]) -> Object:
        return await segment_object(image, box)

    async def remove(
        self, image: Image, targets: List[Union[Image, Object, Text]]
    ) -> Image:
        return await remove_objects(image, targets)

    async def replace(self, image: Image, targets: List[Object], prompt: str) -> Image:
        return await replace_objects_with_prompt(image, targets, prompt)

    def filter(
        self,
        image: Image,
        filter_name: str,
        filter_value: float = None,
        targets: List[Object] = None,
    ) -> Image:
        filter_name = filter_name.lower()
        if filter_name not in FILTER_NAME_MAPPINGS:
            text = f"Available values for `filter_name` are: {FILTER_NAME_MAPPINGS.values()}"
            self.feedback("error", text)
            return image

        filter_name = FILTER_NAME_MAPPINGS[filter_name]
        return apply_filter(image, filter_name, filter_value, targets)

    async def rotate(
        self,
        image: Image,
        angle: int,
        targets: List[Union[Image, Object, Text]] = None,
    ) -> Image:
        if targets:
            return await rotate_objects(image, targets, angle)

        image.backgroundImage.rotate(angle)
        return image

    async def flip(
        self,
        image: Image,
        axis: Literal["x", "y"],
        targets: List[Union[Image, Object, Text]] = None,
    ) -> Image:
        if targets:
            return await flip_objects(image, targets, axis)

        image.backgroundImage.flip(axis)
        return image

    async def move(
        self,
        image: Image,
        targets: List[Union[Image, Object, Text]],
        dest: Tuple[int, int],
    ) -> Image:
        return await move_objects(image, targets, dest)

    async def shift(
        self,
        image: Image,
        targets: List[Union[Image, Object, Text]],
        offset: int,
        axis: Literal["x", "y"],
    ) -> Image:
        return await shift_objects(image, targets, offset, axis)

    async def scale(
        self,
        image: Image,
        factor: float,
        targets: List[Union[Image, Object, Text]],
        axis: Literal["x", "y"] = None,
    ) -> Image:
        return await scale_objects(image, targets, factor, axis)

    def _annotate_detections(
        self, canvas: FabricCanvas, objects: List[FabricImage]
    ) -> FabricCanvas:
        canvas = deepcopy(canvas)

        for idx, obj in enumerate(objects):
            obj_box = FabricRect(
                left=obj.left,
                top=obj.top,
                width=obj.width,
                height=obj.height,
                stroke="red",
                strokeWidth=3,
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
            canvas.objects.append(obj_box)
            canvas.objects.append(obj_idx)

        return canvas

    def create_text(
        self,
        content: str,
        font_family: str,
        font_size: int,
        font_weight: str,
        font_style: str,
        color: str,
    ) -> Text:
        return FabricTextbox(
            text=content,
            fontFamily=font_family,
            fontSize=font_size,
            fontWeight=font_weight,
            fontStyle=font_style,
            fill=color,
        )

    def get_position(self, target: Union[Image, Object, Text]) -> Tuple[int, int]:
        return target.left, target.top

    def get_size(self, target: Union[Image, Object, Text]) -> Tuple[int, int]:
        return target.width, target.height
