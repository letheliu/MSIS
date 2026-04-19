import pytest
from pydantic import ValidationError
from src.templates.models import Template, TemplateField, TemplateType, FieldType, GeneratedDocument


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


def test_template_without_id():
    """测试未保存的模板（无id）"""
    template = Template(
        name="新建模板",
        type=TemplateType.NOTICE
    )
    assert template.id is None


def test_generated_document():
    """测试 GeneratedDocument 模型"""
    doc = GeneratedDocument(
        id=1,
        template_id=10,
        content="文档内容",
        metadata={"author": "张三"}
    )
    assert doc.id == 1
    assert doc.template_id == 10
    assert doc.content == "文档内容"
    assert doc.metadata["author"] == "张三"


def test_generated_document_without_id():
    """测试未保存的 GeneratedDocument"""
    doc = GeneratedDocument(
        template_id=10,
        content="文档内容"
    )
    assert doc.id is None


def test_field_types():
    """测试各字段类型"""
    text_field = TemplateField(name="f1", label="文本", field_type=FieldType.TEXT)
    assert text_field.field_type == FieldType.TEXT

    textarea_field = TemplateField(name="f2", label="多行文本", field_type=FieldType.TEXTAREA)
    assert textarea_field.field_type == FieldType.TEXTAREA

    date_field = TemplateField(name="f3", label="日期", field_type=FieldType.DATE)
    assert date_field.field_type == FieldType.DATE

    select_field = TemplateField(name="f4", label="选择", field_type=FieldType.SELECT, options=["A", "B"])
    assert select_field.field_type == FieldType.SELECT


def test_template_types():
    """测试各模板类型"""
    command = Template(name="命令模板", type=TemplateType.COMMAND)
    assert command.type == TemplateType.COMMAND

    report = Template(name="报告模板", type=TemplateType.REPORT)
    assert report.type == TemplateType.REPORT

    notice = Template(name="通知模板", type=TemplateType.NOTICE)
    assert notice.type == TemplateType.NOTICE

    summary = Template(name="总结模板", type=TemplateType.SUMMARY)
    assert summary.type == TemplateType.SUMMARY

    memo = Template(name="纪要模板", type=TemplateType.MEMO)
    assert memo.type == TemplateType.MEMO
