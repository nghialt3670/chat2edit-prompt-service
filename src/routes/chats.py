import json
import traceback
from uuid import uuid4

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Query, Response

from models.chat import Chat, Context
from src.lib.fs import get_bucket

router = APIRouter(prefix="/chats")


@router.post("")
async def create_chat(chat_id: str = Query(...)):
    try:
        buffer = json.dumps({}).encode()
        bucket = get_bucket("contexts")
        file_id = bucket.upload_from_stream(f"{uuid4()}.json", buffer)
        context = Context(file_id=file_id)

        chat = Chat(id=PydanticObjectId(chat_id), context=context)
        await chat.save()

        return Response(status_code=204)

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(500, str(e))
