import logging
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

from src.documents.library import DocumentLibrary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

document_library = DocumentLibrary()


class ConfigResponse(BaseModel):
    document_path: str
    index_path: str
    auto_reindex: bool
    supported_formats: List[str]


class UpdateConfigRequest(BaseModel):
    document_path: Optional[str] = None
    auto_reindex: Optional[bool] = None


class UploadResponse(BaseModel):
    success: bool
    file_name: str
    message: str
    indexed_path: Optional[str] = None
    error: Optional[str] = None


class DocumentItem(BaseModel):
    name: str
    size: int
    path: str


class DocumentsListResponse(BaseModel):
    documents: List[DocumentItem]
    total: int


class ReindexResponse(BaseModel):
    total: int
    success: int
    errors: List[str] = []


@router.get("/config", response_model=ConfigResponse)
def get_document_config():
    config = document_library.get_config()
    return ConfigResponse(**config)


@router.put("/config", response_model=ConfigResponse)
def update_document_config(request: UpdateConfigRequest):
    updates = request.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="没有提供需要更新的配置")
    config = document_library.update_config(updates)
    return ConfigResponse(**config)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    config = document_library.get_config()
    document_path = Path(config["document_path"])
    document_path.mkdir(parents=True, exist_ok=True)

    file_suffix = Path(file.filename).suffix.lower()
    if file_suffix not in config["supported_formats"]:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {file_suffix}. 支持的格式: {', '.join(config['supported_formats'])}"
        )

    save_path = document_path / file.filename
    counter = 1
    original_save_path = save_path
    while save_path.exists():
        name_without_ext = original_save_path.stem
        save_path = document_path / f"{name_without_ext}_{counter}{file_suffix}"
        counter += 1

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

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


@router.get("/list", response_model=DocumentsListResponse)
def list_documents():
    files = document_library.get_indexed_files()
    return DocumentsListResponse(
        documents=[DocumentItem(**f) for f in files],
        total=len(files)
    )


@router.post("/reindex", response_model=ReindexResponse)
def reindex_documents():
    result = document_library.reindex_all()
    return ReindexResponse(**result)


@router.delete("/{file_name}")
def delete_document(file_name: str):
    success = document_library.indexer.remove_file(file_name)
    if success:
        return {"success": True, "message": "文档删除成功"}
    raise HTTPException(status_code=404, detail="文档不存在")
