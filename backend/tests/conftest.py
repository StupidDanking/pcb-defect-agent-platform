"""
pytest 全局 Fixtures

职责：
- 创建 FastAPI TestClient
- 使用 SQLite 测试数据库
- 覆盖正式环境中的 get_db 依赖
- 每次测试前后自动创建 / 清理数据表
"""

import os
import sys
import gc
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 确保 backend 目录在 Python 搜索路径里
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import Base, get_db  # noqa: E402
from app.entity import db_models  # noqa: F401, E402
from main import app  # noqa: E402


TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    """
    测试环境数据库依赖。

    正式环境使用 PostgreSQL；
    测试环境使用 SQLite test.db，避免影响真实数据。
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    测试会话开始时创建表，结束后删除表。

    Windows 下 SQLite 文件可能短时间被占用，
    所以删除 test.db 失败时忽略即可。
    test.db 已经加入 .gitignore，不会被提交。
    """
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)

    # 释放 SQLAlchemy 连接池，避免 Windows 锁住 test.db
    test_engine.dispose()
    gc.collect()

    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
        except PermissionError:
            # Windows 下可能还有短暂文件锁，不影响测试结果
            pass


@pytest.fixture()
def client():
    """
    FastAPI 测试客户端。
    """
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
