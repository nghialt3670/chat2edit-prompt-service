import traceback
from base64 import b64encode
from typing import Dict, List, Literal, Optional

import PIL
import PIL.Image
from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from gridfs import GridFS
from pydantic import BaseModel
from pymongo.database import Database

from core.controller import fullfill
from core.llms import LLM
from core.providers import Provider
from core.schemas.fabric import FabricCanvas, FabricObject
from core.schemas.fabric.fabric_image import FabricImage
from db.models import ChatMessage, Conversation
from db.services import CanvasService, ContextService, ConvService
from deps.database import (get_canvas_service, get_context_service,
                           get_conv_service, get_db)
from deps.llms import get_llm
from deps.providers import get_providers

router = APIRouter(prefix="/api/v1")


class ChatRequest(BaseModel):
    conversation_id: str
    text: str
    file_ids: List[str]
    bucket_name: str


class ChatResponse(BaseModel):
    text: str
    file_ids: List[str]


MAX_CYCLES = 6
NAME_TO_CLASS = {"FabricCanvas": FabricCanvas}
TYPE_TO_ALIAS = {FabricCanvas: "image"}
CONTEXT_ALLOWED_TYPES = (str, int, float, bool, list, dict, FabricCanvas, FabricObject)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Database = Depends(get_db),
    llm: LLM = Depends(get_llm),
    providers: Dict[str, Provider] = Depends(get_providers),
    conv_service: ConvService = Depends(get_conv_service),
    canvas_service: CanvasService = Depends(get_canvas_service),
    context_service: ContextService = Depends(get_context_service),
):
    conv_id = request.conversation_id
    text = request.text
    file_ids = request.file_ids
    bucket_name = request.bucket_name
    try:
        conv = conv_service.find_by_id(ObjectId(conv_id))
        context = {}

        if conv:
            context = context_service.load(conv.context_id)
        else:
            context_id = context_service.save(context)
            conv = Conversation(_id=ObjectId(conv_id), context_id=ObjectId(context_id))

        objects = []
        varnames = []
        selected_provider = providers["fabric"]
        gridfs = GridFS(db, bucket_name)
        for file_id in file_ids:
            file_obj = gridfs.get(ObjectId(file_id))
            filename = file_obj.filename
            file_type = file_obj.content_type
            file_bytes = file_obj.read()
            if file_type.startswith("image/") or filename.endswith(".canvas"):
                canvas = None
                if file_type.startswith("image/"):
                    base64 = b64encode(file_bytes).decode()
                    data_url = f"data:{file_type};base64,{base64}"
                    bg_img = FabricImage(src=data_url, filename=filename)
                    canvas = FabricCanvas(backgroundImage=bg_img)
                else:
                    canvas = FabricCanvas.model_validate_json(file_bytes)

                alias = TYPE_TO_ALIAS[FabricCanvas]
                idx = conv.alias_to_count.get(alias, 0)
                conv.alias_to_count[alias] = idx + 1
                varname = f"{alias}{idx}"
                varnames.append(varname)
                objects.append(canvas)
                context[varname] = canvas
                selected_provider = providers["fabric"]
            else:
                raise NotImplementedError()

        cycles = [cycle for cycle in conv.chat_cycles if cycle.response][-MAX_CYCLES:]
        context.update(**{f.__name__: f for f in selected_provider.get_functions()})
        request = ChatMessage(text=text, varnames=varnames)

        # Full fill the current cycle and save the conversation
        curr_cycle = await fullfill(cycles, context, request, llm, selected_provider)
        conv.chat_cycles.append(curr_cycle)
        conv_service.save(conv)

        # Filter out unsupport types
        keys_to_remove = [
            k for k, v in context.items() if not isinstance(v, CONTEXT_ALLOWED_TYPES)
        ]
        for key in keys_to_remove:
            del context[key]

        context_service.update(conv.context_id, context)

        response = curr_cycle.response
        if not response:
            raise HTTPException(500)

        # Save the response files and get the ids
        res_file_ids = []
        for varname in response.varnames:
            obj = context[varname]
            if isinstance(obj, FabricCanvas):
                file_id = canvas_service.save(obj)
                res_file_ids.append(str(file_id))
            else:
                raise NotImplementedError()

        return ChatResponse(text=response.text, file_ids=res_file_ids)

    except Exception:
        print(traceback.format_exc())
        raise HTTPException(500)
