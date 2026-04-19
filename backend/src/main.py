from fastapi import FastAPI, Query
from pydantic import BaseModel
from src.search.retriever import DocumentRetriever

app = FastAPI(title="MSIS API", version="0.0.1")

# 示例文档数据（实际应从数据库加载）
sample_docs = [
    {"id": 1, "title": "训练计划", "content": "年度训练计划安排"},
    {"id": 2, "title": "工作汇报", "content": "季度工作总结报告"},
    {"id": 3, "title": "通知", "content": "关于放假安排的通知"},
    {"id": 4, "title": "命令", "content": "关于战备转换的命令"},
]

retriever = DocumentRetriever(documents=sample_docs)

@app.get("/")
def root():
    return {"message": "MSIS - Military Document Writing Assistant API"}

@app.get("/health")
def health():
    return {"status": "ok"}

class SearchResponse(BaseModel):
    query: str
    results: list
    total: int

@app.get("/api/search", response_model=SearchResponse)
def search(q: str = Query(..., min_length=1, description="搜索关键词")):
    """搜索公文文档"""
    results = retriever.search(q)
    return SearchResponse(query=q, results=results, total=len(results))
