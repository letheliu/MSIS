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
