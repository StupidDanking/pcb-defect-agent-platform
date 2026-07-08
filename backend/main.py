"""
FastAPI 应用入口

职责：
- 创建 FastAPI 应用实例
- 配置 CORS 跨域
- 注册 API 路由
- 提供基础健康检查接口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.config.settings import settings
from app.core.exceptions import register_exception_handlers
from app.core.middleware import RequestLoggingMiddleware


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于 YOLOv11 的目标检测智能体平台 API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 注册全局异常处理器
register_exception_handlers(app)

# 注册 API 请求日志中间件
app.add_middleware(RequestLoggingMiddleware)


# CORS 跨域配置
# 允许前端 Vite 开发服务器 http://localhost:5173 访问后端
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册认证路由
# 最终接口路径：
# POST /api/auth/register
# POST /api/auth/login
# GET  /api/auth/me
app.include_router(auth_router, prefix="/api/auth")
app.include_router(health_router)


@app.get("/", summary="根路径")
def root():
    """根路径接口"""
    return {
        "message": f"欢迎使用 {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
