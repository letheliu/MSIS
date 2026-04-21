# Tasks

## Phase 1: 基础设施层

- [x] Task 1: 创建 `core/config.py` 全局配置模块
  - [x] 1.1: 定义 `Settings` 类（Pydantic BaseSettings），包含 `LLM_BASE_URL`、`LLM_MODEL`、`SIRCHMUNK_SEARCH_PATHS`、`DATABASE_URL`、`LOG_LEVEL` 等字段及默认值
  - [x] 1.2: 创建全局 `settings` 单例实例

- [x] Task 2: 创建 `core/database.py` 数据库初始化
  - [x] 2.1: 创建 SQLAlchemy `engine` 和 `SessionLocal`（SQLite）
  - [x] 2.2: 创建 `Base` 声明基类
  - [x] 2.3: 提供 `get_db()` 生成器函数用于 FastAPI 依赖注入

- [x] Task 3: 创建 `core/dependencies.py` 依赖注入
  - [x] 3.1: 提供 `get_sirchmunk_service()` 单例获取
  - [x] 3.2: 提供 `get_llm_service()` 单例获取
  - [x] 3.3: 提供 `get_creation_orchestrator()` 单例获取

## Phase 2: 后端服务层

- [x] Task 4: 实现 `search/sirchmunk_service.py` Sirchmunk 检索服务
  - [x] 4.1: 创建 `SirchmunkService` 类，初始化 `AgenticSearch`（使用 `OpenAIChat`）
  - [x] 4.2: 实现 `search_documents(query, mode, paths)` 方法
  - [x] 4.3: 实现 `search_for_generation(topic, doc_type, reference_docs)` 方法（DEEP 模式）
  - [x] 4.4: 实现 `get_knowledge_clusters()` 方法

- [x] Task 5: 实现 `llm/service.py` LLM 推理服务
  - [x] 5.1: 创建 `LLMService` 类，初始化 `httpx.AsyncClient`
  - [x] 5.2: 实现 `generate(prompt, system_prompt, max_tokens, temperature)` 异步方法
  - [x] 5.3: 实现 `stream_generate(prompt, ...)` 异步生成器方法（逐 token yield）

- [x] Task 6: 实现 `llm/prompts.py` 提示词模板
  - [x] 6.1: 定义 `PromptTemplates` 类，包含 `SYSTEM_PROMPT`、`GENERATION_TEMPLATE`、`OPTIMIZATION_TEMPLATE`
  - [x] 6.2: 定义 5 种公文类型的 `TYPE_REQUIREMENTS` 字典（command/notice/report/summary/memo）

- [x] Task 7: 实现 `creation/orchestrator.py` 创作编排器
  - [x] 7.1: 创建 `CreationOrchestrator` 类，注入 `SirchmunkService`、`LLMService`、`PromptTemplates`
  - [x] 7.2: 实现 `create_document(topic, doc_type, reference_docs, parameters)` 异步生成器（Sirchmunk DEEP → 提示词构建 → LLM 流式生成）
  - [x] 7.3: 实现 `optimize_document(content, doc_type)` 异步生成器

- [x] Task 8: 实现 `creation/task_manager.py` 任务管理器
  - [x] 8.1: 创建 `TaskManager` 类，管理生成任务的生命周期
  - [x] 8.2: 实现 `create_task(params)` → 返回 `task_id`
  - [x] 8.3: 实现 `stream_result(task_id)` → AsyncIterator
  - [x] 8.4: 实现 `get_task(task_id)` → 获取完整结果
  - [x] 8.5: 实现 `list_tasks()` → 获取历史列表
  - [x] 8.6: 实现 `delete_task(task_id)` → 删除记录

## Phase 3: API 路由层

- [x] Task 9: 实现 `creation/api.py` 生成 API 路由
  - [x] 9.1: `POST /api/generation/create` — 创建生成任务
  - [x] 9.2: `GET /api/generation/{task_id}/stream` — SSE 流式输出
  - [x] 9.3: `GET /api/generation/{task_id}` — 获取完整结果
  - [x] 9.4: `POST /api/generation/{task_id}/optimize` — 优化建议（SSE）
  - [x] 9.5: `GET /api/generation/history` — 生成历史
  - [x] 9.6: `DELETE /api/generation/{task_id}` — 删除记录

- [x] Task 10: 重构 `search/api.py` 检索 API 路由
  - [x] 10.1: `GET /api/search` 对接 SirchmunkService，支持 `mode` 参数
  - [x] 10.2: 定义新的响应模型（包含来源文件和相关性信息）

- [x] Task 11: 重构 `main.py` 为模块化路由注册
  - [x] 11.1: 将现有端点拆分到 `documents/api.py`、`templates/api.py`
  - [x] 11.2: 在 `main.py` 中注册所有子路由（include_router）
  - [x] 11.3: 保留 CORS 中间件、生命周期事件、日志配置

## Phase 4: 前端

- [x] Task 12: 实现 `CreateDocument.vue` 公文创作工作台
  - [x] 12.1: 左侧面板 — 公文类型选择、主题输入、参考文档多选、参数配置（字数/风格/检索模式）
  - [x] 12.2: 右侧面板 — SSE 实时预览区域（逐字显示）+ 参考来源展示
  - [x] 12.3: 操作按钮 — 重新生成、优化建议、格式校验、导出
  - [ ] 12.4: 底部知识库面板 — 展示相关 KnowledgeCluster 卡片（待 Sirchmunk 知识库 API 完善）

- [x] Task 13: 扩展前端路由
  - [x] 13.1: 添加 `/create` 路由 → CreateDocument.vue
  - [x] 13.2: 添加 `/create/:id` 路由 → CreateDocument.vue（编辑模式）
  - [x] 13.3: 在 App.vue 导航栏添加"公文创作"入口

## Phase 5: 依赖与配置

- [x] Task 14: 更新 `pyproject.toml` 依赖
  - [x] 14.1: 添加 `sirchmunk>=0.0.2`（已存在）
  - [x] 14.2: 添加 `sqlalchemy>=2.0.0`
  - [x] 14.3: 添加 `python-json-logger>=2.0.0`
  - [x] 14.4: 添加 `pydantic-settings>=2.0.0`
  - [x] 14.5: 运行 `uv sync` 安装依赖

- [x] Task 15: 创建 `.env.example` 环境变量模板
  - [x] 15.1: 列出所有配置项及默认值说明

# Task Dependencies

- Task 2 depends on Task 1
- Task 3 depends on Task 4, Task 5, Task 7
- Task 4 depends on Task 1
- Task 5 depends on Task 1
- Task 7 depends on Task 4, Task 5, Task 6
- Task 8 depends on Task 7
- Task 9 depends on Task 8
- Task 10 depends on Task 4
- Task 11 depends on Task 9, Task 10
- Task 12 depends on Task 9
- Task 13 depends on Task 12
- Task 14: 独立，可尽早执行
- Task 15: 独立，可尽早执行
