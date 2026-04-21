import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator

from src.templates.manager import TemplateManager
from src.templates.renderer import TemplateRenderer
from src.templates.models import TemplateType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/templates", tags=["templates"])

template_manager = TemplateManager()
template_renderer = TemplateRenderer()

template_manager.create_template(
    name="通知模板",
    template_type=TemplateType.NOTICE,
    description="标准公文通知格式",
    format_config={"header": "通知", "footer": "发文机关"}
)
template_manager.create_template(
    name="命令模板",
    template_type=TemplateType.COMMAND,
    description="军事命令格式",
    format_config={"header": "命令", "footer": "指挥机关"}
)


class TemplatesResponse(BaseModel):
    templates: list
    total: int


class CreateTemplateRequest(BaseModel):
    name: str
    type: str
    description: str = ""

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        try:
            TemplateType(v)
            return v
        except ValueError:
            valid_types = [t.value for t in TemplateType]
            raise ValueError(f"无效的类型: {v}. 有效类型为: {valid_types}")


class RenderRequest(BaseModel):
    title: str
    content: str


@router.get("", response_model=TemplatesResponse)
def list_templates(type: str = None):
    try:
        filter_type = TemplateType(type) if type else None
        templates = template_manager.list_templates(filter_type)
        return TemplatesResponse(templates=templates, total=len(templates))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的类型参数: {type}. 有效类型为: {[t.value for t in TemplateType]}"
        )


@router.post("")
def create_template(request: CreateTemplateRequest):
    template = template_manager.create_template(
        name=request.name,
        template_type=TemplateType(request.type),
        description=request.description
    )
    return template.model_dump()


@router.post("/{template_id}/render")
def render_template(template_id: int, request: RenderRequest):
    template = template_manager.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    content = template_renderer.render(template, {
        "title": request.title,
        "content": request.content
    })
    return {"content": content}
