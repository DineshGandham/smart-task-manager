from fastapi import APIRouter, Depends
from app.schemas.mcp import MCPChatRequest, MCPChatResponse
from app.services.mcp_service import MCPService
from app.core.dependencies import get_mcp_service
from app.services import session_store

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

@router.delete("/session/{session_id}", status_code=204)
def clear_session(session_id: str):
    """Clear conversation history for a session. User wants to start fresh."""
    session_store.clear(session_id)

@router.get("/session/{session_id}/history")
def get_session_history(session_id: str):
    """Get full conversation history for a session — useful for debugging."""
    history = session_store.get_history(session_id)
    return {"session_id": session_id, "message_count": len(history), "history": history}