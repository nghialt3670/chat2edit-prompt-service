import json
import traceback
from typing import List, Literal, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from core.controller.fullfill import fullfill
from core.llms.llm import LLM
from core.providers.fabric_provider import FabricProvider
from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.schemas.fabric.fabric_object import FabricObject
from database.models import ChatMessage, Conversation
from database.services import ConvService
from database.services.canvas_service import CanvasService
from database.services.context_service import ContextService
from database.services.user_service import UserService
from dependencies.authorization import clerk_validate_user
from dependencies.database import (get_canvas_service, get_context_service,
                                   get_conv_service, get_user_service)
from dependencies.llms import get_llm

router = APIRouter(prefix="/api/v1")
provider = FabricProvider(
    ["response_user", "detect", "remove", "filter", "rotate", "flip", "scale"]
)


class ChatResponse(BaseModel):
    status: Literal["success", "error"]
    text: str = Field(default="")
    file_ids: List[str] = Field(default_factory=list)


MAX_CYCLES = 4
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
            conv = Conversation(user_id=user.id, context_id=context_id)

        objects = []
        varnames = []
        req_file_ids = []
        for file in files:
            if file.filename.endswith(".canvas"):
                file_bytes = await file.read()
                canvas = FabricCanvas.parse_raw(file_bytes)
                req_file_ids.append(str(canvas_service.save(canvas)))
                alias = TYPE_TO_ALIAS[FabricCanvas]
                idx = conv.alias_to_count.get(alias, 0)
                conv.alias_to_count[alias] = idx + 1
                varname = f"{alias}{idx}"
                varnames.append(varname)
                objects.append(canvas)
                context[varname] = canvas
            else:
                raise NotImplementedError()

        cycles = conv.chat_cycles[:-MAX_CYCLES]
        context.update(**{f.__name__: f for f in provider.get_functions()})
        request = ChatMessage(
            text=text, file_ids=req_file_ids, varnames=varnames, timestamp=timestamp
        )

        curr_cycle = await fullfill(cycles, context, request, llm, provider)

        conv.title = curr_cycle.response.text
        conv.chat_cycles.append(curr_cycle)
        conv_service.save(conv)

        # Filter out unsupport types
        keys_to_remove = [
            k for k, v in context.items() if not isinstance(v, CONTEXT_ALLOWED_TYPES)
        ]
        for key in keys_to_remove:
            del context[key]

        context_service.update(context_id, context)

        response = curr_cycle.response
        if not response:
            return ChatResponse(status="error")

        res_file_ids = []
        for varname in response.varnames:
            obj = context[varname]
            if isinstance(obj, FabricCanvas):
                res_file_ids.append(await canvas_service.save(obj))
            else:
                raise NotImplementedError()

        return ChatResponse(status="success", text=response.text, file_ids=res_file_ids)

    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500)
