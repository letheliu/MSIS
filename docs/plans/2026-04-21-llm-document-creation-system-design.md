# 军墨智工 - 基于本地LLM的公文创作系统设计

> 版本: 2.0 | 日期: 2026-04-21 | 状态: 设计中

---

## 一、系统概述

### 1.1 项目定位

**军墨智工 (MSIS - Military Script Intelligence System)** 是一套完全离线运行的公文智能创作系统。系统以 **Sirchmunk** 为智能检索基座，结合本地部署的大语言模型(LLM)，实现从文档入库到公文生成的全链路智能化辅助。

### 1.2 核心原则

- **数据本地化**：所有文档、模型、索引均在本地处理，不依赖外部云服务
- **零预索引**：基于 Sirchmunk 的无向量库架构，原始文件即搜即用
- **自进化知识**：检索结果自动沉淀为 KnowledgeCluster，越用越准
- **模块化设计**：各功能模块低耦合高内聚，可独立演进

### 1.3 Sirchmunk 核心能力

本系统选择 **Sirchmunk** 作为检索引擎基座，其核心优势：

| 能力 | 说明 |
|------|------|
| **无向量库** | 无需 ChromaDB/Milvus 等向量数据库，无需嵌入模型，零基础设施开销 |
| **零预索引** | 原始文件直接检索，无需分块(chunking)和嵌入(embedding)预处理 |
| **蒙特卡洛精准抽证** | 三阶段探索-利用策略（撒网→聚焦→合成），从大文档中高效定位关键证据 |
| **自进化沉淀知识库** | 每次深度检索结果结构化为 KnowledgeCluster 并持久化，系统越用越快、越用越准 |
| **ReAct 智能体兜底** | 复杂查询自动触发智能体推理链，保障检索召回率 |
| **全链路集成** | 原生支持 Python SDK / REST API / MCP Server / CLI / Web UI |

### 1.4 系统架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                   前端展示层 (Vue 3 + Element Plus)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐ │
│  │ 文档管理  │ │ 智能检索  │ │ 公文创作  │ │ 校对与优化     │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘ │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP / SSE
┌───────────────────────┴─────────────────────────────────────┐
│                   API 网关层 (FastAPI)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐ │
│  │ 文档API   │ │ 检索API   │ │ 生成API   │ │ 校验API        │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘ │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────────┐
│                   服务层 (Business Logic)                     │
│  ┌──────────┐ ┌──────────────────┐ ┌──────────┐            │
│  │ 文档服务  │ │ Sirchmunk检索服务 │ │ 模板服务  │            │
│  └──────────┘ └──────────────────┘ └──────────┘            │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐            │
│  │ LLM服务   │ │ 校验服务  │ │ 创作编排服务      │            │
│  └──────────┘ └──────────┘ └──────────────────┘            │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────────┐
│               Sirchmunk 智能检索引擎 + 本地LLM               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  AgenticSearch 编排器                                   │ │
│  │  ┌──────────────┐  ┌────────────────────────────────┐ │ │
│  │  │ GrepRetriever│  │ Monte Carlo Evidence Sampler   │ │ │
│  │  │ (ripgrep扫描) │  │ (探索→聚焦→合成 三阶段抽证)     │ │ │
│  │  └──────────────┘  └────────────────────────────────┘ │ │
│  │  ┌──────────────────────┐  ┌───────────────────────┐  │ │
│  │  │ KnowledgeCluster     │  │ ReAct Agent           │  │ │
│  │  │ (自进化知识沉淀)       │  │ (智能体推理兜底)       │  │ │
│  │  └──────────────────────┘  └───────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────────────┐│
│  │ SQLite   │ │ 文件系统   │ │ 本地LLM (Qwen2.5/Ollama)    ││
│  │ (元数据)  │ │ (原始文档) │ │ (推理引擎)                   ││
│  └──────────┘ └──────────┘ └──────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## 二、技术栈选型

### 2.1 后端技术栈

| 组件 | 技术选型 | 版本 | 选型理由 |
|------|----------|------|----------|
| Web框架 | FastAPI | >=0.104 | 异步高性能，自动生成API文档 |
| **智能检索引擎** | **Sirchmunk** | **>=0.0.2** | **无向量库、零预索引、蒙特卡洛抽证、自进化知识库** |
| 关系数据库 | SQLite (via SQLAlchemy) | >=2.0 | 轻量级本地数据库，零配置 |
| LLM推理 | Ollama / llama-cpp-python | - | 支持GGUF量化模型，CPU/GPU兼容 |
| LLM接口 | Sirchmunk OpenAIChat | - | Sirchmunk内置LLM适配层，OpenAI兼容协议 |
| 文档解析 | python-docx / pdfplumber | - | 已集成，支持docx/pdf/txt/md |
| 文件扫描 | ripgrep / ripgrep-all | - | Sirchmunk依赖，高吞吐原始文件扫描 |

### 2.2 前端技术栈

| 组件 | 技术选型 | 版本 | 选型理由 |
|------|----------|------|----------|
| 框架 | Vue 3 | ^3.4 | 组合式API，响应式强 |
| UI库 | Element Plus | ^2.4 | 企业级组件丰富 |
| 状态管理 | Pinia | ^2.1 | 已引入，轻量级状态管理 |
| HTTP客户端 | Axios | ^1.6 | 已引入，拦截器支持完善 |
| 构建工具 | Vite | ^5.0 | 已配置，开发体验好 |

### 2.3 LLM模型选型建议

| 场景 | 推荐模型 | 参数量 | 量化 | 显存需求 |
|------|----------|--------|------|----------|
| 单机CPU | Qwen2.5-7B-Instruct | 7B | Q4_K_M | 4GB内存 |
| GPU桌面 | Qwen2.5-14B-Instruct | 14B | Q4_K_M | 8GB显存 |
| 服务器 | Qwen2.5-32B-Instruct | 32B | Q4_K_M | 20GB显存 |

> **注意**: Sirchmunk 自身也使用 LLM 进行检索推理和知识合成，因此需要确保 LLM 服务同时服务于检索和生成两个场景。推荐使用 Ollama 统一管理模型，通过 OpenAI 兼容协议同时供 Sirchmunk 和 MSIS 业务层调用。

---

## 三、Sirchmunk 集成架构

### 3.1 集成方式

Sirchmunk 提供三种集成方式，本系统全部利用：

```
┌─────────────────────────────────────────────────────────┐
│                    MSIS Backend                          │
│                                                         │
│  ┌─────────────────┐    ┌─────────────────────────┐    │
│  │ Python SDK      │    │ REST API (SSE Streaming) │    │
│  │ (AgenticSearch) │    │ POST /api/v1/search      │    │
│  │                 │    │ POST /api/v1/search/stream│    │
│  └────────┬────────┘    └────────────┬────────────┘    │
│           │                          │                   │
│           │    ┌─────────────────────┘                   │
│           │    │                                         │
│  ┌────────▼────▼───────────────────────────────────┐    │
│  │          Sirchmunk Service Layer                 │    │
│  │  - AgenticSearch 检索编排                        │    │
│  │  - OpenAIChat LLM接口                            │    │
│  │  - KnowledgeCluster 知识沉淀                     │    │
│  └──────────────────────────────────────────────────┘    │
│                                                         │
│  ┌──────────────────────────────────────────────────┐    │
│  │  MCP Server (可选，供IDE/Agent集成)               │    │
│  │  sirchmunk mcp serve                              │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Sirchmunk Python SDK 使用

```python
import asyncio
from sirchmunk import AgenticSearch
from sirchmunk.llm import OpenAIChat

llm = OpenAIChat(
    api_key="your-api-key",
    base_url="http://localhost:11434/v1",
    model="qwen2.5:7b",
)

search = AgenticSearch(llm=llm)

result = await search.search(
    query="年度训练计划的关键要素",
    paths=["./data/sample_docs"],
    mode="DEEP",
)
```

### 3.3 检索模式选择

| 模式 | 耗时 | 适用场景 | MSIS用途 |
|------|------|----------|----------|
| `FAST` | 3-10秒 | 快速关键词匹配 | 文档列表搜索、文件名查找 |
| `DEEP` | 10-30秒 | 蒙特卡洛多阶段分析+LLM合成 | 公文创作时检索参考资料 |
| `FILENAME_ONLY` | <1秒 | 纯文件名搜索（无需LLM） | 文档管理界面快速定位 |

### 3.4 KnowledgeCluster 知识沉淀

```python
class KnowledgeCluster:
    """
    Sirchmunk 自进化知识单元
    - 每次DEEP检索自动生成并持久化
    - 后续相似查询可直接复用，跳过重新检索
    - 越用越快、越用越准
    """
    title: str                  # 知识主题
    content: str                # LLM合成的结构化Markdown分析
    patterns: List[str]         # 从证据中提炼的3-5条核心模式
    confidence: float           # 置信度 [0, 1]
    source_files: List[str]     # 引用来源文件
    related_queries: List[str]  # 关联查询
```

---

## 四、模块详细设计

### 4.1 文档管理模块（增强现有）

#### 4.1.1 功能清单

| 功能 | 状态 | 说明 |
|------|------|------|
| 文档上传 | ✅ 已实现 | 支持 .txt/.md/.json/.docx/.pdf |
| 文档目录指定 | ✅ 已实现 | ConfigManager 管理 |
| 批量导入与索引 | ✅ 已实现 | 文件复制到索引目录 |
| 文件监听 | ✅ 已实现 | watchdog 实时监听 |
| 文档元数据管理 | 🆕 新增 | SQLite 存储元数据 |
| 文档类型分类 | 🆕 新增 | 自动/手动分类 |

> **架构变更**: 原有 `DocumentIndexer` 的文件复制索引逻辑不再需要向量化处理。Sirchmunk 直接读取原始文件进行检索，文档管理模块仅负责文件存储和元数据管理。

#### 4.1.2 数据模型

```python
class Document(BaseModel):
    id: int
    filename: str
    file_type: str              # txt, docx, pdf, md, json
    doc_type: Optional[str]     # command, report, notice, summary, memo
    file_size: int
    file_path: str              # 原始文件存储路径
    content_hash: str           # SHA256 文件指纹
    upload_time: datetime
    update_time: datetime
    metadata: Dict[str, Any]    # 扩展元数据
```

---

### 4.2 Sirchmunk 检索服务（核心新增）

#### 4.2.1 服务封装

```python
from sirchmunk import AgenticSearch
from sirchmunk.llm import OpenAIChat

class SirchmunkService:
    """Sirchmunk 检索服务封装"""

    def __init__(self, config: SirchmunkConfig):
        self.llm = OpenAIChat(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            model=config.llm_model,
        )
        self.search = AgenticSearch(llm=self.llm)
        self.search_paths = config.search_paths

    async def search_documents(
        self,
        query: str,
        mode: str = "FAST",
        paths: Optional[List[str]] = None,
    ) -> SearchResult:
        """
        文档检索入口

        Args:
            query: 检索查询
            mode: FAST / DEEP / FILENAME_ONLY
            paths: 搜索路径（默认使用配置的全局路径）
        """
        result = await self.search.search(
            query=query,
            paths=paths or self.search_paths,
            mode=mode,
        )
        return result

    async def search_for_generation(
        self,
        topic: str,
        doc_type: str,
        reference_docs: Optional[List[str]] = None,
    ) -> GenerationContext:
        """
        为公文生成检索参考资料（DEEP模式）

        流程:
        1. 构建领域特定查询（结合主题+公文类型）
        2. DEEP模式检索 → 蒙特卡洛抽证
        3. 自动沉淀 KnowledgeCluster
        4. 提取结构化上下文返回给生成服务
        """
        query = f"{doc_type}类公文 {topic} 相关内容要点和格式要求"

        if reference_docs:
            paths = [os.path.join(self.search_paths[0], doc) for doc in reference_docs]
        else:
            paths = self.search_paths

        result = await self.search.search(
            query=query,
            paths=paths,
            mode="DEEP",
        )

        return GenerationContext(
            query=query,
            evidence=result.content,
            patterns=result.patterns,
            confidence=result.confidence,
            source_files=result.source_files,
        )

    async def get_knowledge_clusters(self) -> List[KnowledgeCluster]:
        """获取已沉淀的知识库列表"""

    async def get_search_stats(self) -> Dict:
        """获取检索统计信息"""
```

#### 4.2.2 配置管理

```python
class SirchmunkConfig(BaseModel):
    """Sirchmunk 配置"""
    llm_api_key: str = "ollama"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "qwen2.5:7b"
    search_paths: List[str] = ["./data/sample_docs"]
    default_mode: str = "FAST"
    max_concurrent_searches: int = 3
```

对应 `.env` 配置：

```env
SIRCHMUNK_LLM_API_KEY=ollama
SIRCHMUNK_LLM_BASE_URL=http://localhost:11434/v1
SIRCHMUNK_LLM_MODEL=qwen2.5:7b
SIRCHMUNK_SEARCH_PATHS=./data/sample_docs
SIRCHMUNK_MAX_CONCURRENT_SEARCHES=3
```

---

### 4.3 LLM集成与推理引擎（新增）

#### 4.3.1 LLM服务架构

```
┌─────────────────────────────────────────────┐
│              LLMService (统一接口)            │
│  - generate(prompt, params)                 │
│  - stream_generate(prompt, params)          │
│  - get_model_info()                         │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │   Ollama (推荐)      │
        │   OpenAI兼容协议      │
        │   同时服务:           │
        │   - Sirchmunk检索    │
        │   - MSIS公文生成     │
        │   - 格式校验推理     │
        └─────────────────────┘
```

> **设计决策**: 不再独立实现 `LlamaCppAdapter` 和 `OllamaAdapter`。Sirchmunk 已内置 `OpenAIChat` LLM 适配层，统一通过 Ollama 的 OpenAI 兼容协议 (`/v1/chat/completions`) 同时服务检索和生成场景。

#### 4.3.2 LLM服务实现

```python
import httpx

class LLMService:
    """LLM推理服务（基于OpenAI兼容协议）"""

    def __init__(self, base_url: str = "http://localhost:11434/v1", model: str = "qwen2.5:7b"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(base_url=base_url, timeout=120.0)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        """同步生成完整响应"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.post(
            "/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        return response.json()["choices"][0]["message"]["content"]

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """流式生成，逐token返回"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with self.client.stream(
            "POST",
            "/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
            },
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    data = json.loads(line[6:])
                    delta = data["choices"][0].get("delta", {})
                    if "content" in delta:
                        yield delta["content"]
```

#### 4.3.3 提示词工程

```python
class PromptTemplates:
    """公文写作提示词模板"""

    SYSTEM_PROMPT = (
        "你是一个专业的军队公文写作助手。请根据提供的参考资料和格式要求，"
        "撰写符合军队公文写作规范的公文。要求用语规范、逻辑清晰、格式正确。"
    )

    GENERATION_TEMPLATE = """{system_prompt}

参考资料（由智能检索系统提供）：
{context}

公文类型：{doc_type}
主题：{topic}
字数要求：{word_count}字左右
风格：{style}

格式要求：
{format_requirements}

请严格按照{doc_type}的公文格式撰写，确保内容完整、用语规范。"""

    OPTIMIZATION_TEMPLATE = """请对以下公文内容进行优化，从以下几个方面给出具体修改建议：

1. 用语规范性：是否符合军队公文用语标准
2. 逻辑结构：论述是否清晰、层次是否分明
3. 格式合规性：是否符合公文格式规范
4. 内容完整性：是否有遗漏的关键要素

原文：
{content}

公文类型：{doc_type}

请逐条给出修改建议，并给出修改后的文本。"""

    TYPE_REQUIREMENTS = {
        "command": (
            "格式要求：\n"
            "1. 标题使用「关于XXX的命令」格式\n"
            "2. 正文以命令口吻撰写，用词果断、准确\n"
            "3. 包含受令单位、命令内容、执行要求、时限\n"
            "4. 署名为指挥机关全称"
        ),
        "notice": (
            "格式要求：\n"
            "1. 标题使用「关于XXX的通知」格式\n"
            "2. 正文包含：通知事由、具体要求、执行时限\n"
            "3. 语言正式、条理清晰\n"
            "4. 包含主送单位和落款"
        ),
        "report": (
            "格式要求：\n"
            "1. 标题使用「关于XXX的报告」格式\n"
            "2. 正文包含：情况概述、主要工作、成效分析、存在问题、下步打算\n"
            "3. 数据准确，论据充分\n"
            "4. 语言客观、实事求是"
        ),
        "summary": (
            "格式要求：\n"
            "1. 标题使用「XXX工作总结」格式\n"
            "2. 正文包含：基本情况、主要做法、取得成效、经验启示、下步计划\n"
            "3. 全面系统、重点突出\n"
            "4. 语言精炼、概括性强"
        ),
        "memo": (
            "格式要求：\n"
            "1. 标题使用「XXX会议纪要」格式\n"
            "2. 正文包含：会议时间地点、参会人员、议题、决议、责任分工\n"
            "3. 记录准确、要点清晰\n"
            "4. 突出决策事项和执行要求"
        ),
    }
```

---

### 4.4 创作编排服务（核心新增）

#### 4.4.1 编排流程

```
用户输入(主题+类型+参数)
       │
       ▼
┌──────────────────────────────────────────────┐
│          创作编排服务 (CreationOrchestrator)   │
│                                              │
│  Step 1: Sirchmunk DEEP检索                  │
│    query="关于{topic}的{doc_type}要点"         │
│    → 蒙特卡洛抽证 → KnowledgeCluster沉淀       │
│                                              │
│  Step 2: 上下文组装                           │
│    → 检索结果 + 模板格式要求 + 用户参数         │
│                                              │
│  Step 3: 提示词构建                           │
│    → system + context + format + query        │
│                                              │
│  Step 4: LLM 流式生成                         │
│    → SSE 逐token推送到前端                    │
│                                              │
│  Step 5: 后处理                              │
│    → 格式规范化 → 存储生成记录                 │
└──────────────────────────────────────────────┘
```

#### 4.4.2 编排服务实现

```python
class CreationOrchestrator:
    """公文创作编排服务"""

    def __init__(
        self,
        sirchmunk: SirchmunkService,
        llm: LLMService,
        prompts: PromptTemplates,
    ):
        self.sirchmunk = sirchmunk
        self.llm = llm
        self.prompts = prompts

    async def create_document(
        self,
        topic: str,
        doc_type: str,
        reference_docs: Optional[List[str]] = None,
        parameters: Optional[Dict] = None,
    ) -> AsyncIterator[str]:
        """
        公文创作主流程（流式输出）

        1. 调用 Sirchmunk DEEP 检索获取参考资料
           - 蒙特卡洛三阶段抽证自动定位关键内容
           - 结果自动沉淀为 KnowledgeCluster（下次更快）
           - ReAct 智能体兜底确保召回率
        2. 组装生成提示词
        3. LLM 流式生成
        """
        params = parameters or {}
        word_count = params.get("word_count", 800)
        style = params.get("style", "正式")

        # Step 1: Sirchmunk DEEP 检索
        context = await self.sirchmunk.search_for_generation(
            topic=topic,
            doc_type=doc_type,
            reference_docs=reference_docs,
        )

        # Step 2 & 3: 构建提示词
        format_req = self.prompts.TYPE_REQUIREMENTS.get(doc_type, "")
        prompt = self.prompts.GENERATION_TEMPLATE.format(
            system_prompt=self.prompts.SYSTEM_PROMPT,
            context=context.evidence,
            doc_type=doc_type,
            topic=topic,
            word_count=word_count,
            style=style,
            format_requirements=format_req,
        )

        # Step 4: LLM 流式生成
        async for token in self.llm.stream_generate(
            prompt=prompt,
            system_prompt=self.prompts.SYSTEM_PROMPT,
            max_tokens=word_count * 2,
            temperature=0.7,
        ):
            yield token

    async def optimize_document(
        self,
        content: str,
        doc_type: str,
    ) -> AsyncIterator[str]:
        """文档优化（流式输出）"""
        prompt = self.prompts.OPTIMIZATION_TEMPLATE.format(
            content=content,
            doc_type=doc_type,
        )
        async for token in self.llm.stream_generate(
            prompt=prompt,
            temperature=0.5,
        ):
            yield token
```

#### 4.4.3 生成API设计

| 方法 | 路径 | 说明 | 请求/响应 |
|------|------|------|-----------|
| POST | /api/generation/create | 创建生成任务 | Request: topic, doc_type, reference_docs, parameters; Response: task_id |
| GET | /api/generation/{task_id}/stream | SSE流式获取生成内容 | Response: text/event-stream |
| GET | /api/generation/{task_id} | 获取完整生成结果 | Response: content, metadata, sources |
| POST | /api/generation/{task_id}/optimize | 请求优化建议 | Response: suggestions (SSE) |
| GET | /api/generation/history | 获取生成历史 | Response: list of records |
| DELETE | /api/generation/{task_id} | 删除生成记录 | Response: success |
| POST | /api/generation/export/{task_id} | 导出文档 | Request: format (docx/pdf); Response: file download |

---

### 4.5 格式校验模块

#### 4.5.1 校验规则引擎

```python
class ValidationRule(ABC):
    """校验规则抽象基类"""
    @abstractmethod
    def check(self, content: str, doc_type: str) -> List[ValidationIssue]:
        ...

class StructureValidator(ValidationRule):
    """结构校验：检查必要章节是否存在"""

class LengthValidator(ValidationRule):
    """长度校验：检查字数是否在合理范围"""

class TerminologyValidator(ValidationRule):
    """术语校验：检查军队用语规范"""

class FormatValidator(ValidationRule):
    """格式校验：检查编号、日期、署名等格式"""

class ValidationEngine:
    """格式校验引擎（规则引擎 + LLM辅助）"""

    def __init__(self, rules: List[ValidationRule], llm: LLMService):
        self.rules = rules
        self.llm = llm

    async def validate(self, content: str, doc_type: str) -> ValidationResult:
        """
        两阶段校验:
        1. 规则引擎快速检查（结构/格式/长度/术语）
        2. LLM 辅助深度检查（用语/逻辑/完整性）
        """
```

#### 4.5.2 校验结果模型

```python
class ValidationIssue(BaseModel):
    rule: str                     # 规则名称
    level: str                    # error / warning / info
    message: str                  # 问题描述
    position: Optional[int]       # 字符位置
    suggestion: Optional[str]     # 修改建议

class ValidationResult(BaseModel):
    passed: bool                  # 是否通过
    score: float                  # 合规评分 0-100
    issues: List[ValidationIssue]
    summary: str                  # 总结描述
```

---

### 4.6 用户交互模块（新增前端页面）

#### 4.6.1 公文创作工作台 — CreateDocument.vue

```
┌─────────────────────────────────────────────────────────────┐
│  军墨智工 - 公文创作工作台                                    │
├──────────────────────┬──────────────────────────────────────┤
│  创作配置面板          │  内容生成区                           │
│                      │                                      │
│  📋 公文类型          │  ┌────────────────────────────────┐  │
│  ┌────────────────┐  │  │  实时生成内容预览               │  │
│  │ ▼ 通知         │  │  │  (SSE流式输出，逐字显示)        │  │
│  └────────────────┘  │  │                                │  │
│                      │  │  📎 参考来源: 训练计划.txt       │  │
│  📝 主题/标题        │  │  📎 参考来源: 工作总结.txt       │  │
│  ┌────────────────┐  │  │  📎 知识库命中: 2个相关集群      │  │
│  │ 关于XXX的通知   │  │  └────────────────────────────────┘  │
│  └────────────────┘  │                                      │
│                      │  操作按钮:                            │
│  📄 参考文档         │  [重新生成] [优化建议] [格式校验]     │
│  ┌────────────────┐  │  [导出Word] [导出PDF]              │
│  │ ☑ 训练计划.txt  │  │                                      │
│  │ ☑ 工作总结.txt  │  │                                      │
│  │ ☐ 放假通知.txt  │  │                                      │
│  └────────────────┘  │                                      │
│                      │                                      │
│  ⚙ 创作参数          │                                      │
│  字数要求: [800]      │                                      │
│  风格: [正式]         │                                      │
│  检索模式: [●DEEP]   │                                      │
│                      │                                      │
│  [开始创作]           │                                      │
├──────────────────────┴──────────────────────────────────────┤
│  🧠 知识库面板                                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ 训练计划要点  │ │ 通知格式规范  │ │ 工作总结框架  │        │
│  │ 置信度: 0.92 │ │ 置信度: 0.87 │ │ 置信度: 0.79 │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

#### 4.6.2 前端路由扩展

| 路径 | 名称 | 组件 | 说明 |
|------|------|------|------|
| /create | CreateDocument | CreateDocument.vue | 公文创作工作台 |
| /create/:id | EditDocument | CreateDocument.vue | 编辑已生成文档 |
| /validation | Validation | ValidationPage.vue | 格式校验页面 |
| /history | History | GenerationHistory.vue | 生成历史 |
| /knowledge | Knowledge | KnowledgePage.vue | 知识库管理 |

#### 4.6.3 Pinia 状态管理

```typescript
// stores/generation.ts
interface GenerationState {
  task: {
    topic: string
    docType: string
    referenceDocs: string[]
    searchMode: 'FAST' | 'DEEP'
    parameters: {
      wordCount: number
      style: string
      detailLevel: string
    }
  }
  result: {
    content: string
    isStreaming: boolean
    taskId: string
    sources: string[]
    knowledgeClusters: KnowledgeCluster[]
  }
  history: GenerationRecord[]
}
```

---

### 4.7 系统架构设计

#### 4.7.1 后端包结构（重构后）

```
backend/src/
├── main.py                         # FastAPI 应用入口 + 生命周期
├── core/                           # 核心配置
│   ├── __init__.py
│   ├── config.py                   # 全局配置（环境变量、默认值）
│   ├── database.py                 # SQLAlchemy 数据库连接
│   └── dependencies.py             # FastAPI 依赖注入
├── documents/                      # 文档管理模块（已有，增强）
│   ├── __init__.py
│   ├── models.py                   # SQLAlchemy ORM 模型
│   ├── schemas.py                  # Pydantic 请求/响应模型
│   ├── parsers.py                  # 文档解析器（已有）
│   ├── library.py                  # 文档库服务（已有）
│   ├── service.py                  # 文档业务逻辑层
│   └── api.py                      # 文档API路由
├── search/                         # Sirchmunk检索模块（重构）
│   ├── __init__.py
│   ├── sirchmunk_service.py        # Sirchmunk 服务封装
│   ├── schemas.py                  # 检索请求/响应模型
│   └── api.py                      # 检索API路由
├── llm/                            # LLM集成模块（新增）
│   ├── __init__.py
│   ├── service.py                  # LLM服务（OpenAI兼容协议）
│   └── prompts.py                  # 提示词模板
├── creation/                       # 创作编排模块（新增）
│   ├── __init__.py
│   ├── orchestrator.py             # 创作编排器
│   ├── schemas.py                  # 生成请求/响应模型
│   ├── task_manager.py             # 异步任务管理
│   └── api.py                      # 生成API路由（含SSE）
├── templates/                      # 模板管理模块（已有）
│   ├── __init__.py
│   ├── models.py                   # 模板数据模型
│   ├── manager.py                  # 模板管理器
│   ├── renderer.py                 # 模板渲染器
│   └── api.py                      # 模板API路由
├── validation/                     # 格式校验模块（新增）
│   ├── __init__.py
│   ├── rules.py                    # 校验规则集
│   ├── engine.py                   # 校验引擎
│   ├── service.py                  # 校验服务
│   └── api.py                      # 校验API路由
└── knowledge/                      # 知识库管理模块（新增）
    ├── __init__.py
    ├── service.py                  # KnowledgeCluster 管理
    └── api.py                      # 知识库API路由
```

#### 4.7.2 异步处理机制

```python
class TaskManager:
    """异步任务管理器"""

    def __init__(self):
        self.tasks: Dict[str, GenerationTask] = {}

    async def create_task(self, params: GenerationParams) -> str:
        """创建生成任务，返回task_id"""

    async def stream_result(self, task_id: str) -> AsyncIterator[str]:
        """SSE 流式返回生成结果"""

# FastAPI SSE 路由
@router.get("/generation/{task_id}/stream")
async def stream_generation(task_id: str):
    async def event_stream():
        async for token in task_manager.stream_result(task_id):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

#### 4.7.3 日志与监控

```python
class Metrics:
    """系统监控指标"""
    documents_total: int              # 文档总数
    knowledge_clusters: int           # 已沉淀知识集群数
    generations_total: int            # 生成请求总数
    generation_avg_time: float        # 平均生成耗时(秒)
    sirchmunk_searches: int           # Sirchmunk检索次数
    sirchmunk_cache_hits: int         # KnowledgeCluster命中次数
    llm_latency_ms: float             # LLM推理延迟
```

---

## 五、部署架构

### 5.1 Docker Compose 配置

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
    environment:
      # Sirchmunk 配置
      - SIRCHMUNK_LLM_API_KEY=ollama
      - SIRCHMUNK_LLM_BASE_URL=http://ollama:11434/v1
      - SIRCHMUNK_LLM_MODEL=qwen2.5:7b
      - SIRCHMUNK_SEARCH_PATHS=/app/data/sample_docs
      # MSIS 配置
      - LLM_BASE_URL=http://ollama:11434/v1
      - LLM_MODEL=qwen2.5:7b
      - DATABASE_URL=sqlite:///data/msis.db
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  ollama_data:
```

### 5.2 与原架构的对比

| 维度 | 原方案 (ChromaDB + 嵌入模型) | 新方案 (Sirchmunk) |
|------|------|------|
| 向量数据库 | 需要 ChromaDB | **无需** |
| 嵌入模型 | 需要 bge-small-zh-v1.5 | **无需** |
| 文本分块 | 需要实现分块器 | **无需** (蒙特卡洛采样) |
| 预索引 | 需要索引管道 | **无需** (即搜即用) |
| 知识沉淀 | 需要自行实现 | **内置** KnowledgeCluster |
| 智能体兜底 | 需要自行实现 | **内置** ReAct Agent |
| 新增依赖 | chromadb, sentence-transformers | 仅 sirchmunk |
| 复杂度 | 高（分块+嵌入+索引+检索） | **低**（直接检索） |
| 自进化 | 无 | **有**（越用越准） |

---

## 六、实施路线图

### Phase 1: Sirchmunk集成 + LLM基础（2周）

**目标**: 接入 Sirchmunk 检索和本地 LLM，实现基础公文生成

| 任务 | 说明 | 依赖 |
|------|------|------|
| T1.1 | 创建 `core/config.py` 全局配置 | 无 |
| T1.2 | 创建 `core/database.py` SQLAlchemy初始化 | T1.1 |
| T1.3 | 实现 `SirchmunkService` 检索服务封装 | T1.1 |
| T1.4 | 实现 `LLMService` OpenAI兼容协议封装 | T1.1 |
| T1.5 | 实现 `PromptTemplates` 提示词模板 | 无 |
| T1.6 | 实现 `CreationOrchestrator` 基础编排 | T1.3, T1.4, T1.5 |
| T1.7 | 实现生成API（含SSE流式输出） | T1.6 |
| T1.8 | 前端 `CreateDocument.vue` 基础版 | T1.7 |
| T1.9 | 重构现有检索API对接Sirchmunk | T1.3 |

### Phase 2: 文档管理增强 + 知识库（1周）

**目标**: 完善文档元数据管理，接入 KnowledgeCluster

| 任务 | 说明 | 依赖 |
|------|------|------|
| T2.1 | 实现文档元数据SQLAlchemy模型 | T1.2 |
| T2.2 | 重构文档服务对接新模型 | T2.1 |
| T2.3 | 实现知识库管理API | T1.3 |
| T2.4 | 前端知识库管理页面 | T2.3 |
| T2.5 | 前端集成参考文档选择 + 检索模式切换 | T1.8, T2.3 |

### Phase 3: 格式校验与优化（1周）

**目标**: 实现公文格式校验和内容优化

| 任务 | 说明 | 依赖 |
|------|------|------|
| T3.1 | 实现校验规则引擎 | 无 |
| T3.2 | 实现结构/格式/术语校验器 | T3.1 |
| T3.3 | 实现优化建议生成 | T1.4 |
| T3.4 | 实现校验API | T3.2 |
| T3.5 | 前端校验报告页面 | T3.4 |

### Phase 4: 打磨与部署（1周）

**目标**: 完善用户体验和部署配置

| 任务 | 说明 | 依赖 |
|------|------|------|
| T4.1 | 文档导出（Word/PDF） | T1.7 |
| T4.2 | 生成历史管理 | T1.7 |
| T4.3 | Pinia状态管理集成 | T1.8 |
| T4.4 | Docker部署完善（含Ollama） | 全部 |
| T4.5 | 性能测试与优化 | 全部 |

---

## 七、新增依赖清单

### 后端新增依赖

```toml
[project.dependencies]
# 现有依赖保留...

# 智能检索引擎
sirchmunk = ">=0.0.2"                # Sirchmunk 检索引擎

# 数据库
sqlalchemy = ">=2.0.0"               # ORM

# 文档导出
python-docx = ">=1.2.0"              # Word导出（已有）

# 日志
python-json-logger = ">=2.0.0"      # JSON格式日志
```

> **注意**: 不再需要 `chromadb`、`sentence-transformers`、`llama-cpp-python`、`cachetools`。Sirchmunk 自带无向量检索和知识沉淀能力，大幅简化依赖。

### 前端新增依赖

```json
{
  "dependencies": {
    "@vueuse/core": "^10.0.0",
    "markdown-it": "^14.0.0"
  }
}
```

---

## 八、关键设计决策记录

| 决策 | 选择 | 备选方案 | 理由 |
|------|------|----------|------|
| **检索引擎** | **Sirchmunk** | ChromaDB + 嵌入模型 | 无向量库、零预索引、自进化、蒙特卡洛精准抽证 |
| LLM服务 | Ollama (OpenAI协议) | llama-cpp-python | Sirchmunk内置OpenAIChat兼容，统一管理 |
| 数据库 | SQLite | PostgreSQL | 本地化，零配置 |
| 流式输出 | SSE | WebSocket | 实现简单，单向推送足够 |
| 前端状态 | Pinia | Vuex | 已引入，Vue3官方推荐 |
| 文本处理 | 蒙特卡洛采样 | 固定分块+嵌入 | Sirchmunk原生支持，保留语义完整性 |
| 知识沉淀 | KnowledgeCluster | 自建缓存 | Sirchmunk内置自进化，越用越准 |
| 智能体兜底 | ReAct Agent | 自建Agent | Sirchmunk内置，保障复杂查询召回率 |
