import json
import traceback
from typing import List, Literal, Optional

from bson import ObjectId
from core.controller.fullfill import fullfill
from core.llms.llm import LLM
from core.providers.fabric_provider import FabricProvider
from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.schemas.fabric.fabric_object import FabricObject
from database.models import ChatMessage, Conversationersation
from database.services import ConvService
from database.services.canvas_service import CanvasService
from database.services.context_service import ContextService
from database.services.user_service import UserService
from dependencies.authorization import clerk_validate_user
from dependencies.database import (get_canvas_service, get_context_service,
                                   get_conv_service, get_user_service)
from dependencies.llms import get_llm
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1")
provider = FabricProvider(
    [
        "response_user",
        "detect",
        "remove",
        "filter",
        "rotate",
        "flip",
        "scale",
        "move",
        "shift",
    ]
)

class UpdateResponse(BaseModel):
    convId: str
    fileIds: List[str]


class MessageResponse(BaseModel):
    text: str
    fileIds: List[str]
    timestamp: int


class ChatResponse(BaseModel):
    status: Literal["success", "error"]
    update: UpdateResponse
    message: Optional[MessageResponse] = None


MAX_CYCLES = 6
NAME_TO_CLASS = {"FabricCanvas": FabricCanvas}
TYPE_TO_ALIAS = {FabricCanvas: "image"}
CONTEXT_ALLOWED_TYPES = (str, int, float, bool, list, dict, FabricCanvas, FabricObject)


@router.post("/chat/{conv_id}", response_model=ChatResponse)
async def chat(
    conv_id: str,
    text: str = Form(...),
    timestamp: int = Form(...),
    files: List[UploadFile] = File(None),
    llm: LLM = Depends(get_llm),
    clerk_user_id: str = Depends(clerk_validate_user),
    user_service: UserService = Depends(get_user_service),
    conv_service: ConvService = Depends(get_conv_service),
    canvas_service: CanvasService = Depends(get_canvas_service),
    context_service: ContextService = Depends(get_context_service),
):
    if not files:
        files = []
    try:
        user = user_service.find_by_clerk_user_id(clerk_user_id)
        conv = conv_service.find_by_id_and_user_id(conv_id, user.id)
        context = {}

        if conv:
            context = context_service.load(conv.context_id)
        else:
            context_id = context_service.save({})
            conv = Conversationersation(user_id=user.id, context_id=context_id)

        objects = []
        varnames = []
        req_file_ids = []
        for file in files:
            if file.filename.endswith(".canvas"):
                file_bytes = await file.read()
                canvas = FabricCanvas.model_validate_json(file_bytes)
                req_file_ids.append(str(canvas_service.save(canvas, user.id)))
                alias = TYPE_TO_ALIAS[FabricCanvas]
                idx = conv.alias_to_count.get(alias, 0)
                conv.alias_to_count[alias] = idx + 1
                varname = f"{alias}{idx}"
                varnames.append(varname)
                objects.append(canvas)
                context[varname] = canvas
            else:
                raise NotImplementedError()
            
        update = UpdateResponse(convId=str(conv.id), fileIds=[str(id) for id in req_file_ids])

        cycles = [cycle for cycle in conv.chat_cycles if cycle.response][-MAX_CYCLES:]
        context.update(**{f.__name__: f for f in provider.get_functions()})
        request = ChatMessage(
            text=text, file_ids=req_file_ids, varnames=varnames, timestamp=timestamp
        )

        curr_cycle = await fullfill(cycles, context, request, llm, provider)
        conv.chat_cycles.append(curr_cycle)

        # Filter out unsupport types
        keys_to_remove = [
            k for k, v in context.items() if not isinstance(v, CONTEXT_ALLOWED_TYPES)
        ]
        for key in keys_to_remove:
            del context[key]

        context_service.update(conv.context_id, context)

        response = curr_cycle.response

        if not response:
            conv.title = "ERROR"
            conv_service.save(conv)
            return ChatResponse(status="error", update=update)

        for varname in response.varnames:
            obj = context[varname]
            if isinstance(obj, FabricCanvas):
                response.file_ids.append(str(canvas_service.save(obj, user.id)))
            else:
                raise NotImplementedError()

        conv.title = response.text
        conv_service.save(conv)
        
        
        return ChatResponse(
            status="success",
            update=update,
            message=MessageResponse(
                text=curr_cycle.response.text,
                fileIds=[str(id) for id in curr_cycle.response.file_ids],
                timestamp=curr_cycle.response.timestamp
            )
        )

    except Exception:
        print(traceback.format_exc())
        raise HTTPException(500)
