from typing import Dict

from core.providers.fabric_provider import FabricProvider
from core.providers.provider import Provider
from core.types.provider import Provider as ProviderType

fabric_provider = FabricProvider(
    [
        "response_user",
        "detect",
        "segment",
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
        "get_size",
    ]
)

PROVIDERS = {ProviderType.FABRIC: fabric_provider}


def get_providers() -> Dict[str, Provider]:
    return PROVIDERS
