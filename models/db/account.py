from pydantic import Field

from models.db.document import Document
from models.db.settings import Settings


class Account(Document):
    settings: Settings = Field(default_factory=Settings)
