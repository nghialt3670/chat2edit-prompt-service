from typing import Literal

from pydantic import BaseModel, Field


class Settings(BaseModel):
    theme: Literal["dark", "light"] = Field(default="dark")
