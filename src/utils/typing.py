import types
from inspect import Parameter, _ParameterKind
from typing import Any, TypeVar


def get_annotation_name(annotation: Any) -> str:
    if "__name__" in annotation.__dict__:
        return annotation.__name__

    return extract_annotation_suffix_name(annotation)


def extract_built_in_type_name(type_obj: Any) -> str:
    return type_obj.__name__


def extract_annotation_suffix_name(type_obj: Any) -> str:
    param = str(Parameter("_", _ParameterKind.KEYWORD_ONLY, annotation=type_obj))
    return param.split(": ")[-1].replace("~", "")
