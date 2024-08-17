from typing import Dict

from core.providers.fabric_provider import FabricProvider
from core.providers.provider import Provider

fabric_provider = FabricProvider(
    [
        "response_user",
        "detect",
        "remove",
        "filter",
        "rotate",
        "flip",
        "scale",
        "move",
        "shift",
        "replace",
        "create_text",
        "get_position",
        "get_size"
    ]
)

PROVIDERS = {"fabric": fabric_provider}


def get_providers() -> Dict[str, Provider]:
    return PROVIDERS
