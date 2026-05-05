import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("smart-task-manager")

logging.basicConfig(
    level= logging.INFO,
    format= "%(ascTime)s | %(levelname)s | %(message)s",

)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        logger.info(f"-> {request.method} {request.url.path}")
        try :
            response = await call_next(request)

        except Exception as exc:
            logger.error(f"x unhandled exception on {request.url.path}: {exc} ")
            raise
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"<- {request.method} {request.url.path}"
            f"| status={response.status_code} | {duration_ms:.1f}ms"
        )

        return response