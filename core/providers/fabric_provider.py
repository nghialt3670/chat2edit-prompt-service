from copy import deepcopy
from typing import (Any, Callable, Iterable, List, Literal, Optional, Tuple,
                    TypeVar, Union)

from core.providers.provider import Provider
from core.schemas.fabric import (FabricCanvas, FabricImage, FabricRect,
                                 FabricTextbox)
from core.tools.fabric import (apply_filter, detect_objects, flip_objects,
                               move_objects, remove_objects,
                               replace_objects_with_prompt, rotate_objects,
                               scale_objects, shift_objects)
from database.models import ChatMessage

Image = TypeVar("Image", FabricCanvas, FabricImage, None)
Object = TypeVar("Object", FabricImage, None)
Text = TypeVar("Text", FabricTextbox, None)


EXEMPLARS = """
Example 1:
observation: user_request(text="Hãy xóa con chó khỏi bức ảnh", variables=[image0])
thinking: We need detect the dog first before we can remove it.
commands:
dogs = detect(image0, prompt="dog")
observation: sys_warning(text="Detected 2 `dog` in the image", variables=[annotated_image])
thinking: There are 2 dogs in the image so we need to show the annotated image and ask the user to specify which one to be removed.
commands:
response_user(text"Trong ảnh có 2 con chó, bạn muốn chọn con nào để xóa?", variables=[annotated_image])

Example2: 
observation: user_request(text="Hãy tăng độ sáng của ngôi nhà lên khoảng 15%, variables=[image0])
thinking: We need to detect the house first before we can increase the brightness of it.
commands:
houses = detect(image0, prompt="house")
observation: sys_info(text="Detected 1 `house` in the image")
thinking: We detected the house, now we can do the next step.
commands:
image1 = filter(image0, filter_name="brightness", filter_value=1.15, targets=houses)
response_user(text="Đây là bức ảnh sau khi đã tăng độ sáng ngôi nhà lên 15%.", variables=[image1])
"""

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

    def get_functions(self) -> List[Callable]:
        return [getattr(self, name) for name in self._function_names]

    def get_exemplars(self) -> str:
        return EXEMPLARS

    def response_user(self, text: str, variables: Optional[List[Any]] = None) -> None:
        response = None
        if variables:
            id_to_varname = {id(v): k for k, v in self._context.items()}
            varnames = [id_to_varname[id(var)] for var in variables]
            response = ChatMessage(text=text, varnames=varnames)
        else:
            response = ChatMessage(text=text)
        self._set_signal(status="info", response=response)

    async def detect(self, image: Image, prompt: str) -> List[Object]:
        objects = await detect_objects(image, prompt)
        if len(objects) == 0:
            self._set_signal("warning", f"Detected 0 `{prompt}` in the image")
        elif len(objects) == 1:
            self._set_signal("info", f"Detected 1 `{prompt}` in the image")
        else:
            self._context["annotated_image"] = await self._annotate_detections(
                image, objects
            )
            self._set_signal(
                "warning",
                f"Detected {len(objects)} `{prompt}` in the image",
                varnames=["annotated_image"],
            )

        return objects

    async def remove(
        self, image: Image, targets: List[Union[Image, Object, Text]]
    ) -> Image:
        return await remove_objects(image, targets)

    async def replace(self, image: Image, targets: List[Object], prompt: str) -> Image:
        image = await remove_objects(image, targets)
        await replace_objects_with_prompt(image, targets, prompt)
        return image

    def filter(
        self,
        image: Image,
        filter_name: str,
        filter_value: Optional[float] = None,
        targets: Optional[List[Object]] = None,
    ) -> Image:
        filter_name = filter_name.lower()
        if filter_name not in FILTER_NAME_MAPPINGS:
            self._set_signal(
                "error",
                f"Available values for `filter_name` are: {FILTER_NAME_MAPPINGS.values()}",
            )
            return image
        return apply_filter(
            image, FILTER_NAME_MAPPINGS[filter_name], filter_value, targets
        )

    async def rotate(
        self,
        image: Image,
        angle: int,
        targets: Optional[List[Union[Image, Object, Text]]] = None,
    ) -> Image:
        if targets:
            return await rotate_objects(image, targets, angle)
        return await rotate_objects(image, image.backgroundImage, angle)

    async def flip(
        self,
        image: Image,
        axis: Literal["x", "y"],
        targets: Optional[List[Union[Image, Object, Text]]] = None,
    ) -> Image:
        if targets:
            return await flip_objects(image, targets, axis)
        return await flip_objects(image, image.backgroundImage, axis)

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
        targets: Optional[List[Union[Image, Object, Text]]],
        axis: Optional[Literal["x", "y"]] = None,
    ) -> Image:
        return await scale_objects(image, targets, factor, axis)

    async def _annotate_detections(
        self, canvas: FabricCanvas, objects: List[FabricImage]
    ) -> FabricCanvas:
        canvas = deepcopy(canvas)

        if not canvas.backgroundImage.is_size_initialized():
            await canvas.backgroundImage.init_size()

        for idx, obj in enumerate(objects):
            if not obj.is_size_initialized():
                await obj.init_size()

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
