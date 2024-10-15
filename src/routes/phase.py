import io
import traceback
import zipfile
from typing import List
from uuid import uuid4

from beanie import PydanticObjectId, WriteRules
from fastapi import APIRouter
from fastapi import File as FormFile
from fastapi import Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from core.controller.generate import generate
from core.providers.provider import Provider
from deps.llms import get_llm
from deps.providers import get_provider
from lib.fs import get_bucket
from models.chat import Chat, ChatState
from models.phase import Message
from schemas.file import File
from schemas.language import Language
from schemas.provider import Provider as ProviderType

router = APIRouter(prefix="/phases")

MAX_CHAT_PHASES = 10
MAX_PROMPT_PHASES = 4
LLM = "gemini-1.5-flash"


@router.post("")
async def prompt(
    chat_id: PydanticObjectId = Query(...),
    text: str = Form(...),
    provider: ProviderType = Form(...),
    language: Language = Form(...),
    upload_files: List[UploadFile] = FormFile(default=[], alias="files"),
):
    try:
        files = await convert_upload_files_to_files(upload_files)

        chat = await Chat.get(chat_id, fetch_links=True)
        if not chat:
            raise HTTPException(404)

        bucket = get_bucket("contexts")
        context_id = chat.state.context_id
        context_stream = bucket.open_download_stream(context_id)
        context_buffer = context_stream.read()

        provider = get_provider(provider)
        provider.set_language(language)
        provider.load_context_from_buffer(context_buffer)

        varnames = assign_files(files, chat.state, provider)
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

        chat.phases.append(new_phase)
        context_buffer = provider.save_context_to_buffer()
        chat.state.context_id = bucket.upload_from_stream(
            f"{uuid4()}.json", context_buffer
        )
        await chat.save(link_rule=WriteRules.WRITE)

        if not new_phase.response:
            raise HTTPException(500)

        text = new_phase.response.text
        varnames = new_phase.response.varnames or []
        files = create_files(varnames, provider)

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


async def convert_upload_files_to_files(upload_files: List[UploadFile]) -> List[File]:
    return [
        File(
            buffer=await upload_file.read(),
            name=upload_file.filename,
            content_type=upload_file.content_type,
        )
        for upload_file in upload_files
    ]


def assign_files(files: List[File], state: ChatState, provider: Provider) -> List[str]:
    context = provider.get_context()
    varnames = []

    for file in files:
        parts = file.name.split(".")
        file_id = parts[0]
        file.name = parts[1:]
        file_varnames = []

        if file_id in state.id_to_varnames:
            file_varnames = state.id_to_varnames[file_id]
            varnames.extend(file_varnames)

        else:
            for obj in provider.convert_file_to_objects(file):
                alias = provider.get_obj_alias(obj)
                idx = state.alias_to_count.get(alias, 0)
                state.alias_to_count[alias] = idx + 1
                obj_varname = f"{alias}{idx}"
                context[obj_varname] = obj
                file_varnames.append(obj_varname)

        varnames.extend(file_varnames)
        state.id_to_varnames[file_id] = file_varnames

    return varnames


def create_files(varnames: List[str], provider: Provider) -> List[File]:
    context = provider.get_context()
    objects = [context[varname] for varname in varnames]
    return [provider.convert_object_to_file(obj) for obj in objects]
