import traceback
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from core.llms.llm import LLM
from database.models import ChatCycle, Conv, RequestMessage, ResponseMessage
from database.services import ConvService
from database.services.file_service import FileService
from database.services.user_service import UserService
from dependencies.authorization import clerk_validate_user
from dependencies.database import (get_conv_service, get_file_service,
                                   get_user_service)
from dependencies.llm import get_llm

router = APIRouter(prefix="/api/v1")


class ChatResponse(BaseModel):
    status: Literal["success", "error"]
    text: str
    file_ids: List[str]


@router.post("/chat/{conv_id}", response_model=ChatResponse)
async def chat(
    conv_id: str,
    text: str = Form(...),
    files: Optional[List[UploadFile]] = File([]),
    llm: LLM = Depends(get_llm),
    clerk_user_id: str = Depends(clerk_validate_user),
    user_service: UserService = Depends(get_user_service),
    conv_service: ConvService = Depends(get_conv_service),
    file_service: FileService = Depends(get_file_service),
):
    try:
        user = user_service.find_by_clerk_user_id(clerk_user_id)
        conv = conv_service.find_by_id_and_user_id(conv_id, user.id)

        if not conv:
            conv = Conv(user_id=user.id)

        file_ids = [file_service.save_upload_file(file) for file in files]

        req_message = RequestMessage(text=text, file_ids=file_ids)
        answer = await llm([text])
        res_mesaage = ResponseMessage(status="sucess", text=answer, file_ids=file_ids)
        chat_cycle = ChatCycle(
            req_message=req_message, res_message=res_mesaage, prompt_cycles=[]
        )
        conv.chat_cycles.append(chat_cycle)
        conv.title = answer
        conv_service.save(conv)

        return ChatResponse(status="success", text=answer, file_ids=file_ids)

    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500)
