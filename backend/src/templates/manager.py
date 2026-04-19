from typing import List, Optional
from .models import Template, TemplateType, TemplateField, FieldType


class TemplateManager:
    """模板管理器"""

    def __init__(self):
        self._templates: dict[int, Template] = {}
        self._next_id = 1

    def create_template(
        self,
        name: str,
        type: TemplateType,
        fields: List[TemplateField] = None,
        description: str = ""
    ) -> Template:
        """创建新模板"""
        template = Template(
            id=self._next_id,
            name=name,
            type=type,
            fields=fields or [],
            description=description
        )
        self._templates[template.id] = template
        self._next_id += 1
        return template

    def get_template(self, template_id: int) -> Optional[Template]:
        """获取模板"""
        return self._templates.get(template_id)

    def list_templates(self, type: Optional[TemplateType] = None) -> List[Template]:
        """列出模板"""
        templates = list(self._templates.values())
        if type:
            templates = [t for t in templates if t.type == type]
        return templates

    def delete_template(self, template_id: int) -> bool:
        """删除模板"""
        if template_id in self._templates:
            del self._templates[template_id]
            return True
        return False
