from typing import Optional

from chat2edit.providers.fabric.models.fabric_object import FabricObject
from pydantic import Field


class FabricTextBox(FabricObject):
    text: str
    fontFamily: str = Field(default="Times New Roman", repr=False)
    fontSize: int = Field(default=60, repr=False)
    fontStyle: str = Field(default="normal", repr=False)
    fontWeight: str = Field(default="normal", repr=False)

    def get_copy(self) -> FabricObject:
        return FabricTextBox(
            **FabricObject.get_copy(self).__dict__,
            fontFamily=self.fontFamily,
            fontSize=self.fontSize,
            fontStyle=self.fontStyle,
            fontWeight=self.fontWeight,
            text=self.text
        )
