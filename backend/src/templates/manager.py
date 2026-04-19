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
        template_type: TemplateType,
        fields: List[TemplateField] = None,
        description: str = "",
        format_config: dict = None
    ) -> Template:
        """创建新模板"""
        template = Template(
            id=self._next_id,
            name=name,
            type=template_type,
            fields=fields or [],
            description=description,
            format_config=format_config or {}
        )
        self._templates[template.id] = template
        self._next_id += 1
        return template

    def get_template(self, template_id: int) -> Optional[Template]:
        """获取模板"""
        return self._templates.get(template_id)

    def list_templates(self, template_type: Optional[TemplateType] = None) -> List[Template]:
        """列出模板"""
        templates = list(self._templates.values())
        if template_type:
            templates = [t for t in templates if t.type == template_type]
        return templates

    def delete_template(self, template_id: int) -> bool:
        """删除模板"""
        if template_id in self._templates:
            del self._templates[template_id]
            return True
        return False
