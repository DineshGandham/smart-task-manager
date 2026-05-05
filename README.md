# 🧠 Smart Task Manager

> A production-structured REST API for managing tasks and notes — powered by **FastAPI**, **MCP (Model Context Protocol)**, and **Gemini AI**. Talk to your tasks in plain English.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Gemini-3.0_Flash_Preview-4285F4?style=flat&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/MCP-Tool_Calling-FF6B35?style=flat"/>
  <img src="https://img.shields.io/badge/uv-Package_Manager-DE5FE9?style=flat"/>
  <img src="https://img.shields.io/badge/Tests-29_passing-2ECC71?style=flat&logo=pytest&logoColor=white"/>
</p>

---

## ✨ What makes this project different

Most task managers are just CRUD apps. This one lets you **talk to your data**:

```
You:  "Show me all my high priority tasks"
AI:   📋 Your Tasks (3 tasks)
      🔴 HIGH  Learn MCP tool calling  📅 Due: 2026-06-01
      🔴 HIGH  Deploy to Railway       📅 Due: 2026-07-01
      📊 Total: 3 tasks | 1 todo · 1 in progress · 1 done

You:  "Mark the Deploy task as done"
AI:   ✅ Task updated!
         📌 Title: Deploy to Railway
         🔄 New status: done
```

The AI doesn't fake this — it calls your **real FastAPI services** through MCP tool definitions, reads from your actual data store, and returns a structured, human-friendly reply.

---

## 🏗️ Architecture

```
smart-task-manager/
├── app/
│   ├── main.py                  # FastAPI app — middleware, routers, handlers
│   ├── routers/                 # HTTP layer — thin, zero business logic
│   │   ├── tasks.py             # CRUD endpoints for tasks
│   │   ├── notes.py             # CRUD endpoints for notes
│   │   └── ai.py                # POST /ai/chat — MCP entry point
│   ├── services/                # Business logic layer
│   │   ├── task_service.py      # Task rules, validation, filtering
│   │   ├── note_service.py      # Note rules, linking to tasks
│   │   └── mcp_service.py       # Gemini tool loop + tool executor
│   ├── repositories/            # Data access layer
│   │   ├── base.py              # Abstract interface (swap DB without touching services)
│   │   ├── json_repo.py         # Phase 1: JSON file store
│   │   └── pg_repo.py           # Phase 2: PostgreSQL stub (ready to implement)
│   ├── schemas/                 # Pydantic v2 models
│   │   ├── task.py              # TaskCreate, TaskUpdate, TaskOut + enums
│   │   ├── note.py              # NoteCreate, NoteUpdate, NoteOut
│   │   └── mcp.py               # MCPChatRequest, MCPChatResponse
│   ├── core/
│   │   ├── config.py            # pydantic-settings — loads from .env
│   │   ├── dependencies.py      # FastAPI Depends() wiring
│   │   └── exceptions.py        # Custom exceptions + global handlers
│   └── middleware/
│       └── logging.py           # Request/response logging with timing
├── data/db.json                 # Phase 1 storage (auto-created, gitignored)
├── tests/                       # 29 pytest tests, isolated temp DB per test
└── pyproject.toml               # uv project config
```

---

## 🤖 MCP — How the AI chat works

The `/api/v1/ai/chat` endpoint implements a **full MCP tool-calling loop**:

```
User message
     │
     ▼
Gemini receives message + 7 tool schemas (create_task, list_tasks, etc.)
     │
     ▼
Gemini decides which tool to call + what arguments to pass
     │
     ▼
MCPService executes the real service method against the data store
     │
     ▼
Tool result sent back to Gemini
     │
     ▼
Gemini formats a natural language reply following your style rules
     │
     ▼
{ "reply": "...", "tools_called": ["list_tasks"] }
```

**Available MCP tools:**

| Tool | Description |
|------|-------------|
| `create_task` | Creates a task with title, priority, due date, tags |
| `list_tasks` | Lists tasks, filterable by status / priority / tag |
| `update_task` | Updates any field on an existing task |
| `delete_task` | Deletes a task by ID |
| `create_note` | Creates a note, optionally linked to a task |
| `list_notes` | Lists notes, filterable by tag or linked task |
| `summarize_notes` | Returns note content for AI to summarize |

---

## 🚀 Getting started

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) installed
- A free [Gemini API key](https://aistudio.google.com/app/apikey)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/smart-task-manager.git
cd smart-task-manager

# 2. Create virtual environment and install dependencies
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 4. Start the server
uvicorn app.main:app --reload
```

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Swagger UI — try every endpoint |
| http://localhost:8000/redoc | ReDoc documentation |
| http://localhost:8000/health | Health check |

---

## 📡 API reference

### Tasks

```
GET    /api/v1/tasks/              List tasks  (?status=todo&priority=high&tag=mcp)
POST   /api/v1/tasks/              Create task                          → 201
GET    /api/v1/tasks/{id}          Get task by ID
PATCH  /api/v1/tasks/{id}          Partial update (only send changed fields)
DELETE /api/v1/tasks/{id}          Delete task                          → 204
```

### Notes

```
GET    /api/v1/notes/              List notes  (?tag=python&linked_task_id=uuid)
POST   /api/v1/notes/              Create note                          → 201
GET    /api/v1/notes/{id}          Get note by ID
PATCH  /api/v1/notes/{id}          Partial update
DELETE /api/v1/notes/{id}          Delete note                          → 204
```

### AI Chat

```
POST   /api/v1/ai/chat             Natural language interface
```

**Request:**
```json
{
  "message": "Create a high priority task called Deploy to Railway due 2026-07-01",
  "history": []
}
```

**Response:**
```json
{
  "reply": "✅ Task created successfully!\n   📌 Title: Deploy to Railway\n   🎯 Priority: high\n   📅 Due: 2026-07-01\n   🆔 ID: abc-123",
  "tools_called": ["create_task"]
}
```

### Example chat messages to try

```
"Show me all my tasks"
"Show only high priority todo tasks"
"Create a task called Learn PostgreSQL, medium priority, due 2026-08-01, tag it backend"
"Mark task {id} as done"
"Save a note titled MCP Learnings with content Tool calling connects AI to real services"
"Summarize all my notes tagged python"
"Delete task {id}"
```

---

## 🧪 Running tests

```bash
pytest -v
```

```
tests/test_tasks.py::test_create_returns_201           PASSED
tests/test_tasks.py::test_blank_title_rejected         PASSED
tests/test_tasks.py::test_past_due_date_rejected       PASSED
tests/test_tasks.py::test_tags_are_lowercased          PASSED
tests/test_tasks.py::test_filter_by_status             PASSED
tests/test_tasks.py::test_patch_only_changes_sent_fields PASSED
...
29 passed in 0.42s
```

Tests use FastAPI's `dependency_overrides` to inject a fresh temp database per test — the real `data/db.json` is never touched.

---

## 🔑 Design decisions worth noting

**Repository pattern** — `repositories/base.py` defines an abstract interface. Services only depend on this interface, never on the storage engine. Swapping to PostgreSQL means changing one function in `dependencies.py`. Nothing in services or routers changes.

**`exclude_unset=True` on PATCH** — `TaskUpdate` with `{"status": "done"}` only saves the status field. It doesn't overwrite title, tags, or priority with `None`. This is correct REST partial update behaviour.

**Dependency injection for testing** — `get_task_repo` and `get_note_repo` are FastAPI dependencies. Tests override them with `app.dependency_overrides` pointing to a temp file. No mocking, real code path, isolated data.

**MCP tool descriptions** — Gemini picks which tool to call purely from reading the `description` field in each `FunctionDeclaration`. Well-written descriptions = correct tool selection. Vague descriptions = wrong calls.

**Custom exception handlers** — `NotFoundError`, `ValidationError`, and `AIProviderError` all produce consistent JSON error shapes. The Gemini 429 rate limit becomes a proper `429` response with `retry_after_seconds`, not a raw 500.

---

## 🗺️ Roadmap

- [x] **Phase 1** — Task + Note REST API with JSON file store
- [x] **Phase 3** — MCP tool calling with Gemini 2.0 Flash
- [ ] **Phase 2** — PostgreSQL + SQLAlchemy 2.0 (swap `json_repo.py` → `pg_repo.py`)
- [ ] Conversation session memory (stateful multi-turn chat)
- [ ] Retry with exponential backoff on Gemini 429
- [ ] `get_overdue_tasks` MCP tool
- [ ] `search_notes` full-text MCP tool
- [ ] Task analytics — `get_summary` tool for productivity insights
- [ ] Dockerize + deploy to Railway

---

## 🛠️ Tech stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.115+ |
| Validation | Pydantic v2 |
| AI | Gemini 2.0 Flash via google-genai SDK |
| Protocol | MCP (Model Context Protocol) — tool calling |
| Config | pydantic-settings |
| Storage (Phase 1) | JSON file store |
| Storage (Phase 2) | PostgreSQL + SQLAlchemy 2.0 |
| Package manager | uv |
| Testing | pytest + httpx |
| Python | 3.11+ |

---

## 📄 License

MIT
