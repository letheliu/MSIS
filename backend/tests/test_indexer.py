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
    assert result["success"] == 2
    assert len(result["errors"]) == 0
    # 验证文件确实被复制
    assert (output_dir / "doc1.txt").exists()
    assert (output_dir / "doc2.txt").exists()

def test_is_supported_format():
    """测试支持的格式检查"""
    indexer = DocumentIndexer()
    assert indexer._is_supported_format(Path("test.txt")) is True
    assert indexer._is_supported_format(Path("test.md")) is True
    assert indexer._is_supported_format(Path("test.json")) is True
    assert indexer._is_supported_format(Path("test.pdf")) is False
    assert indexer._is_supported_format(Path("test.docx")) is False

def test_index_directory_not_exists(tmp_path):
    """测试目录不存在的情况"""
    output_dir = tmp_path / "indexed"
    indexer = DocumentIndexer(output_dir=str(output_dir))
    result = indexer.index_directory(str(tmp_path / "nonexistent"))
    assert "error" in result
    assert result["error"] == "目录不存在"
    assert result["total"] == 0
    assert result["success"] == 0

def test_file_overwrite_prevention(test_data_dir, tmp_path):
    """测试文件覆盖预防"""
    output_dir = tmp_path / "indexed"
    output_dir.mkdir()
    # 预先创建同名文件
    (output_dir / "doc1.txt").write_text("existing content", encoding="utf-8")

    indexer = DocumentIndexer(output_dir=str(output_dir))
    result = indexer.index_directory(str(test_data_dir))

    assert result["success"] == 2
    # 原文件应保持不变
    assert (output_dir / "doc1.txt").read_text(encoding="utf-8") == "existing content"
    # 应该创建带后缀的新文件
    assert (output_dir / "doc1_1.txt").exists()
    assert (output_dir / "doc2.txt").exists()
