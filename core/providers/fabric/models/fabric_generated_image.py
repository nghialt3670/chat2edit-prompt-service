from chat2edit.providers.fabric.models.fabric_image import FabricImage


class FabricGeneratedImage(FabricImage):
    prompt: str

    def get_copy(self) -> "FabricGeneratedImage":
        return FabricGeneratedImage(
            **FabricImage.get_copy(self).__dict__,
            prompt=self.prompt,
        )
