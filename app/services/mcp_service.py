import re
import time
from google import genai
from google.genai import types
from google.genai.errors import ClientError

from app.core.config import get_settings
from app.core.exceptions import AIProviderError
from app.schemas.mcp import MCPChatRequest, MCPChatResponse
from app.services.task_service import TaskService
from app.services.note_service import NoteService
from app.services import session_store


class MCPService:

    def __init__(self, task_service: TaskService, note_service: NoteService):
        self._tasks = task_service
        self._notes = note_service

        settings = get_settings()

        # New SDK uses Client() instead of genai.configure()
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model  = "gemini-3-flash-preview"
        self._tools  = self._build_tools()

    # ── Tool definitions ───────────────────────────────────────────────────────

    def _build_tools(self) -> list[types.Tool]:
        return [
            types.Tool(function_declarations=[

                types.FunctionDeclaration(
                    name="create_task",
                    description=(
                        "Create a new task. Use when the user says "
                        "'add a task', 'create a task', 'remind me to', 'I need to'."
                    ),
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "title":       types.Schema(type=types.Type.STRING, description="Task title (required)"),
                            "description": types.Schema(type=types.Type.STRING, description="Optional longer description"),
                            "priority":    types.Schema(type=types.Type.STRING, description="low, medium, or high"),
                            "status":      types.Schema(type=types.Type.STRING, description="todo, in_progress, or done"),
                            "due_date":    types.Schema(type=types.Type.STRING, description="ISO date e.g. 2026-06-01"),
                            "tags":        types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
                        },
                        required=["title"],
                    ),
                ),

                types.FunctionDeclaration(
                    name="list_tasks",
                    description=(
                        "List existing tasks. Use when the user asks "
                        "'show my tasks', 'what do I have', 'show high priority tasks'."
                    ),
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "status":   types.Schema(type=types.Type.STRING, description="Filter: todo, in_progress, done"),
                            "priority": types.Schema(type=types.Type.STRING, description="Filter: low, medium, high"),
                            "tag":      types.Schema(type=types.Type.STRING, description="Filter by tag name"),
                        },
                    ),
                ),

                types.FunctionDeclaration(
                    name="update_task",
                    description="Update an existing task's status, priority, title, or other fields.",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "task_id":     types.Schema(type=types.Type.STRING, description="The task UUID — required"),
                            "title":       types.Schema(type=types.Type.STRING),
                            "description": types.Schema(type=types.Type.STRING),
                            "status":      types.Schema(type=types.Type.STRING, description="todo, in_progress, or done"),
                            "priority":    types.Schema(type=types.Type.STRING, description="low, medium, or high"),
                            "due_date":    types.Schema(type=types.Type.STRING),
                            "tags":        types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
                        },
                        required=["task_id"],
                    ),
                ),

                types.FunctionDeclaration(
                    name="delete_task",
                    description="Delete a task permanently by its ID.",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "task_id": types.Schema(type=types.Type.STRING, description="The task UUID"),
                        },
                        required=["task_id"],
                    ),
                ),

                types.FunctionDeclaration(
                    name="create_note",
                    description=(
                        "Create a new note. Use when the user says "
                        "'save a note', 'write this down', 'note that'."
                    ),
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "title":          types.Schema(type=types.Type.STRING),
                            "content":        types.Schema(type=types.Type.STRING),
                            "tags":           types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
                            "linked_task_id": types.Schema(type=types.Type.STRING, description="UUID of a task to link to"),
                        },
                        required=["title", "content"],
                    ),
                ),

                types.FunctionDeclaration(
                    name="list_notes",
                    description="List notes, optionally filtered by tag or linked task.",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "tag":            types.Schema(type=types.Type.STRING),
                            "linked_task_id": types.Schema(type=types.Type.STRING),
                        },
                    ),
                ),

                types.FunctionDeclaration(
                    name="summarize_notes",
                    description=(
                        "Fetch all notes and return their content so the AI can summarize them. "
                        "Use when user asks to summarize or review notes."
                    ),
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "tag": types.Schema(type=types.Type.STRING, description="Optional tag to filter notes"),
                        },
                    ),
                ),

            ])
        ]

    # ── Tool executor ──────────────────────────────────────────────────────────

    def _execute_tool(self, name: str, args: dict) -> str:
        try:
            if name == "create_task":
                from app.schemas.task import TaskCreate
                result = self._tasks.create(TaskCreate(**args))
                return f"Task created: id={result.id}, title={result.title}"

            elif name == "list_tasks":
                from app.schemas.task import TaskStatus, TaskPriority
                status   = TaskStatus(args["status"])     if "status"   in args else None
                priority = TaskPriority(args["priority"]) if "priority" in args else None
                tasks    = self._tasks.get_all(status=status, priority=priority, tag=args.get("tag"))

                if not tasks:
                    return "No tasks found."

                # Give Gemini all fields so it can format properly
                lines = []
                for t in tasks:
                    due = str(t.due_date) if t.due_date else "No due date"
                    tags = ", ".join(t.tags) if t.tags else ""
                    lines.append(
                        f"id={t.id} | title={t.title} | status={t.status} "
                        f"| priority={t.priority} | due={due} | tags={tags}"
                    )
                return "\n".join(lines)

            elif name == "update_task":
                from app.schemas.task import TaskUpdate
                task_id = args.pop("task_id")
                result  = self._tasks.update(task_id, TaskUpdate(**args))
                return f"Task updated: id={result.id}, status={result.status}, title={result.title}"

            elif name == "delete_task":
                self._tasks.delete(args["task_id"])
                return f"Task {args['task_id']} deleted successfully."

            elif name == "create_note":
                from app.schemas.note import NoteCreate
                result = self._notes.create(NoteCreate(**args))
                return f"Note created: id={result.id}, title={result.title}"

            elif name == "list_notes":
                notes = self._notes.get_all(
                    tag=args.get("tag"),
                    linked_task_id=args.get("linked_task_id"),
                )
                if not notes:
                    return "No notes found."

                lines = []
                for n in notes:
                    tags    = ", ".join(n.tags) if n.tags else ""
                    preview = n.content[:100] + "..." if len(n.content) > 100 else n.content
                    linked  = n.linked_task_id or ""
                    lines.append(
                        f"id={n.id} | title={n.title} | preview={preview} "
                        f"| tags={tags} | linked_task_id={linked}"
                    )
                return "\n".join(lines)


            elif name == "summarize_notes":
                notes = self._notes.get_all(tag=args.get("tag"))
                if not notes:
                    return "No notes found."

                lines = []
                for n in notes:
                    tags = ", ".join(n.tags) if n.tags else "no tags"
                    lines.append(f"title={n.title} | tags={tags}\ncontent={n.content}")
                return "\n\n".join(lines)

        except Exception as e:
            return f"Tool error ({name}): {str(e)}"
        
    def _chat_with_retry(self,request: MCPChatRequest, max_retries: int = 3) -> MCPChatResponse:
        for attempt in range(max_retries):
            try:
                return self._chat(request)
            except AIProviderError as e:
                if e.status_code == 429 and attempt < max_retries -1:
                    wait = e.retry_after or (2 ** attempt)
                    time.sleep(wait)
                    continue
                raise

    def chat(self, request: MCPChatRequest) -> MCPChatResponse:
        try:
            return self._chat_with_retry(request)

        except ClientError as e:
            # New google-genai SDK stores status code in .code, not .status_code
            # Safely extract it with fallback
            status_code = getattr(e, "code", None) or getattr(e, "status_code", None) or 500
            raw_message = str(e)

            if status_code == 429:
                retry_after = self._parse_retry_delay(raw_message)
                raise AIProviderError(
                    status_code=429,
                    message=(
                        "Gemini API rate limit reached. "
                        f"Please wait {retry_after} seconds and try again. "
                        "(Free tier limit: 15 requests/minute, 1500 requests/day)"
                    ),
                    retry_after=retry_after,
                )

            elif status_code == 403:
                raise AIProviderError(
                    status_code=502,
                    message="Gemini API key is invalid or has insufficient permissions.",
                )

            elif status_code == 404:
                raise AIProviderError(
                    status_code=502,
                    message=f"Gemini model not found. {raw_message}",
                )

            elif status_code == 503:
                raise AIProviderError(
                    status_code=502,
                    message="Gemini API is temporarily unavailable. Please try again shortly.",
                )

            else:
                raise AIProviderError(
                    status_code=502,
                    message=f"Gemini API error ({status_code}): {raw_message}",
                )
        except AIProviderError:
            raise   # already formatted, let it bubble up

        except Exception as e:
            raise AIProviderError(
                status_code=500,
                message=f"Unexpected error in AI service: {str(e)}",
            )

    # ── Internal chat logic (separated so chat() stays clean) ─────────────────

    def _chat(self, request: MCPChatRequest) -> MCPChatResponse:
        session_id = request.session_id
        if request.history:

            history = [
                types.Content(
                    role=msg.role,
                    parts=[types.Part(text=msg.content)],
                )
                for msg in request.history
            ]
        else:

            stored = session_store.get_history(session_id)
            history = [
                types.Content(
                    role=msg.role,
                    parts=[types.Part(text=msg.content)],
                )
                for msg in stored
            ]
        system_instruction = """
        You are a helpful personal assistant managing the user's tasks and notes.
        Use the provided tools to create, update, list, or delete tasks and notes.

        ## Response formatting rules — follow these exactly:

        ### When listing TASKS — always use this format:
        📋 **Your Tasks** (show total count)

        then for each task:
        [STATUS EMOJI] **[PRIORITY BADGE] Task title**
        📅 Due: due_date (or "No due date")
        🏷️ Tags: tag1, tag2 (or skip if no tags)
        🆔 ID: task_id

        Status emojis:
        ✅ = done
        🔄 = in_progress  
        📌 = todo

        Priority badges:
        🔴 HIGH
        🟡 MEDIUM
        🟢 LOW

        End with a summary line like:
        📊 Total: X tasks | X todo · X in progress · X done

        ---

        ### When listing NOTES — always use this format:
        📝 **Your Notes** (show total count)

        then for each note:
        📄 **Note title**
        💬 content preview (first 100 characters then ...)
        🏷️ Tags: tag1, tag2 (or skip if no tags)
        🔗 Linked task: task_id (or skip if not linked)
        🆔 ID: note_id

        ---

        ### When CREATING a task — confirm like this:
        ✅ **Task created successfully!**
        📌 Title: task title
        🎯 Priority: priority
        📅 Due: due_date
        🆔 ID: task_id

        ---

        ### When CREATING a note — confirm like this:
        ✅ **Note saved successfully!**
        📄 Title: note title
        🆔 ID: note_id

        ---

        ### When UPDATING a task — confirm like this:
        ✅ **Task updated!**
        📌 Title: task title
        🔄 New status: status
        🆔 ID: task_id

        ---

        ### When DELETING — confirm like this:
        🗑️ **Task deleted successfully.**
        🆔 ID: task_id

        ---

        ### When NO results found:
        🔍 No tasks found. Try creating one by saying "add a task called..."

        ---

        ### General rules:
        - Always be friendly and concise.
        - Never show raw JSON or Python dicts.
        - Never show technical field names like created_at or updated_at.
        - If the user's request is unclear, ask one clarifying question.
        - For errors, explain what went wrong in plain English.
        """

        chat_session = self._client.chats.create(
            model=self._model,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=self._tools,
            ),
            history=history,
        )

        response     = chat_session.send_message(request.message)
        tools_called = []

        if not response.candidates:
                return MCPChatResponse(
                    reply="Gemini returned an empty response. Please try again.",
                    tools_called=[],
                )
        while True:
            tool_calls = [
                part for part in response.candidates[0].content.parts
                if getattr(part, "function_call", None) is not None
            ]

            if not tool_calls:
                break

            tool_results = []
            for part in tool_calls:
                fn   = part.function_call
                name = fn.name
                args = dict(fn.args)

                tools_called.append(name)
                result_text = self._execute_tool(name, args)

                tool_results.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=name,
                            response={"result": result_text},
                        )
                    )
                )

            # Pass parts list directly — not wrapped in Content
            response = chat_session.send_message(tool_results)

        reply = ""

        for part in response.candidates[0].content.parts:
            text = getattr(part, "text", None)
            if text:
                reply += text

        reply = reply.strip()

        # Fallback if Gemini returned nothing usable
        if not reply:
            if tools_called:
                reply = f"Done! I used the following actions: {', '.join(tools_called)}."
            else:
                reply = "I'm not sure how to help with that. Try rephrasing your request."

        return MCPChatResponse(reply=reply, tools_called=tools_called)

    # ── Helper: parse retry delay from Gemini's error message ─────────────────

    @staticmethod
    def _parse_retry_delay(message: str) -> int:
        """Extracts retry seconds from Gemini's error message, defaults to 60."""
        match = re.search(r"retry[^\d]*(\d+)", message, re.IGNORECASE)
        return int(match.group(1)) if match else 60