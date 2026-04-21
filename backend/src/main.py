import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.documents.api import router as documents_router, document_library
from src.templates.api import router as templates_router
from src.search.api import router as search_router
from src.creation.api import router as creation_router

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "document_index.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MSIS Backend starting...")
    document_library.start_file_watching()
    result = document_library.reindex_all()
    logger.info(f"文档索引完成: {result['success']}/{result['total']} 文件")
    yield
    logger.info("MSIS Backend shutting down...")
    document_library.stop_file_watching()


app = FastAPI(title="MSIS API", version="0.0.1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(templates_router)
app.include_router(search_router)
app.include_router(creation_router)


@app.get("/")
def root():
    return {"message": "MSIS - Military Document Writing Assistant API"}


@app.get("/health")
def health():
    return {"status": "ok"}
