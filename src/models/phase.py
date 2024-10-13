from typing import List, Literal, Optional

from beanie import Document
from pydantic import BaseModel, Field


class Message(BaseModel):
    src: Literal["user", "system", "llm"] = Field(...)
    type: Literal["request", "response", "info", "warning", "error"] = Field(...)
    text: str = Field(...)
    varnames: List[str] = Field(default_factory=list)


class Execution(BaseModel):
    commands: List[str] = Field(default_factory=list)
    durations: List[float] = Field(default_factory=list)
    traceback: Optional[str] = Field(default=None)
    feedback: Optional[Message] = Field(default=None)
    response: Optional[Message] = Field(default=None)


class PromptPhase(BaseModel):
    prompts: List[str] = Field(default_factory=list)
    answers: List[str] = Field(default_factory=list)
    durations: List[float] = Field(default_factory=list)
    tracebacks: List[str] = Field(default_factory=list)
    execution: Optional[Execution] = Field(default=None)


class ChatPhase(Document):
    request: Message = Field(...)
    prompt_phases: List[PromptPhase] = Field(default_factory=list)
    response: Optional[Message] = Field(default=None)

    class Settings:
        name = "chat-phases"
