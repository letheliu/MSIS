import logging
import queue
import threading
from pathlib import Path
from typing import Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent

from .config import ConfigManager
from .parsers import DocumentParser, TextParser, DocxParser, PDFParser
from ..search.indexer import DocumentIndexer

logger = logging.getLogger(__name__)


class FileChangeHandler(FileSystemEventHandler):
    """文件变化处理器"""

    def __init__(self, task_queue: queue.Queue, document_path: Path, supported_formats: set):
        self.task_queue = task_queue
        self.document_path = document_path
        self.supported_formats = supported_formats

    def on_created(self, event: FileCreatedEvent):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in self.supported_formats:
                logger.info(f"检测到新文件: {file_path.name}")
                self.task_queue.put(("index", file_path))

    def on_modified(self, event: FileModifiedEvent):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in self.supported_formats:
                logger.info(f"检测到文件修改: {file_path.name}")
                self.task_queue.put(("index", file_path))

    def on_deleted(self, event: FileDeletedEvent):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in self.supported_formats:
                relative_path = file_path.relative_to(self.document_path) if file_path.is_relative_to(self.document_path) else file_path.name
                logger.info(f"检测到文件删除: {file_path.name}")
                self.task_queue.put(("remove", relative_path))


class DocumentLibrary:
    """文档库服务"""

    PARSERS: Dict[str, DocumentParser] = {
        '.txt': TextParser(),
        '.md': TextParser(),
        '.json': TextParser(),
        '.docx': DocxParser(),
        '.pdf': PDFParser(),
    }

    def __init__(self, config_path: str = "backend/config/document_library.json"):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()

        self.indexer = DocumentIndexer(output_dir=self.config["index_path"])
        self.supported_formats = set(self.config.get("supported_formats", []))

        self.observer: Optional[Observer] = None
        self.task_queue = queue.Queue()
        self.worker_thread: Optional[threading.Thread] = None
        self.running = False

    def start_file_watching(self):
        """启动文件监听"""
        if self.config.get("auto_reindex", False):
            document_path = Path(self.config["document_path"])
            document_path.mkdir(parents=True, exist_ok=True)

            event_handler = FileChangeHandler(
                self.task_queue,
                document_path,
                self.supported_formats
            )

            self.observer = Observer()
            self.observer.schedule(event_handler, str(document_path), recursive=True)
            self.observer.start()
            self.running = True

            # 启动工作线程处理任务
            self.worker_thread = threading.Thread(target=self._process_tasks, daemon=True)
            self.worker_thread.start()

            logger.info(f"文件监听已启动: {document_path}")

    def stop_file_watching(self):
        """停止文件监听"""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self.worker_thread:
            self.worker_thread.join(timeout=2)
        logger.info("文件监听已停止")

    def _process_tasks(self):
        """处理文件变化任务"""
        while self.running:
            try:
                task_type, file_path = self.task_queue.get(timeout=1)
                if task_type == "index":
                    self.index_file(Path(file_path))
                elif task_type == "remove":
                    self.indexer.remove_file(str(file_path))
            except queue.Empty:
                continue

    def index_file(self, file_path: Path) -> Dict:
        """索引单个文件"""
        if not file_path.exists():
            return {"success": False, "error": "文件不存在"}

        suffix = file_path.suffix.lower()
        if suffix not in self.supported_formats:
            return {"success": False, "error": f"不支持的文件格式: {suffix}"}

        try:
            parser = self.PARSERS.get(suffix, TextParser())
            content = parser.parse(file_path)

            # 复制到索引目录
            indexed_path = self.indexer._index_file(file_path)

            logger.info(f"文件索引成功: {file_path.name}")
            return {
                "success": True,
                "file_name": file_path.name,
                "indexed_path": indexed_path,
                "content_length": len(content)
            }
        except Exception as e:
            logger.error(f"索引文件失败 {file_path.name}: {str(e)}")
            return {"success": False, "error": str(e)}

    def reindex_all(self) -> Dict:
        """重新索引所有文件"""
        result = self.indexer.index_directory(self.config["document_path"])
        return result

    def get_indexed_files(self) -> List[Dict]:
        """获取已索引的文件列表"""
        return self.indexer.get_indexed_files()

    def update_config(self, updates: Dict) -> Dict:
        """更新配置"""
        self.config = self.config_manager.update_config(updates)
        self.supported_formats = set(self.config.get("supported_formats", []))
        return self.config

    def get_config(self) -> Dict:
        """获取当前配置"""
        return self.config
