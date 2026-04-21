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
