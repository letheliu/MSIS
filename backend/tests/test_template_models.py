import pytest
from pydantic import ValidationError
from src.templates.models import Template, TemplateField, TemplateType, FieldType


def test_template_field():
    field = TemplateField(
        name="title",
        label="标题",
        field_type=FieldType.TEXT,
        required=True
    )
    assert field.name == "title"
    assert field.required is True


def test_template_creation():
    template = Template(
        id=1,
        name="通知模板",
        type=TemplateType.NOTICE,
        fields=[
            TemplateField(name="title", label="标题", field_type=FieldType.TEXT),
            TemplateField(name="content", label="内容", field_type=FieldType.TEXTAREA)
        ]
    )
    assert template.name == "通知模板"
    assert len(template.fields) == 2


def test_template_validation():
    with pytest.raises(ValidationError):
        Template(id=1, name="", type=TemplateType.NOTICE)


def test_template_field_select_with_options():
    field = TemplateField(
        name="priority",
        label="优先级",
        field_type=FieldType.SELECT,
        options=["高", "中", "低"]
    )
    assert field.field_type == FieldType.SELECT
    assert len(field.options) == 3


def test_template_default_values():
    template = Template(
        id=2,
        name="默认值测试模板",
        type=TemplateType.REPORT
    )
    assert template.description == ""
    assert template.fields == []
    assert template.format_config == {}
