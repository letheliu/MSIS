from src.templates.manager import TemplateManager
from src.templates.models import Template, TemplateType, TemplateField, FieldType


def test_manager_init():
    manager = TemplateManager()
    assert manager is not None


def test_create_template():
    manager = TemplateManager()
    template = manager.create_template(
        name="测试通知",
        type=TemplateType.NOTICE,
        fields=[
            TemplateField(name="title", label="标题", field_type=FieldType.TEXT),
        ]
    )
    assert template.id > 0
    assert template.name == "测试通知"


def test_get_template():
    manager = TemplateManager()
    created = manager.create_template(
        name="查找测试",
        type=TemplateType.NOTICE
    )
    found = manager.get_template(created.id)
    assert found is not None
    assert found.id == created.id


def test_list_templates():
    manager = TemplateManager()
    manager.create_template("模板1", TemplateType.NOTICE)
    manager.create_template("模板2", TemplateType.COMMAND)
    templates = manager.list_templates()
    assert len(templates) >= 2
