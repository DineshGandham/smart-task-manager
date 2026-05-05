from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarlettehHTTPException

# -----------------------------------------------------------
# CUSTOM EXCEPTION HANDLING MODULE
# -----------------------------------------------------------
# Purpose:
# - Define application-specific (domain) exceptions
# - Register global exception handlers in FastAPI
# - Ensure consistent and structured error responses
# -----------------------------------------------------------

class StmException(Exception):
    pass

class NotFoundError(StmException):

    def __init__(self, resource: str, resource_id: str):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} with {resource_id} not found.")

class ConflictError(StmException):
    """Raised when a resource already exists or a concurrent modification occurs."""

    def __init__(self, resource: str, message: str):
        self.resource = resource
        self.message = message
        super().__init__(message)

class DependencyError(StmException):
    """Raised when an operation is blocked by dependent resources."""

    def __init__(self, resource: str, dependent: str, message: str):
        self.resource = resource
        self.dependent = dependent
        self.message = message
        super().__init__(message)

class ValidationError(StmException):

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class StorageError(StmException):
    """Raised when the data store (JSON file, DB, etc.) fails."""

    def __init__(self, message: str = "Data store operation failed"):
        self.message = message
        super().__init__(message)

class ConfigurationError(StmException):
    """Raised when a required configuration value is missing or invalid."""

    def __init__(self, setting: str, message: str):
        self.setting = setting
        self.message = message
        super().__init__(message)

class ForbiddenError(StmException):
    """Raised when the user lacks permission for an action."""

    def __init__(self, message: str = "Forbidden"):
        self.message = message
        super().__init__(message)

class RateLimitError(StmException):
    """Raised when the user exceeds request rate limits."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        self.message = message
        self.retry_after = retry_after
        super().__init__(message)

class AIProviderError(StmException):

    def __init__(self, status_code: int, message:str, retry_after: int = None):
        self.status_code = status_code
        self.message = message
        self.retry_after = retry_after
        super().__init__(message)

# -----------------------------------------------------------
# REGISTER EXCEPTION HANDLERS
# -----------------------------------------------------------
# This function attaches exception handlers to FastAPI app
# Must be called once during app initialization (in main.py)
# -----------------------------------------------------------
def register_exception_handlers(app : FastAPI) -> None:

    # -------------------------------------------------------
    # Handler for NotFoundError
    # -------------------------------------------------------
    # Triggered when NotFoundError is raised anywhere in app
    # Returns HTTP 404 with structured response
    # -------------------------------------------------------
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code= 404,
            content={
                "error" : "not_found",
                "message" : str(exc),
                "resource" : exc.resource,
                "id" : exc.resource_id
            }
        )

    @app.exception_handler(ConflictError)
    async def conflict_error_handler(request: Request, exc: ConflictError):
        return JSONResponse(
            status_code=409,
            content={
                "error": "conflict",
                "message": exc.message,
                "resource": exc.resource,
            },
        )

    @app.exception_handler(DependencyError)
    async def dependency_error_handler(request: Request, exc: DependencyError):
        return JSONResponse(
            status_code=409,
            content={
                "error": "dependency_error",
                "message": exc.message,
                "resource": exc.resource,
                "dependent": exc.dependent,
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code= 422,
            content={
                "error" : "validation_error",
                "message" : exc.message
            }
        )

    @app.exception_handler(StorageError)
    async def storage_error_handler(request: Request, exc: StorageError):
        return JSONResponse(
            status_code=503,
            content={
                "error": "storage_error",
                "message": exc.message,
            },
        )

    @app.exception_handler(ConfigurationError)
    async def configuration_error_handler(request: Request, exc: ConfigurationError):
        return JSONResponse(
            status_code=500,
            content={
                "error": "configuration_error",
                "message": exc.message,
                "setting": exc.setting,
            },
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_error_handler(request: Request, exc: ForbiddenError):
        return JSONResponse(
            status_code=403,
            content={
                "error": "forbidden",
                "message": exc.message,
            },
        )

    @app.exception_handler(RateLimitError)
    async def rate_limit_error_handler(request: Request, exc: RateLimitError):
        headers = {}
        if exc.retry_after:
            headers["Retry-After"] = str(exc.retry_after)
        return JSONResponse(
            status_code=429,
            headers=headers,
            content={
                "error": "rate_limit",
                "message": exc.message,
                "retry_after_seconds": exc.retry_after,
            },
        )
    
    # ── NEW: AI provider errors return 429 or 502, never 500 ──────────────────
    @app.exception_handler(AIProviderError)
    async def ai_provider_handler(request: Request, exc: AIProviderError):
        """Raised when the AI provider (Gemini/OpenAI) returns an error."""
        content = {
            "error" : "ai_provider_error",
            "message" : exc.message
        }

        if exc.retry_after:
            content["retry_after_seconds"] = exc.retry_after
        
        return JSONResponse(status_code= exc.status_code,content= content)
    
    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        errors = [
            {
                "fields" : "->".join(str(loc) for loc in err["loc"]),
                "message" : err["msg"],
                "type" : err["type"]
            }
            for err in exc.errors()
        ]

        return JSONResponse(status_code=422, content={
            "error" : "Request_validation_error",
            "details" : errors
        })
    
    @app.exception_handler(StarlettehHTTPException)
    async def http_exception_handler(request:Request, exc:StarlettehHTTPException):
        return JSONResponse(status_code= exc.status_code, content={
            "error" : "http_error",
            "message" : exc.detail,
            "status_code" : exc.status_code,
        })
    

    @app.exception_handler(StmException)
    async def unhandled_exception_handler(request: Request, exc:StmException):
        return JSONResponse(
            status_code= 500,
            content= {
                "error" : "internal_server_error",
                "message" : "Something went wrong. Please try again."
            })
