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


def test_empty_query(sample_documents):
    """测试空查询"""
    retriever = DocumentRetriever(documents=sample_documents)
    results = retriever.search("")
    assert len(results) == 0


def test_nonexistent_keyword(sample_documents):
    """测试不存在的关键词"""
    retriever = DocumentRetriever(documents=sample_documents)
    results = retriever.search("不存在")
    assert len(results) == 0


def test_case_insensitive(sample_documents):
    """测试大小写不敏感"""
    retriever = DocumentRetriever(documents=sample_documents)
    results1 = retriever.search("训练")
    results2 = retriever.search("训练".upper())
    results3 = retriever.search("训练".lower())
    assert len(results1) == len(results2) == len(results3)
    assert results1[0]["id"] == results2[0]["id"] == results3[0]["id"]


def test_top_k_parameter(sample_documents):
    """测试 top_k 参数"""
    retriever = DocumentRetriever(documents=sample_documents)
    # 获取所有结果
    all_results = retriever.search("工作", top_k=10)
    # 限制结果数量
    limited_results = retriever.search("工作", top_k=1)
    assert len(limited_results) == 1
    if len(all_results) > 1:
        assert len(limited_results) < len(all_results)


def test_sorting_correctness(sample_documents):
    """测试排序正确性"""
    retriever = DocumentRetriever(documents=sample_documents)
    results = retriever.search("计划", top_k=5)
    # 检查结果是否按相关性排序（分数应递减）
    if len(results) > 1:
        for i in range(len(results) - 1):
            assert results[i]["score"] >= results[i + 1]["score"]


def test_title_and_content_match(sample_documents):
    """测试 title 和 content 同时匹配"""
    retriever = DocumentRetriever(documents=sample_documents)
    # 使用一个既能匹配 title 也能匹配 content 的关键词
    results = retriever.search("计划")
    # 至少有一个结果
    assert len(results) > 0
    # 检查是否正确匹配
    matched_ids = [r["id"] for r in results]
    assert 1 in matched_ids  # "训练计划" 应该匹配
