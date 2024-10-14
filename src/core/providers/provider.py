import inspect
import traceback
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

from pydantic import TypeAdapter

from models.phase import ChatPhase, Message
from schemas.file import File
from schemas.language import Language
from utils.env import ENV
from utils.typing import get_annotation_name

INVALID_PARAMETER_TEMPLATE = "In `{f}` function, parameter `{p}` must be of type `{t1}`, but received type `{t2}`"
UNEXPECTED_ERROR_OCCURRED_TEMPLATE = (
    "Unexpected error occurred while executing `{f}` function: `{e}`."
)


def validate_params_by_annotations(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        signature = inspect.signature(func)
        parameters = signature.parameters

        arguments = signature.bind(self, *args, **kwargs)
        arguments.apply_defaults()

        for param_name, param in parameters.items():
            param_value = arguments.arguments[param_name]
            annotation = param.annotation
            if annotation is inspect.Parameter.empty:
                continue

            try:
                TypeAdapter(annotation).validate_python(param_value)
            except:
                annotation_name = get_annotation_name(annotation)
                value_type_name = type(param_value).__name__
                feedback_text = INVALID_PARAMETER_TEMPLATE.format(
                    f=func.__name__,
                    p=param_name,
                    t1=annotation_name,
                    t2=value_type_name,
                )
                self._set_feedback("error", feedback_text)
                return None

        return await func(self, *args, **kwargs)

    return wrapper


def catch_unexpected_error(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self._language or not self._context:
            raise RuntimeError("Provider has not been initialized")

        try:
            return await func(self, *args, **kwargs)
        except Exception as e:
            feedback_text = UNEXPECTED_ERROR_OCCURRED_TEMPLATE.format(
                f=func.__name__, e=e
            )
            self._set_feedback("error", feedback_text)
            return None

    return wrapper


def prompt_function(*, index: int, description: str):
    def decorator(func: Callable):
        @catch_unexpected_error
        @validate_params_by_annotations
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            return await func(self, *args, **kwargs)

        setattr(wrapper, "__prompt_index__", index)
        setattr(wrapper, "__description__", description)
        return wrapper

    return decorator


class Provider(ABC):
    def __init__(
        self,
        lang_to_exemplars: Dict[Language, List[ChatPhase]],
        context_value_types: Tuple[Any],
        type_to_alias: Dict[Any, str],
    ) -> None:
        self._lang_to_exemplars = lang_to_exemplars
        context_value_type = Union[context_value_types]
        self._context_adapter = TypeAdapter(Dict[str, context_value_type])
        self._context_value_adapter = TypeAdapter(context_value_type)
        self._type_to_alias = type_to_alias
        self._language: Language = None
        self._context: Dict[str, Any] = None
        self._feedback: Message = None
        self._response: Message = None

    @abstractmethod
    def convert_file_to_objects(self, file: File) -> List[Any]:
        pass

    @abstractmethod
    def convert_object_to_file(self, obj: Any) -> File:
        pass

    def get_context(self) -> Dict[str, Any]:
        return self._context

    def get_feedback(self) -> Optional[Message]:
        return self._feedback

    def get_response(self) -> Optional[Message]:
        return self._response

    def get_exemplars(self) -> List[ChatPhase]:
        return self._lang_to_exemplars[self._language]

    def get_varname(self, value: Any) -> None:
        id_to_varname = {id(v): k for k, v in self._context.items()}
        return id_to_varname[id(value)]

    def get_obj_alias(self, obj: Any) -> str:
        return self._type_to_alias[type(obj)]

    def get_prompt_functions(self) -> List[Callable]:
        attributes = [getattr(self, name) for name in dir(self)]
        is_prompt_func = lambda x: callable(x) and hasattr(x, "__prompt_index__")
        prompt_functions = [a for a in attributes if is_prompt_func(a)]
        get_prompt_index = lambda x: getattr(x, "__prompt_index__")
        return sorted(prompt_functions, key=get_prompt_index)

    def set_language(self, language: Language) -> None:
        self._language = language

    def clear_feedback(self) -> None:
        self._feedback = None

    def load_context_from_buffer(self, buffer: bytes) -> None:
        self._context = self._context_adapter.validate_json(buffer)
        self._context.update({f.__name__: f for f in self.get_prompt_functions()})

    def save_context_to_buffer(self) -> bytes:
        filtered_context = self._filter_context(self._context)
        return self._context_adapter.dump_json(filtered_context)

    def _filter_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        invalid_keys = {
            k for k, v in context.items() if not self._check_context_value(v)
        }

        for k in invalid_keys:
            context.pop(k)

        return context

    def _check_context_value(self, value: Any) -> bool:
        try:
            self._context_value_adapter.validate_python(value)
            return True

        except:
            return False

    def _set_feedback(
        self,
        type: Literal["info", "warning", "error"],
        text: str,
        varnames: List[str] = [],
    ) -> None:
        self._feedback = Message(src="system", type=type, text=text, varnames=varnames)
        
    def _update_context(self, key: str, value: Any) -> None:
        self._context[key] = value
