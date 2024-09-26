import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Literal, Optional

import aiohttp
from pydantic import TypeAdapter

from models.db.chat_phase import ChatPhase
from models.db.context import Context
from models.db.context_message import ContextMessage
from models.db.execution import Execution
from models.file import File
from models.language import Language
from schemas.attachment_schema import AttachmentSchema
from utils.env import ENV


class Provider(ABC):
    def __init__(self) -> None:
        self._language: Language = None
        self._execution: Execution = None
        self._context: Context = None

    @abstractmethod
    def get_functions(self) -> List[Callable]:
        pass

    @abstractmethod
    def get_exemplars(self) -> List[List[ChatPhase]]:
        pass

    @abstractmethod
    def get_alias(self, obj) -> str:
        pass

    @abstractmethod
    def filter_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def encode_context(self, context: Dict[str, Any]) -> bytes:
        pass

    @abstractmethod
    def decode_context(self, data: bytes) -> Dict[str, Any]:
        pass

    @abstractmethod
    def filter_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def convert_file_to_objects(self, file: File) -> Any:
        pass

    @abstractmethod
    def convert_object_to_file(self, obj: Any) -> File:
        pass

    def set_context(self, context: Context) -> None:
        self._context = context
        self._context.data = self.decode_context(context.data)
        self._context.data.update({f.__name__: f for f in self.get_functions()})
        self._context = context

    def get_context(self) -> Context:
        filtered_context = self.filter_context(self._context.data)
        self._context.data = self.encode_context(filtered_context)
        return self._context

    def get_context_dict(self) -> Dict[str, Any]:
        return self._context.data

    async def assign_attachments(
        self, attachments: List[AttachmentSchema]
    ) -> List[str]:
        varnames = []
        files = [await File.from_attachment(att) for att in attachments]

        for att, file in zip(attachments, files):
            if att.type == "file":
                objects = self.convert_file_to_objects(file)
                att_varnames = []

                for obj in objects:
                    alias = self.get_alias(obj)
                    idx = self._context.alias_to_count.get(alias, 0)
                    self._context.alias_to_count[alias] = idx + 1
                    varname = f"{alias}{idx}"
                    self._context.data[varname] = obj
                    att_varnames.append(varnames)

                varnames.extend(att_varnames)
                self._context.id_to_varnames[att.id] = att_varnames

            elif att.type == "link":
                raise NotImplementedError("Link attachment not implemented")

            elif att.type == "ref":
                att_varnames = self._context.id_to_varnames[att.ref]
                varnames.extend(att_varnames)

        return varnames

    async def create_attachments(self, varnames: List[str]) -> List[AttachmentSchema]:
        if not varnames:
            return []

        objects = [self._context.data[varname] for varname in varnames]
        files = [self.convert_object_to_file(obj) for obj in objects]
        api_base_url = ENV.ATTACHMENT_SERVICE_API_BASE_URL
        endpoint = f"{api_base_url}/api/attachments/files/batch"

        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.FormData()
            for file in files:
                form_data.add_field(
                    "files",
                    file.data,
                    filename=file.name,
                    content_type=file.content_type,
                )

            async with session.post(endpoint, data=form_data) as response:
                payload = await response.json()
                return TypeAdapter(List[AttachmentSchema]).validate_python(payload)

    def set_language(self, language: Language) -> None:
        self._language = language

    def set_execution(self, execution: Execution) -> None:
        self._execution = execution

    def add_to_context(self, key: str, value: Any) -> None:
        self._context.data[key] = value

    def feedback(
        self, type: Literal["info", "warning", "error"], text: str, varnames: List[str]
    ) -> None:
        self._execution.feedback = ContextMessage(
            src="system", type=type, text=text, varnames=varnames
        )

    def get_varname(self, obj: Any) -> None:
        id_to_varname = {id(v): k for k, v in self._context.data.items()}
        return id_to_varname[id(obj)]

    def response_user(self, text: str, attachments: List[Any] = []) -> None:
        id_to_varname = {id(v): k for k, v in self._context.data.items()}
        varnames = [id_to_varname[id(att)] for att in attachments]
        self._execution.response = ContextMessage(
            src="llm", type="response", text=text, varnames=varnames
        )
