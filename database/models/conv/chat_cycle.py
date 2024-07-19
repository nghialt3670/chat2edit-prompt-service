from typing import List

from pydantic import BaseModel

from database.models.conv.prompt_cycle import PromptCycle
from database.models.conv.req_message import RequestMessage
from database.models.conv.res_message import ResponseMessage


class ChatCycle(BaseModel):
    req_message: RequestMessage
    prompt_cycles: List[PromptCycle]
    res_message: ResponseMessage
