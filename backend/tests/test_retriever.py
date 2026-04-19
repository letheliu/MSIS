import pytest
from src.search.retriever import DocumentRetriever


@pytest.fixture
def sample_documents():
    return [
        {"id": 1, "title": "训练计划", "content": "年度训练计划安排"},
        {"id": 2, "title": "工作汇报", "content": "季度工作总结报告"},
        {"id": 3, "title": "通知", "content": "关于放假安排的通知"},
    ]


def test_retriever_init():
    """测试检索器初始化"""
    retriever = DocumentRetriever()
    assert retriever is not None


def test_search_query(sample_documents):
    """测试搜索查询"""
    retriever = DocumentRetriever(documents=sample_documents)
    results = retriever.search("训练")
    assert len(results) > 0
    assert "训练计划" in results[0]["title"]
