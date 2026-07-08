"""
认证接口测试

测试范围：
- 用户注册
- 重复注册
- 用户登录
- 错误密码登录
- 携带 Token 获取当前用户
- 未携带 Token 访问受保护接口
"""

import uuid


def unique_user():
    """
    生成唯一测试用户，避免多次运行 pytest 时用户名重复。
    """
    suffix = uuid.uuid4().hex[:8]
    return {
        "username": f"testuser_{suffix}",
        "email": f"testuser_{suffix}@example.com",
        "password": "123456",
    }


def register_user(client, user_data):
    """
    注册测试用户辅助函数。
    """
    return client.post("/api/auth/register", json=user_data)


def login_user(client, username, password):
    """
    登录测试用户辅助函数。

    注意：
    后端 /api/auth/login 使用 OAuth2PasswordRequestForm，
    所以这里必须用 data= 表单格式，而不是 json=。
    """
    return client.post(
        "/api/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )


def test_register_success(client):
    """测试用户注册成功"""
    user = unique_user()

    response = register_user(client, user)

    assert response.status_code == 201

    data = response.json()
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]
    assert data["is_active"] is True
    assert "id" in data

    # 响应中不能泄露密码字段
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_username(client):
    """测试重复用户名注册失败"""
    user = unique_user()

    first_response = register_user(client, user)
    assert first_response.status_code == 201

    duplicate_user = {
        "username": user["username"],
        "email": f"another_{uuid.uuid4().hex[:8]}@example.com",
        "password": "123456",
    }

    second_response = register_user(client, duplicate_user)

    assert second_response.status_code == 400

    data = second_response.json()
    assert data["code"] == 400
    assert "用户名" in data["message"] or "已存在" in data["message"]


def test_register_duplicate_email(client):
    """测试重复邮箱注册失败"""
    user = unique_user()

    first_response = register_user(client, user)
    assert first_response.status_code == 201

    duplicate_user = {
        "username": f"another_{uuid.uuid4().hex[:8]}",
        "email": user["email"],
        "password": "123456",
    }

    second_response = register_user(client, duplicate_user)

    assert second_response.status_code == 400

    data = second_response.json()
    assert data["code"] == 400
    assert "邮箱" in data["message"] or "已存在" in data["message"]


def test_login_success(client):
    """测试登录成功并返回 Token"""
    user = unique_user()

    register_response = register_user(client, user)
    assert register_response.status_code == 201

    login_response = login_user(
        client,
        username=user["username"],
        password=user["password"],
    )

    assert login_response.status_code == 200

    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == user["username"]


def test_login_wrong_password(client):
    """测试错误密码登录失败"""
    user = unique_user()

    register_response = register_user(client, user)
    assert register_response.status_code == 201

    login_response = login_user(
        client,
        username=user["username"],
        password="wrong_password",
    )

    assert login_response.status_code == 401

    data = login_response.json()
    assert data["code"] == 401


def test_get_current_user_success(client):
    """测试携带 Token 获取当前用户信息"""
    user = unique_user()

    register_response = register_user(client, user)
    assert register_response.status_code == 201

    login_response = login_user(
        client,
        username=user["username"],
        password=user["password"],
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    me_response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert me_response.status_code == 200

    data = me_response.json()
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]
    assert data["is_active"] is True
    assert "hashed_password" not in data


def test_get_current_user_without_token(client):
    """测试未携带 Token 访问 /api/auth/me"""
    response = client.get("/api/auth/me")

    assert response.status_code == 401

    data = response.json()
    assert data["code"] == 401
    assert data["path"] == "/api/auth/me"
