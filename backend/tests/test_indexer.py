import pytest
from pathlib import Path
from src.search.indexer import DocumentIndexer

@pytest.fixture
def test_data_dir(tmp_path):
    """创建测试数据目录"""
    test_dir = tmp_path / "test_docs"
    test_dir.mkdir()
    (test_dir / "doc1.txt").write_text("这是一份测试公文文档", encoding="utf-8")
    (test_dir / "doc2.txt").write_text("关于军队建设的通知", encoding="utf-8")
    return test_dir

def test_indexer_init():
    """测试索引器初始化"""
    indexer = DocumentIndexer()
    assert indexer is not None

def test_index_documents(test_data_dir, tmp_path):
    """测试文档索引"""
    output_dir = tmp_path / "indexed"
    indexer = DocumentIndexer(output_dir=str(output_dir))
    result = indexer.index_directory(str(test_data_dir))
    assert result["total"] == 2
    assert result["success"] >= 0
