from typing import Any, Dict, List, Tuple

from fastapi import UploadFile

from core.schemas.fabric.fabric_canvas import FabricCanvas
from database.models.conversation.context import Context
from database.models.conversation.variable import Variable
from database.services.file_service import FileService


def load_variable(
    var: Variable, name_to_class: Dict[str, Any], file_service: FileService
) -> Tuple[str, Any]:
    if var.type == "primitive":
        return var.name, var.value

    elif var.type == "object":
        return var.name, name_to_class[var.class_name](var.value)

    elif var.type == "list":
        return var.name, [
            load_variable(v, name_to_class, file_service) for v in var.value
        ]

    elif var.type == "file":
        file_object = file_service.get(var.value)
        file_content = file_object.read()
        json_str = file_content.decode()
        return var.name, name_to_class[var.class_name].from_raw(json_str)


async def save_variable(
    name: str, value: Any, file_service: FileService, user_id: str
) -> Variable:
    if isinstance(value, FabricCanvas):
        file = value.to_file()
        await file_service.save_upload_file(file, value.id, user_id)
        return Variable(
            type="file", class_name="FabricCanvas", name=name, value=value.id
        )

    elif isinstance(value, (int, float, str)):
        return Variable(type="primitive", name=name, value=value)

    elif isinstance(value, list):
        return Variable(
            type="list",
            name=name,
            value=[
                save_variable(f"{name}_[{idx}]", v, file_service, user_id)
                for idx, v in enumerate(value)
            ],
        )


def create_obj_varnames(
    objects: List[Any], type_to_count: Dict[str, int], class_to_type: Dict[Any, str]
) -> List[str]:
    varnames = []
    for obj in objects:
        obj_type = class_to_type[type(obj)]
        type_count = type_to_count.get(obj_type, 0)
        type_to_count[obj_type] = type_count + 1
        varnames.append(f"{obj_type}_{type_count}")

    return varnames


async def file_to_obj(file_id: str, file: UploadFile) -> Any:
    if file.filename.endswith(".canvas"):
        return await FabricCanvas.from_file(file, id=file_id)
    else:
        raise NotImplementedError()


def object_to_file(obj: Any) -> UploadFile:
    if isinstance(obj, FabricCanvas):
        return obj.to_file()
    else:
        raise NotImplementedError()
