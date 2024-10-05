from typing import List, Literal, Optional

from beanie import Document
from bson import ObjectId
from pydantic import BaseModel, Field


class Message(BaseModel):
    src: Literal["user", "system", "llm"] = Field(...)
    type: Literal["request", "response", "info", "warning", "error"] = Field(...)
    text: str = Field(...)
    varnames: List[str] = Field(default_factory=list)


class Execution(BaseModel):
    commands: List[str] = Field(default_factory=list)
    durations: Optional[List[float]] = Field(default_factory=list)
    traceback: Optional[str] = Field(default=None)
    feedback: Optional[Message] = Field(default=None)
    response: Optional[Message] = Field(default=None)


class PromptPhase(BaseModel):
    responses: Optional[List[str]] = Field(default_factory=list)
    durations: Optional[List[float]] = Field(default_factory=list)
    tracebacks: Optional[List[str]] = Field(default_factory=list)
    execution: Optional[Execution] = Field(default=None)


class ChatPhase(Document):
    request: Message = Field(...)
    prompt_phases: List[PromptPhase] = Field(default_factory=list)
    response: Optional[Message] = Field(default=None)
    
    class Settings:
        name = "chat-phases"
