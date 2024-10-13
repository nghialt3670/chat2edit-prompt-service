from abc import ABC, abstractmethod
from typing import Literal, Union

from pydantic import BaseModel, Field


class AdjustableFilter(ABC):
    @abstractmethod
    def merge(self, filt: "AdjustableFilter") -> None:
        pass


class GrayscaleFilter(BaseModel):
    type: Literal["Grayscale"] = Field(default="Grayscale")
    mode: str = Field(default="average")


class InvertFilter(BaseModel):
    type: Literal["Invert"] = Field(default="Invert")
    alpha: bool = Field(default=False)
    invert: bool = Field(default=True)


class BrightnessFilter(BaseModel, AdjustableFilter):
    type: Literal["Brightness"] = Field(default="Brightness")
    brightness: float = Field(...)

    def merge(self, filt: "BrightnessFilter") -> None:
        self.brightness += filt.brightness


class BlurFilter(BaseModel, AdjustableFilter):
    type: Literal["Blur"] = Field(default="Blur")
    blur: float = Field(...)

    def merge(self, filt: "BlurFilter") -> None:
        self.blur += filt.blur


class ContrastFilter(BaseModel, AdjustableFilter):
    type: Literal["Contrast"] = Field(default="Contrast")
    contrast: float = Field(...)

    def merge(self, filt: "ContrastFilter") -> None:
        self.contrast += filt.contrast


class NoiseFilter(BaseModel, AdjustableFilter):
    type: Literal["Noise"] = Field(default="Noise")
    noise: float = Field(...)

    def merge(self, filt: "NoiseFilter") -> None:
        self.noise += filt.noise


class PixelateFilter(BaseModel, AdjustableFilter):
    type: Literal["Pixelate"] = Field(default="Pixelate")
    blocksize: int = Field(...)

    def merge(self, filt: "PixelateFilter") -> None:
        self.blocksize += filt.blocksize


class SaturationFilter(BaseModel, AdjustableFilter):
    type: Literal["Saturation"] = Field(default="Saturation")
    saturation: float = Field(...)

    def merge(self, filt: "SaturationFilter") -> None:
        self.saturation += filt.saturation


FabricFilter = Union[
    GrayscaleFilter,
    InvertFilter,
    BrightnessFilter,
    BlurFilter,
    ContrastFilter,
    NoiseFilter,
    PixelateFilter,
    SaturationFilter,
]
