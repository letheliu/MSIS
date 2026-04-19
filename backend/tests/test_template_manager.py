from src.templates.manager import TemplateManager
from src.templates.models import Template, TemplateType, TemplateField, FieldType


def test_manager_init():
    manager = TemplateManager()
    assert manager is not None


def test_create_template():
    manager = TemplateManager()
    template = manager.create_template(
        name="测试通知",
        template_type=TemplateType.NOTICE,
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
        template_type=TemplateType.NOTICE
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


def test_list_templates_by_type():
    manager = TemplateManager()
    manager.create_template("通知1", TemplateType.NOTICE)
    manager.create_template("通知2", TemplateType.NOTICE)
    manager.create_template("命令1", TemplateType.COMMAND)
    notice_templates = manager.list_templates(template_type=TemplateType.NOTICE)
    command_templates = manager.list_templates(template_type=TemplateType.COMMAND)
    assert len(notice_templates) == 2
    assert len(command_templates) == 1
    assert all(t.type == TemplateType.NOTICE for t in notice_templates)
    assert all(t.type == TemplateType.COMMAND for t in command_templates)


def test_delete_template():
    manager = TemplateManager()
    created = manager.create_template("待删除", TemplateType.NOTICE)
    result = manager.delete_template(created.id)
    assert result is True
    found = manager.get_template(created.id)
    assert found is None


def test_get_template_not_exists():
    manager = TemplateManager()
    found = manager.get_template(999)
    assert found is None


def test_delete_template_not_exists():
    manager = TemplateManager()
    result = manager.delete_template(999)
    assert result is False
