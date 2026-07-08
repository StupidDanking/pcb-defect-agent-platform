"""
统一日志配置模块

职责：
- 配置全局日志格式和输出级别
- 同时输出到控制台和日志文件
- 日志文件按大小自动轮转

使用方式：
    from app.core.logger import get_logger

    logger = get_logger(__name__)
    logger.info("服务启动成功")
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config.settings import settings


# backend 目录
BACKEND_DIR = Path(__file__).resolve().parents[2]

# 日志目录：backend/logs
LOG_DIR = BACKEND_DIR / settings.LOG_DIR
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 日志格式
LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | "
    "%(name)s:%(funcName)s:%(lineno)d | %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

_initialized = False


def setup_logging() -> None:
    """
    初始化全局日志系统。

    输出目标：
    1. 控制台：开发时实时查看
    2. 文件：写入 backend/logs/app.log，并按大小自动轮转
    """
    global _initialized

    if _initialized:
        return

    _initialized = True

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 避免重复添加 handler
    root_logger.handlers.clear()

    # 控制台 Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件 Handler
    file_path = LOG_DIR / "app.log"

    file_handler = RotatingFileHandler(
        filename=file_path,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 降低第三方库日志级别，避免刷屏
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("minio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的 Logger。

    推荐传入 __name__，这样日志中能显示模块路径。
    """
    setup_logging()
    return logging.getLogger(name)
