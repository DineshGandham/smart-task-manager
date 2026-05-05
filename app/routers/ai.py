from fastapi import APIRouter, Depends
from app.schemas.mcp import MCPChatRequest, MCPChatResponse
from app.services.mcp_service import MCPService
from app.core.dependencies import get_mcp_service

router = APIRouter(prefix="/ai", tags=["AI / MCP"])


@router.post("/chat", response_model=MCPChatResponse)
def chat(
        payload: MCPChatRequest,
        service: MCPService = Depends(get_mcp_service)
):
    """
    Natural language interface to your tasks and notes.

    Send a message like:
    - "Create a task called Learn MCP, high priority, due 2026-06-01"
    - "Show all my todo tasks"
    - "Mark task {id} as done"
    - "Summarize my notes tagged python"
    """

    return service.chat(payload)