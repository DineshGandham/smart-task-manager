from typing import Any, Optional
from pydantic import BaseModel, Field

class McpMessage(BaseModel):
    role: str
    content: str

class MCPChatRequest(BaseModel):
    message: str = Field(...,min_length=1, max_length=500)
    session_id: str = Field("default", max_length=100)
    history : list[McpMessage] = Field(default_factory=list, max_length=20)

class MCPChatResponse(BaseModel):
    reply: str
    tools_called: list[str] = []

