from core.providers.fabric.fabric_provider import FabricProvider
from core.providers.provider import Provider
from schemas.provider import Provider as ProviderType


def get_provider(type: ProviderType) -> Provider:
    if type == "fabric":
        return FabricProvider()

    raise ValueError(f"Invalid provider type: {type}")
