from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_list_templates():
    response = client.get("/api/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data

def test_create_template():
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

def test_render_template():
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
