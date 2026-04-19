from fastapi import FastAPI, Query, HTTPException, status
from pydantic import BaseModel, field_validator
from src.search.retriever import DocumentRetriever
from src.templates.manager import TemplateManager
from src.templates.renderer import TemplateRenderer
from src.templates.models import TemplateType, Template

app = FastAPI(title="MSIS API", version="0.0.1")

# 示例文档数据（实际应从数据库加载）
sample_docs = [
    {"id": 1, "title": "训练计划", "content": "年度训练计划安排"},
    {"id": 2, "title": "工作汇报", "content": "季度工作总结报告"},
    {"id": 3, "title": "通知", "content": "关于放假安排的通知"},
    {"id": 4, "title": "命令", "content": "关于战备转换的命令"},
]

retriever = DocumentRetriever(documents=sample_docs)

# 模板管理
template_manager = TemplateManager()
template_renderer = TemplateRenderer()

# 初始化示例模板
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

@app.get("/")
def root():
    return {"message": "MSIS - Military Document Writing Assistant API"}

@app.get("/health")
def health():
    return {"status": "ok"}

class SearchResponse(BaseModel):
    query: str
    results: list
    total: int

@app.get("/api/search", response_model=SearchResponse)
def search(q: str = Query(..., min_length=1, description="搜索关键词")):
    """搜索公文文档"""
    results = retriever.search(q)
    return SearchResponse(query=q, results=results, total=len(results))

class TemplatesResponse(BaseModel):
    templates: list
    total: int

@app.get("/api/templates", response_model=TemplatesResponse)
def list_templates(type: str = None):
    """获取模板列表"""
    try:
        filter_type = TemplateType(type) if type else None
        templates = template_manager.list_templates(filter_type)
        return TemplatesResponse(templates=templates, total=len(templates))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的类型参数: {type}. 有效类型为: {[t.value for t in TemplateType]}"
        )

class CreateTemplateRequest(BaseModel):
    name: str
    type: str
    description: str = ""

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """验证 type 是否为有效的 TemplateType"""
        try:
            TemplateType(v)
            return v
        except ValueError:
            valid_types = [t.value for t in TemplateType]
            raise ValueError(f"无效的类型: {v}. 有效类型为: {valid_types}")

@app.post("/api/templates")
def create_template(request: CreateTemplateRequest):
    """创建模板"""
    template = template_manager.create_template(
        name=request.name,
        template_type=TemplateType(request.type),
        description=request.description
    )
    return template.model_dump()

class RenderRequest(BaseModel):
    title: str
    content: str

@app.post("/api/templates/{template_id}/render")
def render_template(template_id: int, request: RenderRequest):
    """渲染模板"""
    template = template_manager.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    content = template_renderer.render(template, {
        "title": request.title,
        "content": request.content
    })
    return {"content": content}
