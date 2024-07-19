from typing import TypeVar

from core.schemas.fabric import FabricCanvas, FabricImage, FabricTextbox

Image = TypeVar("Image", FabricCanvas, None)
Object = TypeVar("Object", FabricImage, None)
Text = TypeVar("Text", FabricTextbox, None)
