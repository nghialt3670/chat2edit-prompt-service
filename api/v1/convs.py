import traceback
from typing import List

from database.services import ConvService
from database.services.user_service import UserService
from dependencies.authorization import clerk_validate_user
from dependencies.database import get_conv_service, get_user_service
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")


class MessageResponse(BaseModel):
    text: str
    fileIds: List[str]
    timestamp: int


class ConversationResponse(BaseModel):
    messages: List[MessageResponse]


@router.get("/convs/{conv_id}", response_model=ConversationResponse)
async def get_conversation(
    conv_id: str,
    clerk_user_id: str = Depends(clerk_validate_user),
    user_service: UserService = Depends(get_user_service),
    conv_service: ConvService = Depends(get_conv_service),
):
    try:
        user = user_service.find_by_clerk_user_id(clerk_user_id)
        conv = conv_service.find_by_id_and_user_id(conv_id, user.id)

        if not conv:
            raise HTTPException(404)

        messages = [
            MessageResponse(text=m.text, fileIds=m.file_ids, timestamp=m.timestamp)
            for c in conv.chat_cycles
            for m in (c.request, c.response)
            if c.response
        ]
        return ConversationResponse(messages=messages)

    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500)
