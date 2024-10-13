import json
import traceback
from uuid import uuid4

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Response

from models.chat import Chat, ChatState
from schemas.chat_create_request import ChatCreateRequest
from src.lib.fs import get_bucket

router = APIRouter(prefix="/chats")


@router.post("")
async def create_chat(request: ChatCreateRequest):
    try:
        bucket = get_bucket("contexts")
        context_buffer = json.dumps({}).encode()
        context_id = bucket.upload_from_stream(f"{uuid4()}.json", context_buffer)
        state = ChatState(context_id=context_id)
        
        chat = Chat(id=PydanticObjectId(request.chat_id), state=state)
        await chat.save()

        return Response(status_code=201)

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(500, str(e))
