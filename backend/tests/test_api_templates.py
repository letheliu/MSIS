from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_list_templates():
    """测试获取模板列表"""
    response = client.get("/api/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert "total" in data
    assert data["total"] >= 2  # 初始化有2个模板

def test_list_templates_with_type_filter():
    """测试按类型过滤模板"""
    response = client.get("/api/templates?type=notice")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert "total" in data
    # 验证返回的都是 notice 类型
    for template in data["templates"]:
        assert template["type"] == "notice"

def test_list_templates_invalid_type():
    """测试无效的 type 参数"""
    response = client.get("/api/templates?type=invalid_type")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "无效的类型参数" in data["detail"]

def test_create_template():
    """测试创建模板"""
    response = client.post(
        "/api/templates",
        json={
            "name": "测试模板",
            "type": "notice",
            "description": "测试描述"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "测试模板"
    assert data["type"] == "notice"
    assert data["description"] == "测试描述"

def test_create_template_invalid_type():
    """测试创建模板时使用无效类型"""
    response = client.post(
        "/api/templates",
        json={
            "name": "测试模板",
            "type": "invalid_type",
            "description": "测试描述"
        }
    )
    assert response.status_code == 422  # Pydantic 验证错误
    data = response.json()
    assert "detail" in data

def test_render_template():
    """测试渲染模板"""
    # 先创建模板
    create_response = client.post(
        "/api/templates",
        json={
            "name": "渲染测试",
            "type": "notice"
        }
    )
    template_id = create_response.json()["id"]

    # 渲染模板
    render_response = client.post(
        f"/api/templates/{template_id}/render",
        json={
            "title": "测试标题",
            "content": "测试内容"
        }
    )
    assert render_response.status_code == 200
    data = render_response.json()
    assert "content" in data

def test_render_template_not_found():
    """测试渲染不存在的模板"""
    response = client.post(
        "/api/templates/99999/render",
        json={
            "title": "测试标题",
            "content": "测试内容"
        }
    )
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "模板不存在" in data["detail"]
