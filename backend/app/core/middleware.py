"""
请求日志中间件

职责：
- 记录每一次 HTTP 请求
- 记录请求方法、路径、状态码、耗时、客户端 IP
- 出现异常时记录异常日志
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import get_logger


logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    API 请求日志中间件。

    每个请求都会记录一条日志，例如：
        GET /api/health 200 12.35ms client=127.0.0.1
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        start_time = time.perf_counter()

        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"

        try:
            response = await call_next(request)

            process_time_ms = (time.perf_counter() - start_time) * 1000

            response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"

            logger.info(
                "HTTP Request: method=%s path=%s status=%s duration=%.2fms client=%s",
                method,
                path,
                response.status_code,
                process_time_ms,
                client_host,
            )

            return response

        except Exception as exc:
            process_time_ms = (time.perf_counter() - start_time) * 1000

            logger.exception(
                "HTTP Request Failed: method=%s path=%s duration=%.2fms client=%s error=%s",
                method,
                path,
                process_time_ms,
                client_host,
                str(exc),
            )

            raise
