import json
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.core.dependencies import get_creation_orchestrator
from src.creation.orchestrator import CreationOrchestrator
from src.creation.task_manager import TaskManager, GenerationTask

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/generation", tags=["generation"])

task_manager = TaskManager()


class CreateGenerationRequest(BaseModel):
    topic: str
    doc_type: str
    reference_docs: Optional[List[str]] = None
    parameters: Optional[dict] = None


class GenerationResponse(BaseModel):
    task_id: str


class GenerationResultResponse(BaseModel):
    task_id: str
    topic: str
    doc_type: str
    content: str
    sources: List[str] = []
    status: str
    error: Optional[str] = None


class GenerationHistoryItem(BaseModel):
    task_id: str
    topic: str
    doc_type: str
    status: str
    content: str = ""


class GenerationHistoryResponse(BaseModel):
    items: List[GenerationHistoryItem]
    total: int


async def _run_generation(
    task_id: str,
    orchestrator: CreationOrchestrator,
    request: CreateGenerationRequest,
):
    task = task_manager.get_task(task_id)
    if not task:
        return

    task.status = "generating"
    full_content = ""

    try:
        async for token in orchestrator.create_document(
            topic=request.topic,
            doc_type=request.doc_type,
            reference_docs=request.reference_docs,
            parameters=request.parameters,
        ):
            full_content += token
            await task_manager.put_token(task_id, token)

        task_manager.update_task(
            task_id,
            content=full_content,
            status="completed",
        )
    except Exception as e:
        logger.error(f"Generation failed for task {task_id}: {e}")
        task_manager.update_task(
            task_id,
            status="failed",
            error=str(e),
        )
    finally:
        await task_manager.finish_task(task_id)


@router.post("/create", response_model=GenerationResponse)
async def create_generation(
    request: CreateGenerationRequest,
    orchestrator: CreationOrchestrator = Depends(get_creation_orchestrator),
):
    task_id = task_manager.create_task(
        topic=request.topic,
        doc_type=request.doc_type,
        reference_docs=request.reference_docs,
        parameters=request.parameters,
    )

    import asyncio
    asyncio.create_task(_run_generation(task_id, orchestrator, request))

    return GenerationResponse(task_id=task_id)


@router.get("/{task_id}/stream")
async def stream_generation(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    async def event_stream():
        async for token in task_manager.stream_result(task_id):
            data = json.dumps({"token": token}, ensure_ascii=False)
            yield f"data: {data}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/{task_id}", response_model=GenerationResultResponse)
async def get_generation_result(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return GenerationResultResponse(
        task_id=task.task_id,
        topic=task.topic,
        doc_type=task.doc_type,
        content=task.content,
        sources=task.sources,
        status=task.status,
        error=task.error,
    )


@router.post("/{task_id}/optimize")
async def optimize_generation(
    task_id: str,
    orchestrator: CreationOrchestrator = Depends(get_creation_orchestrator),
):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if not task.content:
        raise HTTPException(status_code=400, detail="任务内容为空，无法优化")

    async def event_stream():
        async for token in orchestrator.optimize_document(
            content=task.content,
            doc_type=task.doc_type,
        ):
            data = json.dumps({"token": token}, ensure_ascii=False)
            yield f"data: {data}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/history", response_model=GenerationHistoryResponse)
async def get_generation_history():
    tasks = task_manager.list_tasks()
    items = [
        GenerationHistoryItem(
            task_id=t.task_id,
            topic=t.topic,
            doc_type=t.doc_type,
            status=t.status,
            content=t.content[:200] if t.content else "",
        )
        for t in reversed(tasks)
    ]
    return GenerationHistoryResponse(items=items, total=len(items))


@router.delete("/{task_id}")
async def delete_generation(task_id: str):
    success = task_manager.delete_task(task_id)
    if success:
        return {"success": True, "message": "任务已删除"}
    raise HTTPException(status_code=404, detail="任务不存在")
