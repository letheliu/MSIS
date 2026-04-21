# 文档库增强功能设计

## 概述

增强 MSIS 的文档库功能，支持更多文档格式（docx, pdf）、可配置文档库存储位置、文档动态添加无需重启后端。

## 架构设计

### 后端架构

新增 `DocumentLibrary` 服务类，负责：
1. 文档目录的配置管理（存储在配置文件中）
2. 文件监听（使用 `watchdog` 库）
3. 文档解析（`python-docx` 处理 docx，`pdfplumber` 处理 PDF）
4. 索引更新（调用现有 `DocumentIndexer`）

### 前端架构

新增 `Documents.vue` 页面，提供：
1. 文档库路径配置表单
2. 文件上传区域（支持拖拽和批量上传）
3. 已索引文档列表（显示文件名、大小、索引时间）
4. 手动刷新索引按钮

### API 端点

- `GET /api/documents/config` - 获取当前配置
- `PUT /api/documents/config` - 更新配置
- `POST /api/documents/upload` - 上传文档
- `GET /api/documents/list` - 获取已索引文档列表
- `POST /api/documents/reindex` - 手动触发重新索引

## 数据流与文件监听

### 启动流程

1. 后端启动时读取配置文件（`backend/config/document_library.json`）获取文档库路径
2. 初始化 `DocumentLibrary` 服务，创建 `DocumentIndexer` 和文件监听器
3. 启动时执行一次完整索引，然后开启文件监听

### 文件监听机制

使用 `watchdog.Observer` 监听文档库目录：
- `on_created`：新文件加入，触发增量索引
- `on_modified`：文件被修改，重新索引该文件
- `on_deleted`：文件被删除，从索引中移除

监听器在独立线程中运行，避免阻塞主 API 线程。使用线程安全的队列处理事件。

### 上传流程

1. 前端上传文件到 `POST /api/documents/upload`
2. 后端验证文件格式（支持 `.txt`, `.md`, `.json`, `.docx`, `.pdf`）
3. 保存到配置的文档库目录
4. 立即触发索引更新
5. 返回索引结果

## 文档解析实现

### 解析器接口

```python
class DocumentParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> str:
        """解析文档并返回格式化文本"""
        pass
```

### 各格式解析器

**TextParser** (txt, md, json)：直接读取文件内容，md 文件保留标题语法，json 提取所有字符串值

**DocxParser** (docx)：使用 `python-docx`
- 保留段落层级结构
- 标题输出为 `## 一级标题`、`### 二级标题` 格式
- 列表保留为 `- 列表项` 格式
- 表格转换为 Markdown 表格格式

**PDFParser** (pdf)：使用 `pdfplumber`
- 按页提取文本
- 尝试识别标题（字体较大或加粗的文本）
- 保留段落分隔
- 表格提取并转换为 Markdown 格式

使用 Markdown 标记保留基本格式，便于向量化索引和前端渲染。

## 配置存储与错误处理

### 配置文件

路径：`backend/config/document_library.json`
```json
{
  "document_path": "./data/sample_docs",
  "index_path": "./data/indexed",
  "auto_reindex": true,
  "supported_formats": [".txt", ".md", ".json", ".docx", ".pdf"]
}
```

### 错误处理

1. **解析错误**：单个文件解析失败不影响其他文件，记录错误日志
2. **目录不存在**：自动创建目录并返回提示
3. **权限错误**：返回 403 错误，提示检查权限
4. **格式不支持**：返回 400 错误，列出支持的格式
5. **索引失败**：记录已成功索引的文件，支持断点续传

### 日志记录

所有索引操作记录到 `backend/logs/document_index.log`，包含时间戳、文件路径、操作类型、结果
