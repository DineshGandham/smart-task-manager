from typing import Any, Optional
from pydantic import BaseModel

class McpMessage(BaseModel):
    role: str
    content: str

class MCPChatRequest(BaseModel):
    message: str
    history : list[McpMessage] = []

class MCPChatResponse(BaseModel):
    reply: str
    tools_called: list[str] = []

