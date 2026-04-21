import logging
import os
from typing import Dict, List, Optional

from sirchmunk import AgenticSearch
from sirchmunk.llm import OpenAIChat

from src.core.config import settings

logger = logging.getLogger(__name__)


class GenerationContext:
    def __init__(
        self,
        query: str,
        evidence: str,
        patterns: List[str],
        confidence: float,
        source_files: List[str],
    ):
        self.query = query
        self.evidence = evidence
        self.patterns = patterns
        self.confidence = confidence
        self.source_files = source_files


class SirchmunkService:
    def __init__(self):
        llm = OpenAIChat(
            api_key=settings.SIRCHMUNK_LLM_API_KEY,
            base_url=settings.SIRCHMUNK_LLM_BASE_URL,
            model=settings.SIRCHMUNK_LLM_MODEL,
        )
        self.search = AgenticSearch(llm=llm)
        self.search_paths = settings.SIRCHMUNK_SEARCH_PATHS.split(",")

    async def search_documents(
        self,
        query: str,
        mode: str = "FAST",
        paths: Optional[List[str]] = None,
    ):
        search_paths = paths or self.search_paths
        try:
            result = await self.search.search(
                query=query,
                paths=search_paths,
                mode=mode,
            )
            return result
        except Exception as e:
            logger.error(f"Sirchmunk search failed: {e}")
            raise

    async def search_for_generation(
        self,
        topic: str,
        doc_type: str,
        reference_docs: Optional[List[str]] = None,
    ) -> GenerationContext:
        query = f"{doc_type}类公文 {topic} 相关内容要点和格式要求"

        if reference_docs:
            paths = [
                os.path.join(self.search_paths[0], doc)
                for doc in reference_docs
            ]
        else:
            paths = self.search_paths

        result = await self.search_documents(query=query, mode="DEEP", paths=paths)

        evidence = getattr(result, "content", "") or getattr(result, "answer", "") or str(result)
        patterns = getattr(result, "patterns", [])
        confidence = getattr(result, "confidence", 0.0)
        source_files = getattr(result, "source_files", [])

        return GenerationContext(
            query=query,
            evidence=evidence,
            patterns=patterns,
            confidence=confidence,
            source_files=source_files,
        )

    async def get_knowledge_clusters(self) -> List[Dict]:
        try:
            clusters = self.search.get_knowledge_clusters()
            return clusters if clusters else []
        except Exception:
            return []
