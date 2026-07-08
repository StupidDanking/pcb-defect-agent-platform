"""
全局异常处理模块

职责：
- 捕获 HTTPException，返回统一 JSON
- 捕获请求参数校验错误，返回 422 JSON
- 捕获未知异常，记录日志并返回 500 JSON
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.config.settings import settings
from app.core.logger import get_logger


logger = get_logger(__name__)


def error_response(
    code: int,
    message: str,
    path: str,
    detail=None,
):
    """
    统一错误响应格式
    """
    content = {
        "code": code,
        "message": message,
        "path": path,
    }

    if detail is not None:
        content["detail"] = detail

    return JSONResponse(
        status_code=code,
        content=jsonable_encoder(content),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    注册全局异常处理器。

    在 main.py 中调用：
        register_exception_handlers(app)
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        处理主动抛出的 HTTPException。

        例如：
        - 401 未登录
        - 403 无权限
        - 404 资源不存在
        - 400 参数错误
        """
        logger.warning(
            "HTTPException: method=%s path=%s status=%s detail=%s",
            request.method,
            request.url.path,
            exc.status_code,
            exc.detail,
        )

        return error_response(
            code=exc.status_code,
            message=str(exc.detail),
            path=request.url.path,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        """
        处理请求参数校验错误。

        例如：
        - 注册时缺少 username
        - email 格式不合法
        - password 类型不正确
        """
        logger.warning(
            "RequestValidationError: method=%s path=%s errors=%s",
            request.method,
            request.url.path,
            exc.errors(),
        )

        return error_response(
            code=422,
            message="请求参数验证失败",
            path=request.url.path,
            detail=exc.errors() if settings.DEBUG else None,
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        处理未捕获的未知异常。

        这类异常一般说明程序内部有 bug，
        必须记录完整 traceback，方便排查。
        """
        logger.exception(
            "Unhandled Exception: method=%s path=%s error=%s",
            request.method,
            request.url.path,
            str(exc),
        )

        return error_response(
            code=500,
            message="服务器内部错误",
            path=request.url.path,
            detail=str(exc) if settings.DEBUG else None,
        )
