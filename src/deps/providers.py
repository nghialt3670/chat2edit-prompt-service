from core.providers.fabric.fabric_provider import FabricProvider
from core.providers.provider import Provider
from schemas.provider import Provider as ProviderType

FABRIC_PROVIDER_FUNCTIONS = [
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


def get_provider(type: ProviderType) -> Provider:
    if type == "fabric":
        return FabricProvider(FABRIC_PROVIDER_FUNCTIONS)

    raise ValueError(f"Invalid provider type: {type}")
