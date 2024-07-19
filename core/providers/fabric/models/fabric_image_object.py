import copy
from typing import Dict, Tuple

from chat2edit.providers.fabric.models.fabric_image import FabricImage


class FabricImageObject(FabricImage):
    labelToScore: Dict[str, float]
    inpainted: bool = False

    def get_copy(self) -> "FabricImageObject":
        return FabricImageObject(
            **FabricImage.get_copy(self).__dict__,
            labelToScore=copy.deepcopy(self.labelToScore),
            inpainted=self.inpainted,
        )
