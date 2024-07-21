import asyncio
from copyreg import constructor
from typing import (Any, Callable, Dict, Iterable, List, Literal, Optional,
                    Tuple, TypeVar, Union)

from core.providers.provider import Provider
from core.schemas.fabric import FabricCanvas, FabricImage, FabricTextbox
from core.tools.fabric import (detect_objects, flip_objects, rotate_objects,
                               scale_objects)
from core.tools.fabric.apply_filter import apply_filter
from core.tools.fabric.remove_objects import remove_objects
from database.models.conversation.chat_message import ChatMessage

Image = TypeVar("Image", FabricCanvas, FabricImage, None)
Object = TypeVar("Object", FabricImage, None)
Text = TypeVar("Text", FabricTextbox, None)


EXEMPLARS = """
Example 1:
observation: user_request(text="Hãy xóa con chó khỏi bức ảnh", variables=[image_0])
thinking: We need detect the dog first before we can remove it.
commands:
dogs = detect(image_0, prompt="dog")
observation: sys_warning(text="Detected 2 `dog` in the image", variables=[annotated_image_0])
thinking: There are 2 dogs in the image so we need to show the annotated image and ask the user to specify which one to be removed.
commands:
response_user(text"Trong ảnh có 2 con chó, bạn muốn chọn con nào để xóa?", variables=[annotated_image_0])

Example2: 
observation: user_request(text="Hãy tăng độ sáng của ngôi nhà lên khoảng 15%, variables=[image_0])
thinking: We need to detect the house first before we can increase the brightness of it.
commands:
houses = detect(image_0, prompt="house")
observation: sys_info(text="Detected 1 `house` in the image")
thinking: We detected the house, now we can do the next step.
commands:
image_1 = filter(image_1, filter_name="brightness", filter_value=1.15, targets=houses)
response_user(text="Đây là bức ảnh sau khi đã tăng độ sáng ngôi nhà lên 15%." variables=[image_1])
"""

FILTER_NAMES = [
    "Grayscale",
    "Invert",
    "Brightness",
    "Blur",
    "Contrast",
    "Noise",
    "Pixelate",
]


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
        return await detect_objects(image, prompt)

    async def remove(
        self, image: Image, targets: List[Union[Image, Object, Text]]
    ) -> Image:
        return await remove_objects(image, targets)

    def filter(
        self,
        image: Image,
        filter_name: str,
        filter_value: Optional[float] = None,
        targets: Optional[List[Object]] = None,
    ) -> Image:
        return apply_filter(image, filter_name, filter_value, targets)

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

    async def scale(
        self,
        image: Image,
        factor: float,
        targets: Optional[List[Union[Image, Object, Text]]],
        axis: Optional[Literal["x", "y"]] = None,
    ) -> Image:
        return await scale_objects(image, targets, factor, axis)
