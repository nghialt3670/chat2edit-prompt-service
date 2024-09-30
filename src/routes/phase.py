import io
import traceback
import zipfile
from typing import List, Optional
from uuid import uuid4

from beanie import PydanticObjectId, WriteRules
from fastapi import APIRouter, File as FormFile, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from core.controller.generate import generate
from schemas.provider import Provider
from deps.llms import get_llm
from deps.providers import get_provider
from models.chat import Chat
from models.phase import Message
from schemas.language import Language
from schemas.file import File
from lib.fs import get_bucket

router = APIRouter(prefix="/phases")

MAX_CHAT_PHASES = 10
MAX_PROMPT_PHASES = 3
LLM = "gemini-1.5-flash"


@router.post("")
async def prompt(
    chat_id: PydanticObjectId = Query(...),
    text: str = Form(...),
    provider: Provider = Form(...),
    language: Language = Form(...),
    files: List[UploadFile] = FormFile(None),
):
    try:
        files = files or []
        files = [File(buffer=await file.read(), name=file.filename, content_type=file.content_type) for file in files]
        
        chat = await Chat.get(chat_id, fetch_links=True)
        if not chat:
            raise HTTPException(404)

        context = chat.context
        context_file_id = context.file_id
        bucket = get_bucket("contexts")
        context_stream = bucket.open_download_stream(context_file_id)
        context_buffer = context_stream.read()

        provider = get_provider(provider)
        provider.set_language(language)
        provider.set_context(chat.context)
        provider.set_context_buffer(context_buffer)

        varnames = provider.assign_files(files)
        request = Message(
            src="user",
            type="request",
            text=text,
            varnames=varnames,
        )

        llm = get_llm(LLM)
        phases = [p for p in chat.phases if p.response][-MAX_CHAT_PHASES:]

        new_phase = await generate(
            request=request,
            phases=phases,
            llm=llm,
            provider=provider,
            max_prompt_phases=MAX_PROMPT_PHASES,
        )

        context = provider.get_context()
        context_buffer = provider.get_context_buffer()
        context.file_id = bucket.upload_from_stream(f"{uuid4()}.json", context_buffer)

        chat.context = context
        chat.phases.append(new_phase)
        await chat.save(link_rule=WriteRules.WRITE)

        if not new_phase.response:
            raise HTTPException(500, "No response")

        text = new_phase.response.text
        varnames = new_phase.response.varnames or []
        files = provider.create_files(varnames)

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("text.txt", text)
            for file in files:
                zip_file.writestr(file.name, file.buffer)

        zip_buffer.seek(0)

        response = StreamingResponse(
            zip_buffer, media_type="application/x-zip-compressed"
        )
        response.headers["Content-Disposition"] = "attachment; filename=files.zip"
        return response

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(500, str(e))
