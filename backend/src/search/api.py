import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.core.dependencies import get_sirchmunk_service
from src.search.sirchmunk_service import SirchmunkService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"])


class SearchResultItem(BaseModel):
    title: str = ""
    content: str = ""
    source: str = ""
    score: float = 0.0


class SearchResponse(BaseModel):
    query: str
    mode: str
    results: List[SearchResultItem]
    total: int


@router.get("/api/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    mode: str = Query("FAST", description="检索模式: FAST/DEEP/FILENAME_ONLY"),
    sirchmunk: SirchmunkService = Depends(get_sirchmunk_service),
):
    if not sirchmunk:
        raise HTTPException(
            status_code=503,
            detail="检索服务不可用（Sirchmunk初始化失败，请检查LLM配置）",
        )

    try:
        result = await sirchmunk.search_documents(query=q, mode=mode)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"检索失败: {e}")

    items = []
    if hasattr(result, "results") and result.results:
        for r in result.results:
            items.append(SearchResultItem(
                title=getattr(r, "title", ""),
                content=getattr(r, "content", "")[:500],
                source=getattr(r, "source", getattr(r, "file", "")),
                score=getattr(r, "score", 0.0),
            ))
    elif hasattr(result, "content"):
        items.append(SearchResultItem(
            content=str(result.content)[:500],
            source=str(getattr(result, "source_files", [])),
        ))

    return SearchResponse(query=q, mode=mode, results=items, total=len(items))
