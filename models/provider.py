from enum import Enum


class Provider(str, Enum):
    FABRIC = "fabric"
    PANDAS = "pandas"
