# 集成 Sirchmunk + LLM 公文创作系统 Spec

## Why

当前 MSIS 系统仅有基础的文件索引（文件复制）和简单关键词搜索，缺乏智能检索和公文自动生成能力。需要以 Sirchmunk 为检索基座，接入本地 LLM，实现从文档检索到公文生成的全链路智能化。

## What Changes

- 新增 `core/` 核心配置模块（全局配置、数据库初始化、依赖注入）
- 新增 `search/sirchmunk_service.py` 封装 Sirchmunk AgenticSearch 检索服务
- 新增 `llm/service.py` 基于 OpenAI 兼容协议的 LLM 推理服务（含流式输出）
- 新增 `llm/prompts.py` 公文写作提示词模板（5种公文类型）
- 新增 `creation/` 创作编排模块（编排检索+生成流程、SSE流式输出、任务管理）
- 重构现有检索 API 对接 Sirchmunk 替代简单关键词搜索
- 新增前端 `CreateDocument.vue` 公文创作工作台页面
- 新增前端路由 `/create` 和 `/create/:id`
- 更新 `pyproject.toml` 添加 sirchmunk、sqlalchemy 等依赖
- **BREAKING**: 现有 `/api/search` 端点行为变更，从关键词匹配改为 Sirchmunk 智能检索

## Impact

- Affected specs: 检索系统、模板系统、文档管理
- Affected code: `backend/src/main.py`（路由拆分）、`backend/src/search/`（重构）、`frontend/src/router/`（新增路由）、`frontend/src/views/`（新增页面）

---

## ADDED Requirements

### Requirement: 全局配置管理

系统 SHALL 提供 `core/config.py` 统一管理所有配置项，通过环境变量加载。

#### Scenario: 配置加载
- **WHEN** 系统启动
- **THEN** 从环境变量加载 LLM 地址、模型名称、Sirchmunk 搜索路径等配置，并提供合理的默认值

#### Scenario: 配置项
- **WHEN** 配置被访问
- **THEN** 至少包含以下配置：`LLM_BASE_URL`、`LLM_MODEL`、`SIRCHMUNK_SEARCH_PATHS`、`DATABASE_URL`

### Requirement: SQLAlchemy 数据库初始化

系统 SHALL 提供 `core/database.py` 初始化 SQLite 数据库连接。

#### Scenario: 数据库初始化
- **WHEN** 系统启动
- **THEN** 自动创建 SQLite 数据库文件（若不存在），初始化 SQLAlchemy Session，创建所有表

### Requirement: FastAPI 依赖注入

系统 SHALL 提供 `core/dependencies.py` 统一管理 FastAPI 依赖注入。

#### Scenario: 服务获取
- **WHEN** API 路由需要使用 SirchmunkService、LLMService 等服务
- **THEN** 通过 `Depends()` 注入获取服务实例，确保单例复用

### Requirement: Sirchmunk 检索服务

系统 SHALL 封装 Sirchmunk AgenticSearch 为统一检索服务。

#### Scenario: 基础检索
- **WHEN** 调用 `search_documents(query, mode="FAST")`
- **THEN** 通过 Sirchmunk FAST 模式检索文档，返回检索结果

#### Scenario: 深度检索（用于公文生成）
- **WHEN** 调用 `search_for_generation(topic, doc_type)`
- **THEN** 通过 Sirchmunk DEEP 模式（蒙特卡洛抽证）检索，返回包含 evidence、patterns、confidence、source_files 的结构化上下文

#### Scenario: 检索模式
- **WHEN** 用户指定检索模式
- **THEN** 支持 FAST（3-10秒）、DEEP（10-30秒，蒙特卡洛抽证）、FILENAME_ONLY（<1秒）三种模式

### Requirement: LLM 推理服务

系统 SHALL 基于 OpenAI 兼容协议（Ollama）提供 LLM 推理服务。

#### Scenario: 同步生成
- **WHEN** 调用 `generate(prompt, system_prompt, max_tokens, temperature)`
- **THEN** 发送请求到 Ollama `/v1/chat/completions`，返回完整响应文本

#### Scenario: 流式生成
- **WHEN** 调用 `stream_generate(prompt, ...)`
- **THEN** 通过 SSE 逐 token 返回生成内容，可用于实时预览

### Requirement: 公文写作提示词模板

系统 SHALL 提供 5 种公文类型的提示词模板。

#### Scenario: 模板覆盖
- **WHEN** 用户选择公文类型
- **THEN** 系统提供对应类型的格式要求提示词，覆盖：command（命令）、notice（通知）、report（报告）、summary（总结）、memo（纪要）

#### Scenario: 生成提示词构建
- **WHEN** 触发公文生成
- **THEN** 将 system_prompt + 检索上下文 + 用户参数 + 类型格式要求组装为完整提示词

### Requirement: 创作编排服务

系统 SHALL 提供创作编排器，串联检索和生成流程。

#### Scenario: 公文创作流程
- **WHEN** 调用 `create_document(topic, doc_type, reference_docs, parameters)`
- **THEN** 按以下顺序执行：Sirchmunk DEEP检索 → 上下文组装 → 提示词构建 → LLM流式生成 → 逐token yield

#### Scenario: 文档优化
- **WHEN** 调用 `optimize_document(content, doc_type)`
- **THEN** 使用优化提示词模板，通过 LLM 生成优化建议（流式输出）

### Requirement: 生成任务管理

系统 SHALL 管理异步生成任务的生命周期。

#### Scenario: 任务创建
- **WHEN** 用户发起生成请求 `POST /api/generation/create`
- **THEN** 创建后台任务，立即返回 `task_id`

#### Scenario: SSE 流式输出
- **WHEN** 前端连接 `GET /api/generation/{task_id}/stream`
- **THEN** 通过 Server-Sent Events 逐 token 推送生成内容，完成后发送 `done: true`

#### Scenario: 获取完整结果
- **WHEN** 调用 `GET /api/generation/{task_id}`
- **THEN** 返回完整的生成内容、来源文件、元数据

### Requirement: 生成历史管理

系统 SHALL 持久化生成记录。

#### Scenario: 历史查询
- **WHEN** 调用 `GET /api/generation/history`
- **THEN** 返回分页的生成历史记录列表

#### Scenario: 记录删除
- **WHEN** 调用 `DELETE /api/generation/{task_id}`
- **THEN** 删除指定的生成记录

### Requirement: 前端公文创作工作台

系统 SHALL 提供 CreateDocument.vue 公文创作工作台页面。

#### Scenario: 创作配置
- **WHEN** 用户进入创作页面
- **THEN** 显示公文类型选择器、主题输入框、参考文档多选框、参数配置（字数、风格、检索模式）

#### Scenario: 实时生成预览
- **WHEN** 用户点击"开始创作"
- **THEN** 通过 SSE 接收流式内容，逐字显示在预览区域，并显示参考来源和知识库命中信息

#### Scenario: 操作按钮
- **WHEN** 生成完成
- **THEN** 显示"重新生成"、"优化建议"、"格式校验"、"导出"操作按钮

### Requirement: 前端路由扩展

系统 SHALL 新增创作相关路由。

#### Scenario: 路由注册
- **WHEN** 应用加载
- **THEN** 注册 `/create`（新建）、`/create/:id`（编辑）路由，使用 CreateDocument 组件

### Requirement: 重构检索 API

系统 SHALL 将现有 `/api/search` 端点对接 Sirchmunk。

#### Scenario: 检索请求
- **WHEN** 调用 `GET /api/search?q=xxx&mode=FAST`
- **THEN** 使用 Sirchmunk 进行智能检索，返回结构化结果（含来源文件和相关性信息）

---

## MODIFIED Requirements

### Requirement: 现有检索端点行为变更

原 `GET /api/search` 从内存关键词匹配改为 Sirchmunk 智能检索。

- **原行为**: `DocumentRetriever.search(q)` 在内存示例数据中子串匹配
- **新行为**: `SirchmunkService.search_documents(q, mode)` 通过 Sirchmunk 检索文件系统中的原始文档
- **新增参数**: `mode`（可选，默认 FAST）
- **响应格式变更**: 从 `{query, results, total}` 改为包含 Sirchmunk 检索结果的新格式

### Requirement: main.py 路由拆分

原 `main.py` 包含所有端点定义，需要拆分为模块化路由。

- 将路由按领域拆分到 `documents/api.py`、`search/api.py`、`creation/api.py`、`templates/api.py`、`validation/api.py`
- `main.py` 保留应用初始化、中间件配置、路由注册
