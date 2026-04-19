from typing import Dict
from .models import Template


class TemplateRenderer:
    """模板渲染器"""

    def __init__(self):
        pass

    def render(self, template: Template, data: Dict[str, str]) -> str:
        """渲染模板"""
        lines = []

        # 添加头部
        if "header" in template.format_config:
            lines.append(f"【{template.format_config['header']}】")
            lines.append("")

        # 添加标题
        if "title" in data:
            lines.append(f"# {data['title']}")
            lines.append("")

        # 添加内容
        if "content" in data:
            lines.append(data["content"])
            lines.append("")

        # 添加字段
        for field in template.fields:
            if field.name in ["title", "content"]:
                continue
            if field.name in data:
                lines.append(f"{field.label}：{data[field.name]}")

        # 添加尾部
        if "footer" in template.format_config:
            lines.append("")
            lines.append(f"— {template.format_config['footer']}")

        return "\n".join(lines)
