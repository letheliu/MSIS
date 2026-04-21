import logging

from src.search.sirchmunk_service import SirchmunkService
from src.llm.service import LLMService
from src.llm.prompts import PromptTemplates
from src.creation.orchestrator import CreationOrchestrator

logger = logging.getLogger(__name__)

_sirchmunk_service: SirchmunkService | None = None
_llm_service: LLMService | None = None
_creation_orchestrator: CreationOrchestrator | None = None


def get_sirchmunk_service() -> SirchmunkService:
    global _sirchmunk_service
    if _sirchmunk_service is None:
        try:
            _sirchmunk_service = SirchmunkService()
        except Exception as e:
            logger.warning(f"SirchmunkService init failed (LLM unavailable?): {e}")
            _sirchmunk_service = None
    return _sirchmunk_service


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def get_creation_orchestrator() -> CreationOrchestrator:
    global _creation_orchestrator
    if _creation_orchestrator is None:
        _creation_orchestrator = CreationOrchestrator(
            sirchmunk=get_sirchmunk_service(),
            llm=get_llm_service(),
            prompts=PromptTemplates,
        )
    return _creation_orchestrator
