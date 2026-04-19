from pydantic import BaseModel, Field
from enum import Enum
from typing import List


class TemplateType(str, Enum):
    """模板类型"""
    COMMAND = "command"      # 命令
    REPORT = "report"        # 报告
    NOTICE = "notice"        # 通知
    SUMMARY = "summary"      # 总结
    MEMO = "memo"            # 纪要


class FieldType(str, Enum):
    """字段类型"""
    TEXT = "text"
    TEXTAREA = "textarea"
    DATE = "date"
    SELECT = "select"


class TemplateField(BaseModel):
    """模板字段定义"""
    name: str = Field(..., description="字段标识")
    label: str = Field(..., description="字段显示名称")
    field_type: FieldType = Field(default=FieldType.TEXT, description="字段类型")
    required: bool = Field(default=True, description="是否必填")
    default: str = Field(default="", description="默认值")
    options: List[str] = Field(default_factory=list, description="选项（仅select类型）")


class Template(BaseModel):
    """公文模板"""
    id: int | None = None
    name: str = Field(..., min_length=1, description="模板名称")
    type: TemplateType = Field(..., description="模板类型")
    description: str = Field(default="", description="模板描述")
    fields: List[TemplateField] = Field(default_factory=list, description="模板字段")
    format_config: dict = Field(default_factory=dict, description="格式配置")


class GeneratedDocument(BaseModel):
    """生成的文档"""
    id: int | None = None
    template_id: int
    content: str
    metadata: dict = Field(default_factory=dict)
