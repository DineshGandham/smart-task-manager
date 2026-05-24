from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.routers import tasks, notes, ai, auth

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ────────────────────────────────────────────────────────────────
    # Create tables if they don't exist (safe — skips existing tables)
    # In production, use `alembic upgrade head` instead of create_all
    from app.models.base import Base
    from app.models import TaskModel, NoteModel  # noqa — registers models with Base
    from app.core.database import engine
    Base.metadata.create_all(bind=engine)

    yield  # ← server runs here

    # ── Shutdown ───────────────────────────────────────────────────────────────
    engine.dispose()  # close all DB connections cleanly


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Phase 1: JSON → Phase 2: PostgreSQL → Phase 3: MCP + Gemini",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,   # ← pass lifespan here instead of @app.on_event
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# ── Exception handlers ─────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(notes.router, prefix="/api/v1")
app.include_router(ai.router,    prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status":  "ok",
        "app":     settings.APP_NAME,
        "version": settings.APP_VERSION,
        "db":      "postgresql",
    }