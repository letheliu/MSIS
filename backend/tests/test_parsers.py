import pytest
from pathlib import Path
from src.documents.parsers import TextParser, DocxParser, PDFParser

# Base directory for test resources
BASE_DIR = Path(__file__).parent.parent / "data"

def test_text_parser_txt():
    """Test parsing txt files"""
    parser = TextParser()
    content = parser.parse(BASE_DIR / "sample_docs" / "命令_训练计划.txt")
    assert isinstance(content, str)
    assert len(content) > 0
    assert "训练" in content

def test_text_parser_md():
    """Test parsing markdown files"""
    parser = TextParser()
    test_file = Path(__file__).parent.parent / "test_data" / "test.md"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("# 标题\n\n内容\n", encoding="utf-8")
    content = parser.parse(test_file)
    assert "# 标题" in content
    test_file.unlink()

def test_text_parser_json():
    """Test parsing JSON files"""
    parser = TextParser()
    test_file = Path(__file__).parent.parent / "test_data" / "test.json"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text('{"key": "value", "nested": {"text": "hello"}}')
    content = parser.parse(test_file)
    assert "value" in content
    assert "hello" in content
    test_file.unlink()


def test_text_parser_file_not_found():
    """Test TextParser raises error for missing file"""
    parser = TextParser()
    with pytest.raises(FileNotFoundError):
        parser.parse(Path(__file__).parent / "nonexistent.txt")


def test_text_parser_invalid_json():
    """Test TextParser raises error for invalid JSON"""
    parser = TextParser()
    test_file = Path(__file__).parent.parent / "test_data" / "invalid.json"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text('{"invalid": json}')
    with pytest.raises(ValueError, match="Invalid JSON"):
        parser.parse(test_file)
    test_file.unlink()


def test_docx_parser():
    """Test parsing DOCX files - uses sample doc if available"""
    parser = DocxParser()
    sample_file = Path(__file__).parent.parent / "data" / "sample_docs" / "sample.docx"
    if sample_file.exists():
        content = parser.parse(sample_file)
        assert isinstance(content, str)
        assert len(content) > 0
    else:
        pytest.skip("Sample DOCX file not found")


def test_pdf_parser():
    """Test parsing PDF files - uses sample PDF if available"""
    parser = PDFParser()
    sample_file = Path(__file__).parent.parent / "data" / "sample_docs" / "sample.pdf"
    if sample_file.exists():
        content = parser.parse(sample_file)
        assert isinstance(content, str)
        assert len(content) > 0
    else:
        pytest.skip("Sample PDF file not found")


def test_docx_parser_file_not_found():
    """Test DocxParser raises error for missing file"""
    parser = DocxParser()
    with pytest.raises(FileNotFoundError):
        parser.parse(Path(__file__).parent / "nonexistent.docx")


def test_pdf_parser_file_not_found():
    """Test PDFParser raises error for missing file"""
    parser = PDFParser()
    with pytest.raises(FileNotFoundError):
        parser.parse(Path(__file__).parent / "nonexistent.pdf")
