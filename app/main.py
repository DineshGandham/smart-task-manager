from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.routers import tasks,notes,ai

settings = get_settings()

app = FastAPI(
    title= settings.APP_NAME,
    version= settings.APP_VERSION,
    description= "Phase 1: JSON store. Phase 2: PostgreSQL. Phase 3: MCP + AI.",
    docs_url= "/docs",
    redoc_url= "/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins= settings.CORS_ORIGINS,
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

app.include_router(tasks.router, prefix="/api/v1")
app.include_router(notes.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV
    }

