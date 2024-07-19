from chat2edit.providers.fabric.models.fabric_collection import \
    FabricCollection
from chat2edit.providers.fabric.models.fabric_object import FabricObject


class FabricGroup(FabricObject, FabricCollection):
    def get_copy(self) -> "FabricGroup":
        return FabricGroup(
            **FabricObject.get_copy(self).__dict__,
            **FabricCollection.get_copy(self).__dict__
        )
