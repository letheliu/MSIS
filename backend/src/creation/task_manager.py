import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from typing import AsyncIterator, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class GenerationTask:
    task_id: str
    topic: str
    doc_type: str
    reference_docs: List[str] = field(default_factory=list)
    parameters: Dict = field(default_factory=dict)
    status: str = "pending"
    content: str = ""
    sources: List[str] = field(default_factory=list)
    error: Optional[str] = None


class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, GenerationTask] = {}
        self._queues: Dict[str, asyncio.Queue] = {}

    def create_task(
        self,
        topic: str,
        doc_type: str,
        reference_docs: Optional[List[str]] = None,
        parameters: Optional[Dict] = None,
    ) -> str:
        task_id = str(uuid.uuid4())
        task = GenerationTask(
            task_id=task_id,
            topic=topic,
            doc_type=doc_type,
            reference_docs=reference_docs or [],
            parameters=parameters or {},
        )
        self.tasks[task_id] = task
        self._queues[task_id] = asyncio.Queue()
        return task_id

    async def stream_result(self, task_id: str) -> AsyncIterator[str]:
        queue = self._queues.get(task_id)
        if not queue:
            return

        while True:
            item = await queue.get()
            if item is None:
                break
            yield item

    async def put_token(self, task_id: str, token: str):
        queue = self._queues.get(task_id)
        if queue:
            await queue.put(token)

    async def finish_task(self, task_id: str):
        queue = self._queues.get(task_id)
        if queue:
            await queue.put(None)

    def update_task(
        self,
        task_id: str,
        content: str = "",
        sources: Optional[List[str]] = None,
        status: str = "completed",
        error: Optional[str] = None,
    ):
        task = self.tasks.get(task_id)
        if task:
            task.content = content
            task.status = status
            if sources is not None:
                task.sources = sources
            if error is not None:
                task.error = error

    def get_task(self, task_id: str) -> Optional[GenerationTask]:
        return self.tasks.get(task_id)

    def list_tasks(self) -> List[GenerationTask]:
        return list(self.tasks.values())

    def delete_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._queues.pop(task_id, None)
            return True
        return False
