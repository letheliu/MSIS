from typing import List, Dict, Optional


class DocumentRetriever:
    """文档检索器"""

    def __init__(self, documents: Optional[List[Dict]] = None):
        self.documents = documents or []

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """搜索文档"""
        if not query:
            return []

        # 简单的关键词匹配（MVP 阶段）
        results = []
        query_lower = query.lower()

        for doc in self.documents:
            score = self._calculate_score(doc, query_lower)
            if score > 0:
                results.append({
                    **doc,
                    "score": score
                })

        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def _calculate_score(self, doc: Dict, query: str) -> float:
        """计算文档相关性分数"""
        title = doc.get("title", "").lower()
        content = doc.get("content", "").lower()

        score = 0
        # 标题匹配权重更高
        if query in title:
            score += 2
        if query in content:
            score += 1

        return score
