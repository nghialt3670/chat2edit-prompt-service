from typing import Literal

from pydantic import Field

from core.providers.fabric.models.fabric_object import FabricObject


class FabricTextbox(FabricObject):
    type: Literal["Textbox"] = Field(default="Textbox")
    fontSize: int = Field(default=40)
    fontWeight: str = Field(default="normal")
    fontFamily: str = Field(default="Times New Roman")
    fontStyle: str = Field(default="normal")
    lineHeight: float = Field(default=1.16)
    charSpacing: int = Field(default=0)
    textAlign: str = Field(default="left")
    underline: bool = Field(default=False)
    overline: bool = Field(default=False)
    linethrough: bool = Field(default=False)
    textBackgroundColor: str = Field(default="")
    text: str
