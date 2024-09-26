import traceback
from typing import List, Optional

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import TypeAdapter

from core.controller.generate import generate
from deps.db import (
    get_account_service,
    get_chat_service,
    get_context_service,
    get_message_service,
    get_phase_service,
)
from deps.llms import get_llm
from deps.providers import get_provider
from models.db.context_message import ContextMessage
from models.db.message import Message
from schemas.attachment_schema import AttachmentSchema
from schemas.message_schema import MessageSchema
from schemas.chat_schema import ChatSchema
from services.account_service import AccountService
from services.chat_service import ChatService
from services.context_service import ContextService
from services.message_service import MessageService
from services.phase_service import PhaseService
from utils.env import ENV

router = APIRouter(prefix="/chats")


@router.get("", response_model=List[ChatSchema])
def get_chats(
    account_id: str = Query(...),
    account_service: AccountService = Depends(get_account_service),
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        account = account_service.find_by_id(
            account_id
        ) or account_service.create_with_id(account_id)

        chats = chat_service.find_many_by_account_id(account.id)
        return [
            ChatSchema(id=chat.id, title=chat.title, updated_at=chat.updated_at)
            for chat in chats
        ]

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(500, str(e))


@router.get("/messages", response_model=List[MessageSchema])
async def get_messages(
    chat_id: str = Path(...),
    account_id: str = Query(...),
    chat_service: ChatService = Depends(get_chat_service),
    message_service: MessageService = Depends(get_message_service),
):
    try:
        chat = chat_service.find_by_id_and_account_id(chat_id, account_id)

        if not chat:
            raise HTTPException(400, "Chat not found")

        messages = message_service.find_by_chat(chat)
        attachment_ids = [id for msg in messages for id in msg.attachment_ids]

        endpoint = f"{ENV.ATTACHMENT_SERVICE_API_BASE_URL}/attachments?ids={','.join(attachment_ids)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint) as response:
                response.raise_for_status()
                payload = await response.json()
                attachments = TypeAdapter(List[AttachmentSchema]).validate_python(
                    payload
                )

        id_to_att = {att.id: att for att in attachments}

        return [
            MessageSchema(
                text=msg.text,
                attachments=[id_to_att[att_id] for att_id in msg.attachment_ids],
            )
            for msg in messages
        ]

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(500, str(e))


@router.post("/messages", response_model=MessageSchema)
async def send_message(
    request: MessageSchema,
    chat_id: str = Query(None),
    account_id: str = Query(...),
    chat_service: ChatService = Depends(get_chat_service),
    phase_service: PhaseService = Depends(get_phase_service),
    context_service: ContextService = Depends(get_context_service),
    account_service: AccountService = Depends(get_account_service),
    message_service: MessageService = Depends(get_message_service),
):
    try:
        chat = None
        context = None
        account = account_service.find_by_id(
            account_id
        ) or account_service.create_with_id(account_id)

        if chat_id:
            chat = chat_service.find_by_id_and_account_id(chat_id, account.id)
            if not chat:
                raise HTTPException(404, "Chat not found")
            context = context_service.load(chat.context_id)
        else:
            context = context_service.create()
            chat = chat_service.create(account, context)

        req_message = Message(
            chat_id=chat.id,
            text=request.text,
            attachment_ids=[att.id for att in request.attachments],
        )

        provider = get_provider(chat.settings.provider)
        provider.set_language(chat.settings.language)
        context = context_service.load(chat.context_id)
        provider.set_context(context)

        req_varnames = await provider.assign_attachments(request.attachments)
        request = ContextMessage(
            src="user",
            type="request",
            text=request.text,
            varnames=req_varnames,
        )

        new_phase = await generate(
            request=request,
            phases=phase_service.find_by_chat(chat),
            llm=get_llm(chat.settings.llm),
            provider=provider,
            max_prompt_phases=chat.settings.max_prompt_phases,
        )

        phase_service.insert(new_phase)
        context_service.save(provider.get_context())

        if not new_phase.response:
            raise HTTPException(500, "No response")

        res_varnames = new_phase.response.varnames or []
        res_attachments = await provider.create_attachments(res_varnames)
        res_message = Message(
            chat_id=chat.id,
            text=new_phase.response.text,
            attachment_ids=[att.id for att in res_attachments],
        )

        message_service.insert(req_message)
        message_service.insert(res_message)

        return MessageSchema(
            chat_id=chat.id, text=new_phase.response.text, attachments=res_attachments
        )

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(500, str(e))
