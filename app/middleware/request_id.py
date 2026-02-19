import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import request_id_var


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        # store in contextvar for log formatter
        request_id_var.set(request_id)
        response: Response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response
