"""
健康检查 API 路由

接口列表：
- GET /api/health        基础健康检查
- GET /api/health/detail 详细健康检查，包含 PostgreSQL、Redis、MinIO 状态
"""

from fastapi import APIRouter
from sqlalchemy import text

from app.config.settings import settings
from app.core.logger import get_logger


logger = get_logger(__name__)

router = APIRouter(tags=["健康检查"])


@router.get("/api/health", summary="基础健康检查")
async def health_check():
    """
    基础健康检查。

    用途：
    - 判断 FastAPI 应用进程是否存活
    - 不依赖 PostgreSQL、Redis、MinIO
    - 响应速度快，适合 liveness probe
    """
    return {
        "code": 200,
        "message": "ok",
        "data": {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
        },
    }


@router.get("/api/health/detail", summary="详细健康检查")
async def health_check_detail():
    """
    详细健康检查。

    检查内容：
    - PostgreSQL 连接
    - Redis 连接
    - MinIO 连接

    任一服务不可用时，不抛异常，而是标记为 unhealthy。
    """
    services = {}

    # ── 检查 PostgreSQL ──────────────────────────────
    try:
        from app.database.session import SessionLocal

        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()

        services["database"] = {
            "status": "healthy",
            "message": "PostgreSQL 连接正常",
        }
    except Exception as e:
        services["database"] = {
            "status": "unhealthy",
            "message": f"PostgreSQL 连接失败: {str(e)}",
        }
        logger.error("PostgreSQL 健康检查失败: %s", str(e))

    # ── 检查 Redis ───────────────────────────────────
    try:
        import redis

        r = redis.from_url(settings.REDIS_URL)
        try:
            r.ping()
        finally:
            r.close()

        services["redis"] = {
            "status": "healthy",
            "message": "Redis 连接正常",
        }
    except Exception as e:
        services["redis"] = {
            "status": "unhealthy",
            "message": f"Redis 连接失败: {str(e)}",
        }
        logger.error("Redis 健康检查失败: %s", str(e))

    # ── 检查 MinIO ───────────────────────────────────
    try:
        from app.storage.minio_client import minio_client

        minio_client.client.list_buckets()

        services["minio"] = {
            "status": "healthy",
            "message": "MinIO 连接正常",
        }
    except Exception as e:
        services["minio"] = {
            "status": "unhealthy",
            "message": f"MinIO 连接失败: {str(e)}",
        }
        logger.error("MinIO 健康检查失败: %s", str(e))

    # ── 汇总状态 ─────────────────────────────────────
    all_healthy = all(
        service["status"] == "healthy"
        for service in services.values()
    )

    return {
        "code": 200,
        "message": "ok",
        "data": {
            "status": "healthy" if all_healthy else "degraded",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "services": services,
        },
    }
