import traceback
import zipfile
from base64 import b64encode
from io import BytesIO
from typing import Any, Dict, List, Tuple

from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, UploadFile
from fastapi.responses import StreamingResponse

from core.controller import fullfill
from core.llms import LLM
from core.providers import Provider
from core.schemas.fabric import FabricCanvas, FabricObject
from core.schemas.fabric.fabric_image import FabricImage
from core.schemas.fabric.fabric_rect import FabricRect
from core.types.language import Language
from core.types.provider import Provider as ProviderType
from core.utils.convert import src_to_image
from db.models import ChatMessage
from db.models.chat import Chat
from db.services import ChatService, ContextService
from db.services.chat_service import ChatService
from deps.database import get_chat_service, get_context_service
from deps.llms import get_llm
from deps.providers import get_providers

router = APIRouter(prefix="/api/v2")


MAX_CYCLES = 6
TYPE_TO_ALIAS = {FabricCanvas: "image", tuple: "box"}
MAIN_TYPES = {FabricCanvas}
CONTEXT_ALLOWED_TYPES = (str, int, float, bool, list, dict, tuple, FabricCanvas, FabricObject)


@router.post("/chat/{chat_id}")
async def chat(
    chat_id: str = Path(...),
    text: str = Form(...),
    files: List[UploadFile] = File(None),
    file_ids: List[str] = Form(None),
    language: Language = Form(...),
    provider: ProviderType = Form(...),
    llm: LLM = Depends(get_llm),
    providers: Dict[str, Provider] = Depends(get_providers),
    chat_service: ChatService = Depends(get_chat_service),
    context_service: ContextService = Depends(get_context_service),
):
    try:
        provider = providers[provider]
        provider.set_language(language)
        chat = chat_service.load(chat_id)
        file_ids = file_ids or []
        files = files or []
        context = {}

        if chat:
            context = context_service.load(chat.context_id)
        else:
            context_id = context_service.save(context)
            chat = Chat(_id=ObjectId(chat_id), context_id=context_id)

        # Conver each file to object and asign a variable name in the context
        varnames = []
        for file_id in file_ids:
            if file_id in chat.id_to_varname:
                varname = chat.id_to_varname[file_id]
                varnames.append(varname)
            else:
                file = files.pop(0)
                objects = await file_to_objects(file)
                for obj in objects:
                    alias = TYPE_TO_ALIAS[type(obj)]
                    idx = chat.alias_to_count.get(alias, 0)
                    chat.alias_to_count[alias] = idx + 1
                    varname = f"{alias}{idx}"
                    varnames.append(varname)
                    context[varname] = obj
                    if type(obj) in MAIN_TYPES:
                        chat.id_to_varname[file_id] = varname

        # Prepare cycles, context and request for fullfill
        cycles = [cycle for cycle in chat.chat_cycles if cycle.response][-MAX_CYCLES:]
        context.update(**{f.__name__: f for f in provider.get_functions()})
        request = ChatMessage(text=text, varnames=varnames)
        
        # Start fullfill and save the chat after having the result
        curr_cycle = await fullfill(cycles, context, request, llm, provider)
        chat.chat_cycles.append(curr_cycle)
        chat_service.save(chat)

        # Filter out unsupport types before serializing and saving the context
        keys_to_remove = [
            k for k, v in context.items() if not isinstance(v, CONTEXT_ALLOWED_TYPES)
        ]
        for key in keys_to_remove:
            del context[key]
        context_service.update(chat.context_id, context)

        # Response return phase
        response = curr_cycle.response
        if not response:
            raise HTTPException(500)

        # Convert objects back to files and zip them
        zip_io = BytesIO()
        with zipfile.ZipFile(
            zip_io, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zip_file:
            zip_file.writestr("message.txt", response.text)

            for varname in response.varnames:
                obj = context[varname]
                if isinstance(obj, FabricCanvas):
                    file_bytes = obj.model_dump_json().encode()
                    filename = obj.backgroundImage.filename + ".canvas"
                    content_type = "application/json"
                    if not obj.backgroundImage.is_size_initialized():
                        await obj.backgroundImage.init_size()
                    width = obj.backgroundImage.width
                    height = obj.backgroundImage.height
                    metadata = (
                        f"contentType={content_type};width={width};height={height}"
                    )
                    file_info = zipfile.ZipInfo(filename)
                    file_info.external_attr = 0o644 << 16  # Permissions - rw-r--r--
                    file_info.comment = metadata.encode()
                    zip_file.writestr(file_info, file_bytes)
                elif isinstance(obj, FabricImage):
                    pil_image = await src_to_image(obj.src)
                    buffer = BytesIO()
                    pil_image.save(buffer, format="PNG")
                    file_bytes = buffer.getvalue()
                    metadata = f"contentType=image/png;width={pil_image.width};height={pil_image.height}"
                    file_info = zipfile.ZipInfo(obj.filename)
                    file_info.external_attr = 0o644 << 16  # Permissions - rw-r--r--
                    file_info.comment = metadata.encode()
                    zip_file.writestr(file_info, file_bytes)
                else:
                    raise NotImplementedError()

        zip_io.seek(0)

        return StreamingResponse(
            zip_io,
            media_type="application/x-zip-compressed",
            headers={
                "Content-Disposition": "attachment;filename=files_with_message.zip"
            },
        )

    except Exception:
        print(traceback.format_exc())
        raise HTTPException(500)


async def file_to_objects(file: UploadFile) -> List[Any]:
    file_bytes = await file.read()
    filename = file.filename
    content_type = file.content_type
    objects = []

    if content_type.startswith("image/"):
        base64 = b64encode(file_bytes).decode()
        data_url = f"data:{content_type};base64,{base64}"
        bg_img = FabricImage(src=data_url, filename=filename)
        canvas = FabricCanvas(backgroundImage=bg_img)
        objects.append(canvas)
    elif filename and filename.endswith(".canvas"):
        canvas = FabricCanvas.model_validate_json(file_bytes)
        prompt_objects = []
        for obj in canvas.objects:
            if isinstance(obj, FabricRect) and obj.is_prompt:
                objects.append(obj.get_box())
                prompt_objects.append(obj)
        for obj in prompt_objects:
            canvas.objects.remove(obj)
        objects.append(canvas)
    else:
        raise NotImplementedError("Unsupported file type")

    return objects
