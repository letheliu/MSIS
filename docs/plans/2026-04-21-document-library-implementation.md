# Document Library Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enhance MSIS document library to support docx/pdf formats, configurable storage path, and dynamic file watching without backend restart.

**Architecture:** Backend DocumentLibrary service with watchdog for file watching, parser pattern for different formats, and new API endpoints. Frontend Documents.vue page for configuration and upload management.

**Tech Stack:** Python 3.11, FastAPI, watchdog, python-docx, pdfplumber; Vue 3, Element Plus, axios

---

## Task 1: Add Required Dependencies

**Files:**
- Create: `backend/requirements.txt` (if not exists)
- Modify: `backend/requirements.txt` (append)

**Step 1: Check if requirements.txt exists**

Run: `ls backend/requirements.txt`
Expected: File may not exist

**Step 2: Add required dependencies**

Create or append to `backend/requirements.txt`:
```txt
fastapi==0.136.0
uvicorn[standard]==0.44.0
pydantic==2.10.0
python-multipart==0.0.26
watchdog==5.0.0
python-docx==1.2.0
pdfplumber==0.11.0
aiofiles==24.1.0
```

**Step 3: Install dependencies**

Run: `cd backend && pip install -r requirements.txt`
Expected: All packages installed successfully

**Step 4: Commit**

```bash
git add backend/requirements.txt
git commit -m "chore: add document library dependencies (watchdog, pdfplumber)"
```

---

## Task 2: Create Document Parser Interface and Implementations

**Files:**
- Create: `backend/src/documents/parsers.py`
- Test: `backend/tests/test_parsers.py`

**Step 1: Create test file for parsers**

Create `backend/tests/test_parsers.py`:
```python
import pytest
from pathlib import Path
from src.documents.parsers import TextParser, DocxParser, PDFParser

def test_text_parser_txt():
    """Test parsing txt files"""
    parser = TextParser()
    content = parser.parse(Path("backend/data/sample_docs/命令_训练计划.txt"))
    assert isinstance(content, str)
    assert len(content) > 0
    assert "训练" in content

def test_text_parser_md():
    """Test parsing markdown files"""
    parser = TextParser()
    test_file = Path("backend/test_data/test.md")
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text("# 标题\n\n内容\n")
    content = parser.parse(test_file)
    assert "# 标题" in content
    test_file.unlink()

def test_text_parser_json():
    """Test parsing JSON files"""
    parser = TextParser()
    test_file = Path("backend/test_data/test.json")
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text('{"key": "value", "nested": {"text": "hello"}}')
    content = parser.parse(test_file)
    assert "value" in content
    assert "hello" in content
    test_file.unlink()
```

**Step 2: Run tests to verify they fail**

Run: `cd backend && pytest tests/test_parsers.py -v`
Expected: FAIL with "No module named 'src.documents.parsers'"

**Step 3: Create documents directory and parsers module**

Create `backend/src/documents/__init__.py`:
```python
from .parsers import DocumentParser, TextParser, DocxParser, PDFParser

__all__ = ['DocumentParser', 'TextParser', 'DocxParser', 'PDFParser']
```

**Step 4: Implement parsers**

Create `backend/src/documents/parsers.py`:
```python
from abc import ABC, abstractmethod
from pathlib import Path
import json
from docx import Document
import pdfplumber


class DocumentParser(ABC):
    """文档解析器抽象基类"""

    @abstractmethod
    def parse(self, file_path: Path) -> str:
        """解析文档并返回格式化文本"""
        pass


class TextParser(DocumentParser):
    """文本文件解析器 (txt, md, json)"""

    def parse(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()

        if suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return self._extract_json_strings(data)

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _extract_json_strings(self, data) -> str:
        """递归提取 JSON 中的所有字符串值"""
        if isinstance(data, str):
            return data
        elif isinstance(data, dict):
            return ' '.join(self._extract_json_strings(v) for v in data.values())
        elif isinstance(data, list):
            return ' '.join(self._extract_json_strings(item) for item in data)
        return ''


class DocxParser(DocumentParser):
    """Word 文档解析器"""

    def parse(self, file_path: Path) -> str:
        doc = Document(file_path)
        content = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # 检查样式是否为标题
            if para.style.name.startswith('Heading'):
                level = para.style.name.replace('Heading ', '')
                hashes = '#' * min(int(level) + 1, 6)
                content.append(f"{hashes} {text}")
            else:
                content.append(text)

        # 处理表格
        for table in doc.tables:
            content.append("")
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                content.append(" | ".join(cells))
            content.append("")

        return "\n".join(content)


class PDFParser(DocumentParser):
    """PDF 文档解析器"""

    def parse(self, file_path: Path) -> str:
        content = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    content.append(text)

                # 尝试提取表格
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        content.append("")
                        for row in table:
                            cells = [str(cell).strip() if cell else "" for cell in row]
                            content.append(" | ".join(cells))
                        content.append("")

        return "\n".join(content)
```

**Step 5: Run tests to verify they pass**

Run: `cd backend && pytest tests/test_parsers.py -v`
Expected: PASS for all tests

**Step 6: Commit**

```bash
git add backend/src/documents/ backend/tests/test_parsers.py
git commit -m "feat: add document parsers for txt/md/json/docx/pdf"
```

---

## Task 3: Create Configuration Manager

**Files:**
- Create: `backend/src/documents/config.py`
- Create: `backend/config/document_library.json`
- Test: `backend/tests/test_config.py`

**Step 1: Write failing test**

Create `backend/tests/test_config.py`:
```python
import pytest
import json
from pathlib import Path
from src.documents.config import ConfigManager

def test_config_manager_load_default():
    """测试加载默认配置"""
    config_file = Path("backend/config/document_library.json")
    if config_file.exists():
        config_file.unlink()

    manager = ConfigManager()
    config = manager.load_config()

    assert config["document_path"] == "./data/sample_docs"
    assert config["index_path"] == "./data/indexed"
    assert config["auto_reindex"] is True
    assert ".txt" in config["supported_formats"]

def test_config_manager_update_path():
    """测试更新配置"""
    manager = ConfigManager()
    new_path = "./custom_docs"
    manager.update_config({"document_path": new_path})

    config = manager.load_config()
    assert config["document_path"] == new_path

    # 恢复默认
    manager.update_config({"document_path": "./data/sample_docs"})
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_config.py -v`
Expected: FAIL with "No module named 'src.documents.config'"

**Step 3: Create config directory and default config**

Create `backend/config/document_library.json`:
```json
{
  "document_path": "./data/sample_docs",
  "index_path": "./data/indexed",
  "auto_reindex": true,
  "supported_formats": [".txt", ".md", ".json", ".docx", ".pdf"]
}
```

**Step 4: Implement ConfigManager**

Create `backend/src/documents/config.py`:
```python
import json
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """文档库配置管理器"""

    DEFAULT_CONFIG = {
        "document_path": "./data/sample_docs",
        "index_path": "./data/indexed",
        "auto_reindex": True,
        "supported_formats": [".txt", ".md", ".json", ".docx", ".pdf"]
    }

    def __init__(self, config_path: str = "backend/config/document_library.json"):
        self.config_path = Path(config_path)

    def load_config(self) -> Dict[str, Any]:
        """加载配置，如果不存在则创建默认配置"""
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 确保所有默认字段都存在
                for key, value in self.DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except (json.JSONDecodeError, IOError):
            return self.DEFAULT_CONFIG.copy()

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新配置"""
        config = self.load_config()
        config.update(updates)
        self._save_config(config)
        return config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
```

**Step 5: Run test to verify it passes**

Run: `cd backend && pytest tests/test_config.py -v`
Expected: PASS for all tests

**Step 6: Commit**

```bash
git add backend/src/documents/config.py backend/config/document_library.json backend/tests/test_config.py
git commit -m "feat: add configuration manager for document library"
```

---

## Task 4: Create Enhanced Document Indexer

**Files:**
- Modify: `backend/src/search/indexer.py`
- Test: `backend/tests/test_indexer.py`

**Step 1: Write failing test for new formats**

Create `backend/tests/test_indexer.py`:
```python
import pytest
from pathlib import Path
from src.search.indexer import DocumentIndexer

def test_indexer_supports_docx():
    """测试索引器支持 docx 格式"""
    indexer = DocumentIndexer(output_dir="./test_output")
    docx_path = Path("test.docx")
    assert indexer._is_supported_format(docx_path) is True

def test_indexer_supports_pdf():
    """测试索引器支持 pdf 格式"""
    indexer = DocumentIndexer(output_dir="./test_output")
    pdf_path = Path("test.pdf")
    assert indexer._is_supported_format(pdf_path) is True
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_indexer.py -v`
Expected: FAIL (docx and pdf not in supported formats)

**Step 3: Update indexer to support new formats**

Modify `backend/src/search/indexer.py`:
```python
from pathlib import Path
from typing import Dict, List
import shutil
import logging

logger = logging.getLogger(__name__)

class DocumentIndexer:
    """文档索引器"""

    def __init__(self, output_dir: str = "./data/indexed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.supported_formats = {'.txt', '.md', '.json', '.docx', '.pdf'}

    def index_directory(self, dir_path: str) -> Dict:
        """索引指定目录下的所有文档"""
        dir_path = Path(dir_path)
        if not dir_path.exists():
            return {"error": "目录不存在", "total": 0, "success": 0}

        total = 0
        success = 0
        errors = []

        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and self._is_supported_format(file_path):
                total += 1
                try:
                    self._index_file(file_path)
                    success += 1
                    logger.info(f"索引成功: {file_path.name}")
                except (IOError, PermissionError, OSError) as e:
                    error_msg = f"索引文件失败 {file_path.name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

        logger.info(f"索引完成: 总计 {total}, 成功 {success}, 失败 {len(errors)}")
        return {"total": total, "success": success, "errors": errors}

    def _is_supported_format(self, file_path: Path) -> bool:
        """检查是否支持的格式"""
        return file_path.suffix.lower() in self.supported_formats

    def _index_file(self, file_path: Path) -> str:
        """索引单个文件，返回目标文件路径"""
        target = self.output_dir / file_path.name

        # 避免文件覆盖
        counter = 1
        original_target = target
        while target.exists():
            target = original_target.with_name(f"{original_target.stem}_{counter}{original_target.suffix}")
            counter += 1

        # 复制文件
        shutil.copy2(file_path, target)
        return str(target)

    def remove_file(self, file_name: str) -> bool:
        """从索引中移除文件"""
        target = self.output_dir / file_name
        if target.exists():
            target.unlink()
            logger.info(f"从索引中移除: {file_name}")
            return True
        return False

    def get_indexed_files(self) -> List[Dict]:
        """获取已索引的文件列表"""
        files = []
        for file_path in self.output_dir.glob("*"):
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "path": str(file_path)
                })
        return files
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_indexer.py -v`
Expected: PASS for all tests

**Step 5: Commit**

```bash
git add backend/src/search/indexer.py backend/tests/test_indexer.py
git commit -m "feat: enhance indexer with new formats and management methods"
```

---

## Task 5: Create Document Library Service with File Watching

**Files:**
- Create: `backend/src/documents/library.py`
- Test: `backend/tests/test_library.py`

**Step 1: Write failing test for DocumentLibrary**

Create `backend/tests/test_library.py`:
```python
import pytest
import time
from pathlib import Path
from src.documents.library import DocumentLibrary

def test_document_library_initialization():
    """测试文档库初始化"""
    library = DocumentLibrary(config_path="backend/config/document_library.json")
    assert library.indexer is not None
    assert library.config_manager is not None

def test_document_library_index_file():
    """测试索引单个文件"""
    library = DocumentLibrary(config_path="backend/config/document_library.json")
    test_file = Path("backend/data/sample_docs/命令_训练计划.txt")
    if test_file.exists():
        result = library.index_file(test_file)
        assert result["success"] is True

def test_document_library_get_indexed_files():
    """测试获取已索引文件列表"""
    library = DocumentLibrary(config_path="backend/config/document_library.json")
    files = library.get_indexed_files()
    assert isinstance(files, list)
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_library.py -v`
Expected: FAIL with "No module named 'src.documents.library'"

**Step 3: Implement DocumentLibrary service**

Create `backend/src/documents/library.py`:
```python
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
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_library.py -v`
Expected: PASS for all tests

**Step 5: Commit**

```bash
git add backend/src/documents/library.py backend/tests/test_library.py
git commit -m "feat: add DocumentLibrary service with file watching"
```

---

## Task 6: Add API Endpoints for Document Library

**Files:**
- Modify: `backend/src/main.py`

**Step 1: Add DocumentLibrary instance and endpoints**

Modify `backend/src/main.py`:
```python
from pathlib import Path
from typing import Dict, List, Optional
import shutil

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

# ============ 搜索相关 ============

class SearchResponse(BaseModel):
    query: str
    results: list
    total: int

@app.get("/api/search", response_model=SearchResponse)
def search(q: str = Query(..., min_length=1, description="搜索关键词")):
    """搜索公文文档"""
    results = retriever.search(q)
    return SearchResponse(query=q, results=results, total=len(results))

# ============ 模板相关 ============

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
```

**Step 2: Run backend to verify endpoints work**

Run: `cd backend && python -m uvicorn src.main:app --reload`
Expected: Server starts without errors

**Step 3: Commit**

```bash
git add backend/src/main.py
git commit -m "feat: add document library API endpoints"
```

---

## Task 7: Create Frontend Documents.vue Page

**Files:**
- Create: `frontend/src/views/Documents.vue`

**Step 1: Create Documents.vue page**

Create `frontend/src/views/Documents.vue`:
```vue
<template>
  <div class="documents-page">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>文档库配置</span>
        </div>
      </template>
      <el-form :model="configForm" label-width="120px">
        <el-form-item label="文档库路径">
          <el-input v-model="configForm.document_path" placeholder="文档库存储路径" />
        </el-form-item>
        <el-form-item label="自动索引">
          <el-switch v-model="configForm.auto_reindex" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="updateConfig">更新配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>上传文档</span>
        </div>
      </template>
      <el-upload
        ref="uploadRef"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        :file-list="fileList"
        :auto-upload="false"
        drag
        multiple
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持格式: .txt, .md, .json, .docx, .pdf
          </div>
        </template>
      </el-upload>
      <div style="margin-top: 16px;">
        <el-button type="primary" @click="startUpload">开始上传</el-button>
        <el-button @click="clearFiles">清空列表</el-button>
      </div>
    </el-card>

    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>已索引文档</span>
          <el-button type="primary" size="small" @click="refreshDocuments" :loading="loading">
            <el-icon><refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>
      <el-table :data="documents" style="width: 100%">
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="deleteDocument(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="documents.length === 0" class="empty-tip">
        暂无已索引文档
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

const configForm = ref({
  document_path: '',
  auto_reindex: true
})

const documents = ref([])
const loading = ref(false)
const uploadUrl = `${API_BASE}/api/documents/upload`
const uploadHeaders = {}
const uploadRef = ref(null)
const fileList = ref([])

// 获取配置
const fetchConfig = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/documents/config`)
    configForm.value = {
      document_path: response.data.document_path,
      auto_reindex: response.data.auto_reindex
    }
  } catch (error) {
    ElMessage.error('获取配置失败')
  }
}

// 更新配置
const updateConfig = async () => {
  try {
    await axios.put(`${API_BASE}/api/documents/config`, configForm.value)
    ElMessage.success('配置更新成功')
  } catch (error) {
    ElMessage.error('配置更新失败')
  }
}

// 获取文档列表
const fetchDocuments = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/api/documents/list`)
    documents.value = response.data.documents
  } catch (error) {
    ElMessage.error('获取文档列表失败')
  } finally {
    loading.value = false
  }
}

// 刷新文档列表
const refreshDocuments = async () => {
  await fetchDocuments()
  ElMessage.success('刷新成功')
}

// 上传前验证
const beforeUpload = (file) => {
  const allowedTypes = ['.txt', '.md', '.json', '.docx', '.pdf']
  const fileName = file.name.toLowerCase()
  const isValid = allowedTypes.some(type => fileName.endsWith(type))
  if (!isValid) {
    ElMessage.error('只支持 .txt, .md, .json, .docx, .pdf 格式的文件')
    return false
  }
  return true
}

// 开始上传
const startUpload = () => {
  uploadRef.value?.submit()
}

// 上传成功
const handleUploadSuccess = (response, file) => {
  if (response.success) {
    ElMessage.success(`上传成功: ${file.name}`)
    fetchDocuments()
  } else {
    ElMessage.error(`上传失败: ${file.name} - ${response.error || '未知错误'}`)
  }
}

// 上传失败
const handleUploadError = (error, file) => {
  ElMessage.error(`上传失败: ${file.name}`)
}

// 清空文件列表
const clearFiles = () => {
  fileList.value = []
}

// 删除文档
const deleteDocument = async (doc) => {
  try {
    await ElMessage.info('删除功能需要后端 API 支持')
    // TODO: 实现删除 API 调用
    // await axios.delete(`${API_BASE}/api/documents/${doc.name}`)
    // fetchDocuments()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 格式化文件大小
const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

onMounted(() => {
  fetchConfig()
  fetchDocuments()
})
</script>

<style scoped>
.documents-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.config-card,
.upload-card,
.list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.empty-tip {
  text-align: center;
  padding: 40px;
  color: #909399;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>
```

**Step 2: Commit**

```bash
git add frontend/src/views/Documents.vue
git commit -m "feat: add Documents page with config and upload"
```

---

## Task 8: Add Router Entry for Documents Page

**Files:**
- Modify: `frontend/src/router/index.js`

**Step 1: Add route for Documents page**

Modify `frontend/src/router/index.js`:
```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue')
  },
  {
    path: '/templates',
    name: 'Templates',
    component: () => import('../views/Templates.vue')
  },
  {
    path: '/templates/:id/edit',
    name: 'TemplateEditor',
    component: () => import('../views/TemplateEditor.vue')
  },
  {
    path: '/documents',
    name: 'Documents',
    component: () => import('../views/Documents.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

**Step 2: Update App.vue navigation**

Modify `frontend/src/App.vue`:
```vue
<template>
  <div id="app">
    <el-container>
      <el-header class="header">
        <h1>MSIS - 内网军队公文写作助手</h1>
        <el-menu
          :default-active="$route.path"
          mode="horizontal"
          background-color="#409EFF"
          text-color="#ffffff"
          active-text-color="#ffd04b"
          class="nav-menu"
          router
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/search">检索</el-menu-item>
          <el-menu-item index="/templates">模板库</el-menu-item>
          <el-menu-item index="/documents">文档库</el-menu-item>
        </el-menu>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
</script>

<style scoped>
.header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}
.header h1 {
  margin: 0 20px 0 0;
  font-size: 20px;
  white-space: nowrap;
}
.nav-menu {
  border: none;
  flex: 1;
}
.nav-menu.el-menu--horizontal {
  border-bottom: none;
}
</style>
```

**Step 3: Commit**

```bash
git add frontend/src/router/index.js frontend/src/App.vue
git commit -m "feat: add Documents page to navigation"
```

---

## Task 9: Add Delete Document API Endpoint

**Files:**
- Modify: `backend/src/main.py`

**Step 1: Add delete endpoint**

Add this to `backend/src/main.py` in the document library section:
```python
@app.delete("/api/documents/{file_name}")
def delete_document(file_name: str):
    """删除已索引的文档"""
    success = document_library.indexer.remove_file(file_name)
    if success:
        return {"success": True, "message": "文档删除成功"}
    raise HTTPException(status_code=404, detail="文档不存在")
```

**Step 2: Commit**

```bash
git add backend/src/main.py
git commit -m "feat: add delete document API endpoint"
```

---

## Task 10: Integrate Frontend Delete Function

**Files:**
- Modify: `frontend/src/views/Documents.vue`

**Step 1: Update delete function**

Replace the `deleteDocument` function in `frontend/src/views/Documents.vue`:
```javascript
// 删除文档
const deleteDocument = async (doc) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${doc.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await axios.delete(`${API_BASE}/api/documents/${encodeURIComponent(doc.name)}`)
    ElMessage.success('删除成功')
    fetchDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
```

Add import at top of script:
```javascript
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'
```

**Step 2: Commit**

```bash
git add frontend/src/views/Documents.vue
git commit -m "feat: integrate delete document functionality"
```

---

## Task 11: Add Logging Configuration

**Files:**
- Modify: `backend/src/main.py`

**Step 1: Add logging setup**

Add at the top of `backend/src/main.py`:
```python
import logging
from pathlib import Path
from typing import Dict, List, Optional
import shutil

# 配置日志
log_dir = Path("backend/logs")
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
...
```

**Step 2: Commit**

```bash
git add backend/src/main.py
git commit -m "feat: add logging configuration"
```

---

## Task 12: Final Integration Test

**Files:**
- Test: Verify full workflow

**Step 1: Start backend**

Run: `cd backend && python -m uvicorn src.main:app --reload`
Expected: Server starts on http://localhost:8000

**Step 2: Start frontend**

Run: `cd frontend && npm run dev`
Expected: Frontend starts

**Step 3: Test workflow**

1. Navigate to http://localhost:5173/documents
2. Verify config is displayed
3. Upload a test file (txt, docx, or pdf)
4. Verify file appears in list
5. Test refresh button
6. Test delete functionality

**Step 4: Commit final changes**

```bash
git add -A
git commit -m "test: verify document library integration complete"
```

---

## Verification Checklist

- [ ] All dependencies installed (watchdog, pdfplumber, python-docx)
- [ ] All parser tests pass
- [ ] Config manager tests pass
- [ ] Indexer tests pass
- [ ] DocumentLibrary tests pass
- [ ] Backend starts without errors
- [ ] All API endpoints respond correctly:
  - GET /api/documents/config
  - PUT /api/documents/config
  - POST /api/documents/upload
  - GET /api/documents/list
  - POST /api/documents/reindex
  - DELETE /api/documents/{file_name}
- [ ] Frontend Documents page loads
- [ ] File upload works (drag and drop)
- [ ] Document list displays correctly
- [ ] Delete functionality works
- [ ] File watching triggers automatic indexing
- [ ] Logging is written to backend/logs/document_index.log
