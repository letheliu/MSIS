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
    assert indexer._is_supported_format(Path("test.pdf")) is True
    assert indexer._is_supported_format(Path("test.docx")) is True
    # 不支持的格式
    assert indexer._is_supported_format(Path("test.exe")) is False
    assert indexer._is_supported_format(Path("test.jpg")) is False

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

def test_remove_file(tmp_path):
    """测试从索引中移除文件"""
    output_dir = tmp_path / "indexed"
    output_dir.mkdir()
    (output_dir / "test.txt").write_text("test content", encoding="utf-8")

    indexer = DocumentIndexer(output_dir=str(output_dir))
    assert indexer.remove_file("test.txt") is True
    assert (output_dir / "test.txt").exists() is False
    # 移除不存在的文件应返回 False
    assert indexer.remove_file("nonexistent.txt") is False

def test_get_indexed_files(tmp_path):
    """测试获取已索引的文件列表"""
    output_dir = tmp_path / "indexed"
    output_dir.mkdir()
    (output_dir / "test1.txt").write_text("content1", encoding="utf-8")
    (output_dir / "test2.md").write_text("content2", encoding="utf-8")
    (output_dir / "subdir").mkdir()

    indexer = DocumentIndexer(output_dir=str(output_dir))
    files = indexer.get_indexed_files()

    assert len(files) == 2
    file_names = {f["name"] for f in files}
    assert "test1.txt" in file_names
    assert "test2.md" in file_names
    # 验证文件信息包含必需字段
    for f in files:
        assert "name" in f
        assert "size" in f
        assert "path" in f
