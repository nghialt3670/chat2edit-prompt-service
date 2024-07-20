import asyncio
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
)
from core.providers.provider import Provider
from core.schemas.fabric import FabricCanvas, FabricImage, FabricTextbox
from core.tools.fabric import (
    detect_objects,
    flip_objects,
    rotate_objects,
    scale_objects,
)
from core.tools.fabric.apply_filter import apply_filter
from core.tools.fabric.remove_objects import remove_objects
from database.models.conversation.chat_message import ChatMessage

Image = TypeVar("Image", FabricCanvas, FabricImage, None)
Object = TypeVar("Object", FabricImage, None)
Text = TypeVar("Text", FabricTextbox, None)


EXEMPLARS = """

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
        response = ChatMessage(text=text, file_ids=[var.id for var in variables])
        self._set_signal(status="info", response=response)

    def detect(self, image: Image, prompt: str) -> List[Object]:
        return asyncio.run(detect_objects(image, prompt))

    def remove(self, image: Image, targets: List[Union[Image, Object, Text]]) -> Image:
        return asyncio.run(remove_objects(image, targets))

    def filter(
        self,
        image: Image,
        filter_name: str,
        filter_value: Optional[float] = None,
        targets: Optional[List[Object]] = None,
    ) -> Image:
        return apply_filter(image, filter_name, filter_value, targets)

    def rotate(
        self,
        image: Image,
        angle: int,
        targets: Optional[List[Union[Image, Object, Text]]] = None,
    ) -> Image:
        if targets:
            return asyncio.run(rotate_objects(image, targets, angle))
        return asyncio.run(rotate_objects(image, image.backgroundImage, angle))

    def flip(
        self,
        image: Image,
        axis: Literal["x", "y"],
        targets: Optional[List[Union[Image, Object, Text]]] = None,
    ) -> Image:
        if targets:
            return asyncio.run(flip_objects(image, targets, axis))
        return asyncio.run(flip_objects(image, image.backgroundImage, axis))

    def scale(
        self,
        image: Image,
        factor: float,
        targets: Optional[List[Union[Image, Object, Text]]],
        axis: Optional[Literal["x", "y"]] = None,
    ) -> Image:
        return asyncio.run(scale_objects(image, targets, factor, axis))
