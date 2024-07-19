from typing import List

from core.schemas.fabric.fabric_object import FabricObject


class FabricTextbox(FabricObject):
    type: str = "Textbox"
    fontSize: int = 40
    fontWeight: str = "normal"
    fontFamily: str = "Times New Roman"
    fontStyle: str = "normal"
    lineHeight: float = 1.16
    text: str
    charSpacing: int = 0
    textAlign: str = "left"
    styles: List = []
    pathStartOffset: int = 0
    pathSide: str = "left"
    pathAlign: str = "baseline"
    underline: bool = False
    overline: bool = False
    linethrough: bool = False
    textBackgroundColor: str = ""
    direction: str = "ltr"
    minWidth: int = 20
    splitByGrapheme: bool = False
