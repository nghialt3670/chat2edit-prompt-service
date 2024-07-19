from typing import (Any, Callable, Iterable, List, Literal, Optional, Tuple,
                    TypeVar, Union)

import numpy as np
from chat2edit.models.chat_cycle import ChatCycle
from chat2edit.models.chat_message import ChatMessage
from chat2edit.providers.fabric.fabric_exemplars import FABRIC_EXEMPLARS
from chat2edit.providers.fabric.models.fabric_canvas import FabricCanvas
from chat2edit.providers.fabric.models.fabric_collection import \
    FabricCollection
from chat2edit.providers.fabric.models.fabric_group import FabricGroup
from chat2edit.providers.fabric.models.fabric_image_object import \
    FabricImageObject
from chat2edit.providers.fabric.models.fabric_text_box import FabricTextBox
from chat2edit.providers.provider import Provider
from chat2edit.tools.image.image_inpainter import ImageInpainter
from chat2edit.tools.image.prompt_based_segmenter import PromptBasedSegmenter
from chat2edit.utils.image import pil_image_to_data_url
from PIL import Image as ImageModule

Image = TypeVar("Image", FabricCollection, None)
Object = TypeVar("Object", FabricImageObject, None)
Text = TypeVar("Text", FabricTextBox, None)


class FabricProvider(Provider):
    def __init__(
        self,
        function_names: Iterable[str],
        segmenter: PromptBasedSegmenter,
        inpainter: ImageInpainter,
    ) -> None:
        super().__init__()
        self._segmenter = segmenter
        self._inpainter = inpainter
        self._function_names = function_names

    def get_functions(self) -> List[Callable[..., Any]]:
        return [getattr(self, name) for name in self._function_names]

    def get_exemplars(self) -> Iterable[Iterable[ChatCycle]]:
        return FABRIC_EXEMPLARS

    def response_user(self, text: str, images: Optional[List[Image]] = None) -> None:
        images = images or []
        self._reponse(ChatMessage("system", text, images))

    def move(
        self,
        image: Image,
        target: Union[Image, Object, Text],
        position: Tuple[int, int],
    ) -> None:
        if not isinstance(image, FabricCanvas):
            self._error(
                f"Argument 'image' in 'move' method must be of type 'Image', not '{type(image).__name__}'"
            )
            return

        if not isinstance(target, (FabricImageObject, FabricGroup, FabricTextBox)):
            self._error(
                f"Argument 'target' in 'move' method must be of type 'Image', 'Object', or 'Text', not '{type(image).__name__}'"
            )
            return

        if (
            not isinstance(position, tuple)
            or len(position) != 2
            or not all(isinstance(coord, int) for coord in position)
        ):
            self._error(
                "Argument 'position' in 'insert' method must be a tuple with two integer elements."
            )
            return

        if not image.contains(target):
            self._error("The target is not within the image.")
            return

        if (
            position[0] > image.backgroundImage.width
            or position[1] > image.backgroundImage.width
        ):
            self._warning("The specified position exceeds the size of the image.")

        if isinstance(target, FabricImageObject) and not target.inpainted:
            self._inpaint(image, target)

        target.left = position[0]
        target.top = position[1]

    def rotate(
        self,
        image: Image,
        angle: float,
        direction: Literal["cw", "ccw"],
        target: Optional[Union[Image, Object, Text]] = None,
    ) -> None:
        if not isinstance(image, FabricCanvas):
            self._error(
                f"Argument 'image' in 'rotate' method must be of type 'Image', not '{type(image).__name__}'"
            )
            return

        if not isinstance(angle, (float, int)):
            self._error("Argument 'angle' in 'rotate' method must be a number")
            return

        if direction not in ["cw", "ccw"]:
            self._error(
                "Argument 'direction' in 'rotate' method must be either 'cw' or 'ccw'"
            )
            return

        if target is None:
            image.backgroundImage.angle += angle if direction == "cw" else -angle
            return

        if not isinstance(target, (FabricImageObject, FabricGroup, FabricTextBox)):
            self._error(
                f"Argument 'target' in 'rotate' method must be of type 'Image', 'Object', or 'Text', not '{type(target).__name__}'"
            )
            return

        if target and not image.contains(target):
            self._error("The target is not within the image.")
            return

        target.angle += angle if direction == "cw" else -angle

        if isinstance(target, FabricImageObject) and not target.inpainted:
            self._inpaint(image, target)

    def flip(
        self,
        image: Image,
        axis: Literal["x", "y"],
        target: Optional[Union[Image, Object, Text]] = None,
    ) -> None:
        if not isinstance(image, FabricCanvas):
            self._error(
                f"The 'image' argument in the 'flip' method must be of type 'Image', not '{type(image).__name__}'"
            )
            return

        if axis not in ["x", "y"]:
            self._error(
                "The 'axis' argument in the 'flip' method must be either 'x' or 'y'"
            )
            return

        if target is None:
            if axis == "x":
                image.backgroundImage.flipX = not image.backgroundImage.flipX
            else:
                image.backgroundImage.flipY = not image.backgroundImage.flipY
            return

        if not isinstance(target, (FabricImageObject, FabricGroup, FabricTextBox)):
            self._error(
                f"The 'target' argument in the 'flip' method must be of type 'Image', 'Object', or 'Text', not '{type(target).__name__}'"
            )
            return

        if target and not image.contains(target):
            self._error("The target is not within the image.")
            return

        if axis == "x":
            target.flipX = not target.flipX
        else:
            target.flipY = not target.flipY

        if isinstance(target, FabricImageObject) and not target.inpainted:
            self._inpaint(image, target)

    def scale(
        self,
        image: Image,
        target: Union[Image, Object, Text],
        factor: float,
        axis: Optional[Literal["x", "y"]] = None,
    ) -> None:
        if not isinstance(image, FabricCanvas):
            self._error(
                f"The 'image' argument in the 'scale' method must be of type 'Image', not '{type(image).__name__}'"
            )
            return

        if not isinstance(target, (FabricImageObject, FabricGroup, FabricTextBox)):
            self._error(
                f"The 'target' argument in the 'scale' method must be of type 'Image', 'Object', or 'Text', not '{type(target).__name__}'"
            )
            return

        if not isinstance(factor, (float, int)):
            self._error("The 'factor' argument in the 'scale' method must be a number")
            return

        if axis not in (None, "x", "y"):
            self._error(
                "The 'axis' argument in the 'scale' method must be either 'x', 'y', or None"
            )
            return

        if not image.contains(target):
            self._error("The target is not within the image.")
            return

        if axis is None:
            target.scaleX *= factor
            target.scaleY *= factor
        elif axis == "x":
            target.scaleX *= factor
        elif axis == "y":
            target.scaleY *= factor

        if isinstance(target, FabricImageObject) and not target.inpainted:
            self._inpaint(image, target)

    def insert(
        self,
        image: Image,
        target: Union[Image, Object, Text],
        position: Optional[Tuple[int, int]] = None,
    ) -> None:
        if not isinstance(image, FabricCanvas):
            self._error(
                f"The 'image' argument in the 'insert' method must be of type 'Image', not '{type(image).__name__}'"
            )
            return

        if not isinstance(target, (FabricImageObject, FabricGroup, FabricTextBox)):
            self._error(
                f"The 'target' argument in the 'insert' method must be of type 'Image', 'Object', or 'Text', not '{type(target).__name__}'"
            )
            return

        if position is not None:
            if (
                not isinstance(position, tuple)
                or len(position) != 2
                or not all(isinstance(coord, int) for coord in position)
            ):
                self._error(
                    "The 'position' argument in the 'insert' method must be a tuple with two integer elements."
                )
                return

            if (
                position[0] > image.backgroundImage.width
                or position[1] > image.backgroundImage.width
            ):
                self._warning("The specified position exceeds the size of the image.")

        image.add(target)
        if position is not None:
            target.left = position[0]
            target.top = position[1]

    def remove(self, image: Image, target: Union[Image, Object, Text]) -> None:
        if not isinstance(image, FabricCanvas):
            self._error(
                f"The 'image' argument in the 'remove' method must be 'Image', not '{type(image).__name__}'"
            )
            return

        if not isinstance(target, (FabricImageObject, FabricGroup, FabricTextBox)):
            self._error(
                f"The 'target' argument in the 'remove' method must be 'Image', 'Object', or 'Text', not '{type(target).__name__}'"
            )
            return

        if not image.contains(target):
            self._error("The target is not within the image.")
            return

        image.remove(target)
        if isinstance(target, FabricImageObject) and not target.inpainted:
            self._inpaint(image, target)

    def replace(self, target: Union[Image, Object, Text], prompt: str) -> None:
        pass

    def apply_filter(
        self,
        image: Image,
        filter_name: str,
        filter_value: float = 1.0,
        target: Optional[Union[Image, Object]] = None,
    ) -> None:
        if not isinstance(image, FabricCanvas):
            self._error(
                f"The 'image' argument in the 'apply_filter' method must be 'Image', not '{type(image).__name__}'"
            )
            return

        if target and not isinstance(
            target, (FabricImageObject, FabricGroup, FabricTextBox)
        ):
            self._error(
                f"The 'target' argument in the 'apply_filter' method must be 'Image' or 'Object', not '{type(target).__name__}'"
            )
            return

        filt = None
        filter_value -= 1
        if self._compare_filter_names(filter_name, ["grayscale"]):
            filt = {"type": "Grayscale", "mode": "average"}
        elif self._compare_filter_names(filter_name, ["invert", "negative"]):
            filt = {"type": "Invert"}
        elif self._compare_filter_names(filter_name, ["brightness"]):
            filt = {"type": "Brightness", "brightness": filter_value}
        elif self._compare_filter_names(filter_name, ["blur"]):
            filt = {"type": "Blur", "blur": filter_value}
        elif self._compare_filter_names(filter_name, ["contrast"]):
            filt = {"type": "Contrast", "contrast": filter_value}
        elif self._compare_filter_names(filter_name, ["noise"]):
            filt = {"type": "Noise", "noise": filter_value}
        elif self._compare_filter_names(filter_name, ["pixelate"]):
            filt = {"type": "Pixelate", "blocksize": filter_value * 10}
        # elif self._compare_filter_names(filter_name, ["temperature", "warmth"]):
        #     filt = Filter(name="temperature", value=filter_value)
        # elif self._compare_filter_names(filter_name, ["saturation"]):
        #     filt = Filter(name="saturation", value=filter_value)
        # elif self._compare_filter_names(filter_name, ["opacity", "transparent"]):
        #     filt = Filter(name="opacity", value=filter_value)
        else:
            self._set_signal(
                status="error", text=f"Filter '{filter_name}' is not supported"
            )
            return

        if target is None:
            if isinstance(image, FabricCanvas):
                image.backgroundImage.filters.append(filt)
            for obj in image.objects:
                obj.filters.append(filt)
        else:
            target.filters.append(filt)

    def detect(self, image: Image, prompt: str) -> List[Object]:
        if not isinstance(image, FabricCanvas):
            self._error(
                f"The 'image' argument in the 'detect' method must be 'Image', not '{type(image).__name__}'"
            )
            return []

        if not isinstance(prompt, str):
            self._error(
                f"The 'prompt' argument in the 'detect' method must be a string, not '{type(prompt).__name__}'"
            )
            return []

        detected_objects = [
            obj
            for obj in image.objects
            if self._compare_object_labels(prompt, list(obj.labelToScore.keys()))
        ]
        if len(detected_objects) != 0:
            return detected_objects

        parent_pil_image = image.backgroundImage.to_image()
        scores, masks = self._segmenter(parent_pil_image, prompt)
        for score, mask in zip(scores, masks):
            xmin, ymin, xmax, ymax = obj_box = ImageModule.fromarray(mask).getbbox()
            obj_width, obj_height = obj_size = xmax - xmin, ymax - ymin
            obj_pil_image = ImageModule.new("RGBA", obj_size)
            obj_pil_image.format = "PNG"
            obj_pil_image.paste(
                parent_pil_image.crop(obj_box),
                mask=ImageModule.fromarray(mask).crop(obj_box),
            )
            obj_data_url = pil_image_to_data_url(obj_pil_image)
            obj = FabricImageObject(
                parentId=image.id,
                type="image",
                left=xmin,
                top=ymin,
                width=obj_width,
                height=obj_height,
                labelToScore={prompt: score},
                src=obj_data_url,
            )
            image.add(obj)
            detected_objects.append(obj)

        annotated_image = image.get_copy()
        annotated_image.annotate(annotated_image.objects[-len(detected_objects) :])
        self._set_signal(
            status="warning",
            text=f"Detected {len(detected_objects)} '{prompt}' in the image",
            attachments=[annotated_image],
        )
        return detected_objects

    def generate(
        self, prompt: str, category: Literal["object", "image"]
    ) -> Union[Object, Image]:
        pass

    def create_text(
        self,
        content: str,
        color: Optional[str] = None,
        font: Optional[str] = None,
        size: Optional[int] = None,
        style: Optional[str] = None,
        weight: Optional[str] = None,
    ) -> Text:
        return FabricTextBox(
            type="textbox",
            text=content,
            color=color,
            font_family=font,
            font_size=size,
            font_style=style,
            font_weight=weight,
        )

    def get_info(
        self,
        target: Union[Image, Object, Text],
        category: Literal["position", "size", "color", "text"],
    ) -> Any:
        if isinstance(target, FabricCanvas):
            target = target.backgroundImage

        if category == "position":
            return target.left, target.top
        if category == "size":
            return target.width, target.height
        if category == "color":
            raise NotImplementedError("Color getter not implemented")
        if category == "text":
            if isinstance(target, FabricTextBox):
                return target.text

            self._error("Can only get text from object of type 'Text'")

    def _inpaint(
        self, parent: Union[FabricCanvas, FabricGroup], obj: FabricImageObject
    ) -> None:
        base_image = None
        if isinstance(parent, FabricCanvas):
            base_image = parent.backgroundImage.to_image()
        elif isinstance(parent, FabricGroup):
            base_image = parent.objects[0].to_image()

        width, height = base_image.size
        obj_image = obj.to_image()
        obj_fit_mask = np.array(obj_image.convert("L"))
        obj_mask = np.zeros((height, width), dtype=np.uint8)
        xmin, ymin, xmax, ymax = obj.get_box()
        obj_mask[ymin:ymax, xmin:xmax] = np.where(obj_fit_mask != 0, 255, 0)
        inpainted_image = self._inpainter(base_image, obj_mask)
        inpainted_image.format = base_image.format

        if isinstance(parent, FabricCanvas):
            parent.backgroundImage.src = pil_image_to_data_url(inpainted_image)
        elif isinstance(parent, FabricGroup):
            parent.objects[0].src = pil_image_to_data_url(inpainted_image)

        obj.inpainted = True

    def _compare_filter_names(
        self, filter_name: str, check_filter_names: Iterable[str]
    ) -> bool:
        for check_name in check_filter_names:
            name1 = filter_name.lower()
            name2 = check_name.lower()
            if name1 in name2 or name2 in name1:
                return True

        return False

    def _compare_object_labels(self, label: str, check_labels: List[str]) -> bool:
        for check_label in check_labels:
            label1 = label.lower()
            label2 = check_label.lower()
            if label1 in label2 or label2 in label1:
                return True

        return False
