from pydantic import BaseModel, Field
from typing import List, Optional


class Message(BaseModel):
    role: str          # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., min_length=1)


class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str     # e.g. "K" (Knowledge), "P" (Personality), "S" (Simulation), etc.


class ChatResponse(BaseModel):
    reply: str
    recommendations: List[Recommendation] = Field(default_factory=list)
    end_of_conversation: bool = False