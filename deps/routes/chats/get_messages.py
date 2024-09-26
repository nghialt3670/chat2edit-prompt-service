import traceback
from typing import List

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import TypeAdapter

from deps.db import get_chat_service, get_message_service
from schemas.attachment_schema import Attachment
from schemas.message_schema import ChatMessage
from schemas.object_id_schema import ObjectIdSchema
from services.chat_service import ChatService
from services.message_service import MessageService
from utils.env import ENV

router = APIRouter()


@router.get("/messages", response_model=List[ChatMessage])
async def get_messages(
    chat_id: str = Query(...),
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

        endpoint = f"{ENV.ATTACHMENT_SERVICE_API_BASE_URL}/attachments?ids={",".join(attachment_ids)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint) as response:
                response.raise_for_status()
                payload = await response.json()
                attachments = TypeAdapter(List[Attachment]).validate_python(payload)

        id_to_att = {att.id: att for att in attachments}

        return [
            ChatMessage(
                text=msg.text, attachments=[id_to_att[id] for id in msg.attachment_ids]
            )
            for msg in messages
        ]

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(500, str(e))
