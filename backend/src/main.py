import logging
from pathlib import Path
from typing import Dict, List, Optional
import shutil

# 配置日志
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "document_index.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

from fastapi import FastAPI, Query, HTTPException, status, UploadFile, File
from pydantic import BaseModel, field_validator
from src.search.retriever import DocumentRetriever
from src.search.indexer import DocumentIndexer
from src.templates.manager import TemplateManager
from src.templates.renderer import TemplateRenderer
from src.templates.models import TemplateType, Template
from src.documents.library import DocumentLibrary

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

# 文档库服务
document_library = DocumentLibrary()

@app.on_event("startup")
async def startup_event():
    """启动事件：初始化文档库"""
    document_library.start_file_watching()
    # 启动时执行一次完整索引
    result = document_library.reindex_all()
    print(f"文档索引完成: {result['success']}/{result['total']} 文件")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件：停止文件监听"""
    document_library.stop_file_watching()

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

# ============ 文档库相关 ============

class ConfigResponse(BaseModel):
    document_path: str
    index_path: str
    auto_reindex: bool
    supported_formats: List[str]

@app.get("/api/documents/config", response_model=ConfigResponse)
def get_document_config():
    """获取文档库配置"""
    config = document_library.get_config()
    return ConfigResponse(**config)

class UpdateConfigRequest(BaseModel):
    document_path: Optional[str] = None
    auto_reindex: Optional[bool] = None

@app.put("/api/documents/config", response_model=ConfigResponse)
def update_document_config(request: UpdateConfigRequest):
    """更新文档库配置"""
    updates = request.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="没有提供需要更新的配置")

    config = document_library.update_config(updates)
    return ConfigResponse(**config)

class UploadResponse(BaseModel):
    success: bool
    file_name: str
    message: str
    indexed_path: Optional[str] = None
    error: Optional[str] = None

@app.post("/api/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """上传文档到文档库"""
    config = document_library.get_config()
    document_path = Path(config["document_path"])
    document_path.mkdir(parents=True, exist_ok=True)

    # 验证文件格式
    file_suffix = Path(file.filename).suffix.lower()
    if file_suffix not in config["supported_formats"]:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {file_suffix}. 支持的格式: {', '.join(config['supported_formats'])}"
        )

    # 保存文件
    save_path = document_path / file.filename
    # 避免文件名冲突
    counter = 1
    original_save_path = save_path
    while save_path.exists():
        name_without_ext = original_save_path.stem
        save_path = document_path / f"{name_without_ext}_{counter}{file_suffix}"
        counter += 1

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    # 触发索引
    result = document_library.index_file(save_path)

    if result["success"]:
        return UploadResponse(
            success=True,
            file_name=save_path.name,
            message="文件上传并索引成功",
            indexed_path=result.get("indexed_path")
        )
    else:
        return UploadResponse(
            success=False,
            file_name=save_path.name,
            message="文件上传成功但索引失败",
            error=result.get("error")
        )

class DocumentItem(BaseModel):
    name: str
    size: int
    path: str

class DocumentsListResponse(BaseModel):
    documents: List[DocumentItem]
    total: int

@app.get("/api/documents/list", response_model=DocumentsListResponse)
def list_documents():
    """获取已索引的文档列表"""
    files = document_library.get_indexed_files()
    return DocumentsListResponse(
        documents=[DocumentItem(**f) for f in files],
        total=len(files)
    )

class ReindexResponse(BaseModel):
    total: int
    success: int
    errors: List[str] = []

@app.post("/api/documents/reindex", response_model=ReindexResponse)
def reindex_documents():
    """手动触发重新索引"""
    result = document_library.reindex_all()
    return ReindexResponse(**result)

@app.delete("/api/documents/{file_name}")
def delete_document(file_name: str):
    """删除已索引的文档"""
    success = document_library.indexer.remove_file(file_name)
    if success:
        return {"success": True, "message": "文档删除成功"}
    raise HTTPException(status_code=404, detail="文档不存在")
