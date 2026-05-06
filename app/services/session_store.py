from collections import defaultdict
from app.schemas.mcp import McpMessage

# In-memory store — lives as long as the server is running
# Phase 2: replace with Redis for persistence across restarts
_store: dict[str, list[McpMessage]] = defaultdict(list)

def get_history(session_id: str) -> list[McpMessage]:
    return _store[session_id]

def append(session_id: str, role: str, content: str) -> None:
    _store[session_id].append(McpMessage(role= role, content= content))

def clear(session_id: str) -> None:
    _store.pop(session_id,None)