import traceback
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from core.controller.fullfill import fullfill
from core.llms.llm import LLM
from core.providers.fabric_provider import FabricProvider
from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.controller.context import (
    create_obj_varnames,
    file_to_obj,
    load_variable,
    save_variable,
)
from database.models import Conversation, ChatMessage
from database.services import ConvService
from database.services.file_service import FileService
from database.services.user_service import UserService
from dependencies.authorization import clerk_validate_user
from dependencies.database import get_conv_service, get_file_service, get_user_service
from dependencies.llms import get_llm

router = APIRouter(prefix="/api/v1")
provider = FabricProvider(
    ["response_user", "detect", "remove", "filter", "rotate", "flip", "scale"]
)


class ChatResponse(BaseModel):
    status: Literal["success", "error"]
    text: str
    file_ids: List[str] = Field(default_factory=list)


NAME_TO_CLASS = {"FabricCanvas": FabricCanvas}
CLASS_TO_TYPE = {FabricCanvas: "image"}
MAX_CYCLES = 4


@router.post("/chat/{conv_id}", response_model=ChatResponse)
async def chat(
    conv_id: str,
    text: str = Form(...),
    file_ids: List[str] = Form(...),
    timestamp: int = Form(...),
    files: Optional[List[UploadFile]] = File([]),
    llm: LLM = Depends(get_llm),
    clerk_user_id: str = Depends(clerk_validate_user),
    user_service: UserService = Depends(get_user_service),
    conv_service: ConvService = Depends(get_conv_service),
    file_service: FileService = Depends(get_file_service),
):
    try:
        user = user_service.find_by_clerk_user_id(clerk_user_id)
        conv = conv_service.find_by_id_and_user_id(conv_id, user.id)

        if not conv:
            conv = Conversation(user_id=user.id)

        mappings = {}
        for var in conv.context.variables:
            name, value = load_variable(var, NAME_TO_CLASS, file_service)
            mappings[name] = value
            
        objects = [file_to_obj(file_id, file) for file_id, file in zip(file_ids, files)]
        varnames = create_obj_varnames(
            objects, conv.context.type_to_count, CLASS_TO_TYPE
        )
        request = ChatMessage(
            text=text, file_ids=file_ids, varnames=varnames, timestamp=timestamp
        )
        mappings.update(zip(varnames, objects))

        cycles = conv.chat_cycles[:-MAX_CYCLES]
        curr_cycle = fullfill(cycles, mappings, request, llm, provider)
        conv.chat_cycles.append(curr_cycle)
        
        conv.context.variables = []
        for name, value in mappings:
            conv.context.variables.append(await save_variable(name, value, file_service, user.id))
            
        response = curr_cycle.response
        if response:
            return ChatResponse(status="success", text=response.text, file_ids=response.file_ids)
        
        return ChatResponse(status="error", text="", file_ids=[])

    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500)
