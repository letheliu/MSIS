import logging
from typing import AsyncIterator, Dict, List, Optional

from src.search.sirchmunk_service import SirchmunkService
from src.llm.service import LLMService
from src.llm.prompts import PromptTemplates

logger = logging.getLogger(__name__)


class CreationOrchestrator:
    def __init__(
        self,
        sirchmunk: SirchmunkService,
        llm: LLMService,
        prompts: type,
    ):
        self.sirchmunk = sirchmunk
        self.llm = llm
        self.prompts = prompts

    async def create_document(
        self,
        topic: str,
        doc_type: str,
        reference_docs: Optional[List[str]] = None,
        parameters: Optional[Dict] = None,
    ) -> AsyncIterator[str]:
        params = parameters or {}
        word_count = params.get("word_count", 800)
        style = params.get("style", "正式")

        context_text = ""
        source_files: List[str] = []

        if self.sirchmunk:
            try:
                ctx = await self.sirchmunk.search_for_generation(
                    topic=topic,
                    doc_type=doc_type,
                    reference_docs=reference_docs,
                )
                context_text = ctx.evidence
                source_files = ctx.source_files
            except Exception as e:
                logger.warning(f"Sirchmunk search failed, proceeding without context: {e}")
                context_text = "（未获取到参考文档，请基于通用知识撰写）"
        else:
            context_text = "（Sirchmunk服务不可用，请基于通用知识撰写）"

        prompt = self.prompts.build_generation_prompt(
            doc_type=doc_type,
            topic=topic,
            context=context_text,
            word_count=word_count,
            style=style,
        )

        async for token in self.llm.stream_generate(
            prompt=prompt,
            system_prompt=self.prompts.SYSTEM_PROMPT,
            max_tokens=word_count * 2,
            temperature=0.7,
        ):
            yield token

    async def optimize_document(
        self,
        content: str,
        doc_type: str,
    ) -> AsyncIterator[str]:
        prompt = self.prompts.build_optimization_prompt(
            content=content,
            doc_type=doc_type,
        )
        async for token in self.llm.stream_generate(
            prompt=prompt,
            temperature=0.5,
        ):
            yield token
