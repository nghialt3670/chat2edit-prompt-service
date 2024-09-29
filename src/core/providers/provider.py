import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Literal, Optional

from pydantic import TypeAdapter

from lib.env import ENV
from models.chat import Context
from models.phase import ChatPhase, Execution, Message
from schemas.file import File
from schemas.language import Language


class Provider(ABC):
    def __init__(self) -> None:
        self._language: Language = None
        self._execution: Execution = None
        self._context: Context = None
        self._context_dict: Dict[str, Any] = None
        self._id_to_varname: Dict[str, str] = {}

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
    def encode_context(self, context: Dict[str, Any]) -> bytes:
        pass

    @abstractmethod
    def decode_context(self, data: bytes) -> Dict[str, Any]:
        pass

    @abstractmethod
    def filter_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def convert_file_to_objects(self, file: File) -> List[Any]:
        pass

    @abstractmethod
    def convert_object_to_file(self, obj: Any) -> File:
        pass

    def set_context(self, context: Context) -> None:
        self._context = context

    def get_context(self) -> Context:
        return self._context

    def set_context_buffer(self, buffer: bytes) -> None:
        self._context_dict = self.decode_context(buffer)
        self._context_dict.update({f.__name__: f for f in self.get_functions()})

    def get_context_buffer(self) -> bytes:
        filtered_context = self.filter_context(self._context)
        return self.encode_context(filtered_context)

    def get_context_dict(self) -> Dict[str, Any]:
        return self._context_dict

    def assign_files(self, files: List[File]) -> List[str]:
        varnames = []

        for file in files:
            file_id = file.name.split(".")[0]
            file_varnames = None

            if file_id in self._context.id_to_varnames:
                file_varnames = self._context.id_to_varnames[file_id]
                varnames.extend(file_varnames)

            else:
                for obj in self.convert_file_to_objects(file):
                    alias = self.get_alias(obj)
                    idx = self._context.alias_to_count.get(alias, 0)
                    self._context.alias_to_count[alias] = idx + 1
                    obj_varname = f"{alias}{idx}"
                    self._context_dict[obj_varname] = obj
                    file_varnames.append(obj_varname)

            varnames.extend(file_varnames)
            self._context.id_to_varnames[file_id] = file_varnames

        return varnames

    def create_files(self, varnames: List[str]) -> List[File]:
        objects = [self._context_dict[varname] for varname in varnames]
        return [self.convert_object_to_file(obj) for obj in objects]

    def set_language(self, language: Language) -> None:
        self._language = language

    def set_execution(self, execution: Execution) -> None:
        self._execution = execution

    def add_to_context(self, key: str, value: Any) -> None:
        self._context_dict[key] = value
        self._id_to_varname[id(value)] = key

    def feedback(
        self, type: Literal["info", "warning", "error"], text: str, varnames: List[str]
    ) -> None:
        self._execution.feedback = Message(
            src="system", type=type, text=text, varnames=varnames
        )

    def get_varname(self, value: Any) -> None:
        return self._id_to_varname[id(value)]

    def response_user(self, text: str, attachments: List[Any] = []) -> None:
        varnames = [self.get_varname(att) for att in attachments]
        self._execution.response = Message(
            src="llm", type="response", text=text, varnames=varnames
        )
