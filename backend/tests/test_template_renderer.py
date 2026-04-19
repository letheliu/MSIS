import pytest
from src.templates.renderer import TemplateRenderer
from src.templates.models import Template, TemplateType, TemplateField, FieldType


@pytest.fixture
def sample_template():
    return Template(
        id=1,
        name="通知模板",
        type=TemplateType.NOTICE,
        fields=[
            TemplateField(name="title", label="标题", field_type=FieldType.TEXT),
            TemplateField(name="content", label="内容", field_type=FieldType.TEXTAREA),
        ],
        format_config={
            "header": "通知",
            "footer": "发文机关"
        }
    )


def test_renderer_init():
    renderer = TemplateRenderer()
    assert renderer is not None


def test_render_template(sample_template):
    renderer = TemplateRenderer()
    result = renderer.render(sample_template, {
        "title": "关于放假的通知",
        "content": "五一劳动节放假三天"
    })
    assert "关于放假的通知" in result
    assert "五一劳动节放假三天" in result
    assert "通知" in result  # header


def test_render_empty_data(sample_template):
    """测试空数据渲染"""
    renderer = TemplateRenderer()
    result = renderer.render(sample_template, {})
    # 应该包含 header
    assert "【通知】" in result
    # 不应该包含 title 或 content
    assert "# " not in result


def test_render_no_format_config():
    """测试无 header/footer 的模板渲染"""
    template_no_format = Template(
        id=2,
        name="简单模板",
        type=TemplateType.NOTICE,
        fields=[
            TemplateField(name="title", label="标题", field_type=FieldType.TEXT),
            TemplateField(name="content", label="内容", field_type=FieldType.TEXTAREA),
        ],
        format_config={}
    )
    renderer = TemplateRenderer()
    result = renderer.render(template_no_format, {
        "title": "测试标题",
        "content": "测试内容"
    })
    # 应该包含数据
    assert "测试标题" in result
    assert "测试内容" in result
    # 不应该包含 header 或 footer
    assert "【" not in result
    assert "— " not in result


def test_render_custom_fields():
    """测试自定义字段渲染"""
    template_custom = Template(
        id=3,
        name="自定义字段模板",
        type=TemplateType.NOTICE,
        fields=[
            TemplateField(name="title", label="标题", field_type=FieldType.TEXT),
            TemplateField(name="content", label="内容", field_type=FieldType.TEXTAREA),
            TemplateField(name="department", label="部门", field_type=FieldType.TEXT),
            TemplateField(name="date", label="日期", field_type=FieldType.TEXT),
        ],
        format_config={}
    )
    renderer = TemplateRenderer()
    result = renderer.render(template_custom, {
        "title": "会议通知",
        "content": "下午三点开会",
        "department": "行政部",
        "date": "2026-04-19"
    })
    # 应该包含所有字段
    assert "会议通知" in result
    assert "下午三点开会" in result
    assert "部门：行政部" in result
    assert "日期：2026-04-19" in result


def test_render_output_format():
    """测试输出格式的精确结构"""
    template = Template(
        id=4,
        name="格式测试模板",
        type=TemplateType.NOTICE,
        fields=[
            TemplateField(name="title", label="标题", field_type=FieldType.TEXT),
            TemplateField(name="content", label="内容", field_type=FieldType.TEXTAREA),
        ],
        format_config={
            "header": "通知",
            "footer": "发文机关"
        }
    )
    renderer = TemplateRenderer()
    result = renderer.render(template, {
        "title": "测试标题",
        "content": "测试内容"
    })
    lines = result.split("\n")
    # 验证结构
    assert lines[0] == "【通知】"
    assert lines[1] == ""
    assert lines[2] == "# 测试标题"
    assert lines[3] == ""
    assert lines[4] == "测试内容"
    assert lines[5] == ""
    assert lines[6] == "— 发文机关"
