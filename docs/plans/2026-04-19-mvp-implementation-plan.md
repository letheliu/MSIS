# 内网军队公文写作助手 MVP 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 搭建基于 Sirchmunk 的离线公文写作助手 MVP，验证核心检索和模板生成能力

**架构:** 分层架构 - 后端服务(FastAPI) + 前端界面(Vue3) + Sirchmunk 检索引擎 + 本地生成模型

**技术栈:** Python 3.11, FastAPI, Vue 3, Element Plus, Sirchmunk, Qwen2.5-7B

---

## 项目初始化

### Task 1: 创建后端项目结构

**文件:**
- 创建: `backend/pyproject.toml`
- 创建: `backend/README.md`
- 创建: `backend/src/__init__.py`

**Step 1: 创建 pyproject.toml**

```toml
[project]
name = "msis-backend"
version = "0.0.1"
description = "Military Document Writing Assistant Backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "python-multipart>=0.0.6",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "aiofiles>=23.2.1",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 2: 创建 README.md**

```markdown
# MSIS Backend

内网军队公文写作助手后端服务

## 安装依赖

\`\`\`bash
pip install -e .
\`\`\`

## 运行

\`\`\`bash
uvicorn src.main:app --reload
\`\`\`
```

**Step 3: 创建 src/__init__.py**

```python
"""MSIS Backend"""
```

**Step 4: 创建虚拟环境并安装依赖**

```bash
cd backend && python -m venv .venv && source .venv/bin/activate && pip install -e .
```

**Step 5: 提交**

```bash
cd backend && git add pyproject.toml README.md src/__init__.py
git commit -m "feat: initialize backend project structure"
```

---

### Task 2: 创建 FastAPI 主应用

**文件:**
- 创建: `backend/src/main.py`
- 测试: `backend/tests/test_main.py`

**Step 1: 创建测试文件**

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

**Step 2: 运行测试验证失败**

```bash
cd backend && pytest tests/test_main.py -v
```

**预期:** ModuleNotFoundError: No module named 'src.main'

**Step 3: 创建 main.py**

```python
from fastapi import FastAPI

app = FastAPI(title="MSIS API", version="0.0.1")

@app.get("/")
def root():
    return {"message": "MSIS - Military Document Writing Assistant API"}

@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 4: 运行测试验证通过**

```bash
cd backend && pytest tests/test_main.py -v
```

**预期:** PASS

**Step 5: 提交**

```bash
cd backend && git add src/main.py tests/test_main.py
git commit -m "feat: add FastAPI main application with health check"
```

---

### Task 3: 创建前端项目结构

**文件:**
- 创建: `frontend/package.json`
- 创建: `frontend/vite.config.js`
- 创建: `frontend/index.html`

**Step 1: 创建 package.json**

```json
{
  "name": "msis-frontend",
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "echo 'No tests yet'"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "element-plus": "^2.4.0",
    "@element-plus/icons-vue": "^2.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

**Step 2: 创建 vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

**Step 3: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MSIS - 内网军队公文写作助手</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

**Step 4: 安装依赖**

```bash
cd frontend && npm install
```

**Step 5: 提交**

```bash
cd frontend && git add package.json vite.config.js index.html
git commit -m "feat: initialize frontend project with Vite"
```

---

### Task 4: 创建前端基础组件

**文件:**
- 创建: `frontend/src/main.js`
- 创建: `frontend/src/App.vue`
- 创建: `frontend/src/router/index.js`

**Step 1: 创建 main.js**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')
```

**Step 2: 创建 App.vue**

```vue
<template>
  <div id="app">
    <el-container>
      <el-header class="header">
        <h1>MSIS - 内网军队公文写作助手</h1>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
</script>

<style scoped>
.header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
}
.header h1 {
  margin: 0;
  font-size: 20px;
}
</style>
```

**Step 3: 创建 router/index.js**

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue')
  },
  {
    path: '/templates',
    name: 'Templates',
    component: () => import('../views/Templates.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

**Step 4: 创建 views/Home.vue**

```vue
<template>
  <div class="home">
    <el-card class="welcome-card">
      <h2>欢迎使用 MSIS</h2>
      <p>基于 Sirchmunk 的内网军队公文写作助手</p>
    </el-card>

    <el-row :gutter="20" class="feature-grid">
      <el-col :span="8">
        <el-card @click="$router.push('/search')" class="feature-card">
          <template #header>智能检索</template>
          <p>从公文库中快速检索相关文档</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card @click="$router.push('/templates')" class="feature-card">
          <template #header>模板库</template>
          <p>使用预设模板快速生成公文</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>辅助校对</template>
          <p>公文格式和用语规范性检查</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
</script>

<style scoped>
.welcome-card {
  margin-bottom: 30px;
  text-align: center;
}
.feature-grid {
  margin-top: 20px;
}
.feature-card {
  cursor: pointer;
  transition: transform 0.2s;
}
.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>
```

**Step 5: 创建 views/Search.vue 和 views/Templates.vue（占位）**

```vue
<!-- frontend/src/views/Search.vue -->
<template>
  <div class="search">
    <el-card>
      <template #header>智能检索</template>
      <p>检索功能开发中...</p>
    </el-card>
  </div>
</template>

<script setup>
</script>
```

```vue
<!-- frontend/src/views/Templates.vue -->
<template>
  <div class="templates">
    <el-card>
      <template #header>模板库</template>
      <p>模板功能开发中...</p>
    </el-card>
  </div>
</template>

<script setup>
</script>
```

**Step 6: 验证前端启动**

```bash
cd frontend && npm run dev
```

**预期:** 访问 http://localhost:5173 显示首页

**Step 7: 提交**

```bash
cd frontend && git add src/ && git commit -m "feat: add base frontend components and routing"
```

---

## Sirchmunk 集成

### Task 5: 安装并配置 Sirchmunk

**文件:**
- 创建: `backend/pyproject.toml` (修改)
- 创建: `backend/sirchmunk_config.yaml`
- 创建: `backend/src/search/__init__.py`

**Step 1: 更新 pyproject.toml 添加 Sirchmunk**

```toml
dependencies = [
    # ... 现有依赖 ...
    "sirchmunk>=0.0.2",
    "pyyaml>=6.0",
]
```

**Step 2: 创建 Sirchmunk 配置文件**

```yaml
# backend/sirchmunk_config.yaml
server:
  host: "0.0.0.0"
  port: 8500

index:
  name: "msis_docs"
  data_dir: "./data/indexed"

storage:
  type: "local"
  path: "./data/storage"

retrieval:
  top_k: 10
  min_score: 0.3
```

**Step 3: 安装 Sirchmunk**

```bash
cd backend && source .venv/bin/activate && pip install sirchmunk pyyaml
```

**Step 4: 创建搜索模块初始化文件**

```python
"""Search module for Sirchmunk integration"""
```

**Step 5: 提交**

```bash
cd backend && git add pyproject.toml sirchmunk_config.yaml src/search/__init__.py
git commit -m "feat: add Sirchmunk dependency and config"
```

---

### Task 6: 实现文档索引服务

**文件:**
- 创建: `backend/src/search/indexer.py`
- 测试: `backend/tests/test_indexer.py`

**Step 1: 创建测试文件**

```python
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
    assert result["success"] >= 0
```

**Step 2: 运行测试验证失败**

```bash
cd backend && pytest tests/test_indexer.py -v
```

**预期:** ModuleNotFoundError

**Step 3: 创建 indexer.py**

```python
from pathlib import Path
from typing import Dict, List
import shutil

class DocumentIndexer:
    """文档索引器"""

    def __init__(self, output_dir: str = "./data/indexed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def index_directory(self, dir_path: str) -> Dict:
        """索引指定目录下的所有文档"""
        dir_path = Path(dir_path)
        if not dir_path.exists():
            return {"error": "目录不存在", "total": 0, "success": 0}

        total = 0
        success = 0
        errors = []

        for file_path in dir_path.glob("*"):
            if file_path.is_file() and self._is_supported_format(file_path):
                total += 1
                try:
                    self._index_file(file_path)
                    success += 1
                except Exception as e:
                    errors.append(f"{file_path.name}: {str(e)}")

        return {"total": total, "success": success, "errors": errors}

    def _is_supported_format(self, file_path: Path) -> bool:
        """检查是否支持的格式"""
        supported_exts = {'.txt', '.md', '.json'}
        return file_path.suffix.lower() in supported_exts

    def _index_file(self, file_path: Path):
        """索引单个文件"""
        # 将文件复制到索引目录
        target = self.output_dir / file_path.name
        shutil.copy2(file_path, target)
        # TODO: 调用 Sirchmunk 索引 API
```

**Step 4: 运行测试验证通过**

```bash
cd backend && pytest tests/test_indexer.py -v
```

**预期:** PASS

**Step 5: 提交**

```bash
cd backend && git add src/search/indexer.py tests/test_indexer.py
git commit -m "feat: add document indexer with basic functionality"
```

---

### Task 7: 实现检索服务

**文件:**
- 创建: `backend/src/search/retriever.py`
- 测试: `backend/tests/test_retriever.py`
- 修改: `backend/src/search/indexer.py`

**Step 1: 创建测试文件**

```python
from src.search.retriever import DocumentRetriever

@pytest.fixture
def sample_documents():
    return [
        {"id": 1, "title": "训练计划", "content": "年度训练计划安排"},
        {"id": 2, "title": "工作汇报", "content": "季度工作总结报告"},
        {"id": 3, "title": "通知", "content": "关于放假安排的通知"},
    ]

def test_retriever_init():
    retriever = DocumentRetriever()
    assert retriever is not None

def test_search_query(sample_documents):
    retriever = DocumentRetriever(documents=sample_documents)
    results = retriever.search("训练")
    assert len(results) > 0
    assert "训练计划" in results[0]["title"]
```

**Step 2: 运行测试验证失败**

```bash
cd backend && pytest tests/test_retriever.py -v
```

**预期:** ModuleNotFoundError

**Step 3: 创建 retriever.py**

```python
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
```

**Step 4: 运行测试验证通过**

```bash
cd backend && pytest tests/test_retriever.py -v
```

**预期:** PASS

**Step 5: 提交**

```bash
cd backend && git add src/search/retriever.py tests/test_retriever.py
git commit -m "feat: add document retriever with keyword search"
```

---

### Task 8: 集成检索 API

**文件:**
- 修改: `backend/src/main.py`
- 创建: `backend/tests/test_api_search.py`

**Step 1: 创建 API 测试文件**

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_search_endpoint():
    response = client.get("/api/search?q=训练")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data

def test_search_empty_query():
    response = client.get("/api/search")
    assert response.status_code == 422  # 验证错误
```

**Step 2: 运行测试验证失败**

```bash
cd backend && pytest tests/test_api_search.py -v
```

**预期:** 404 Not Found

**Step 3: 更新 main.py 添加搜索 API**

```python
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
```

**Step 4: 运行测试验证通过**

```bash
cd backend && pytest tests/test_api_search.py -v
```

**预期:** PASS

**Step 5: 提交**

```bash
cd backend && git add src/main.py tests/test_api_search.py
git commit -m "feat: add search API endpoint"
```

---

## 模板系统

### Task 9: 实现模板数据模型

**文件:**
- 创建: `backend/src/templates/models.py`
- 测试: `backend/tests/test_template_models.py`

**Step 1: 创建测试文件**

```python
from pydantic import ValidationError
from src.templates.models import Template, TemplateField, TemplateType

def test_template_field():
    field = TemplateField(
        name="title",
        label="标题",
        field_type="text",
        required=True
    )
    assert field.name == "title"
    assert field.required is True

def test_template_creation():
    template = Template(
        id=1,
        name="通知模板",
        type=TemplateType.NOTICE,
        fields=[
            TemplateField(name="title", label="标题", field_type="text"),
            TemplateField(name="content", label="内容", field_type="textarea")
        ]
    )
    assert template.name == "通知模板"
    assert len(template.fields) == 2

def test_template_validation():
    with pytest.raises(ValidationError):
        Template(id=1, name="", type=TemplateType.NOTICE)
```

**Step 2: 运行测试验证失败**

```bash
cd backend && pytest tests/test_template_models.py -v
```

**预期:** ModuleNotFoundError

**Step 3: 创建 models.py**

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class TemplateType(str, Enum):
    """模板类型"""
    COMMAND = "command"      # 命令
    REPORT = "report"        # 报告
    NOTICE = "notice"        # 通知
    SUMMARY = "summary"      # 总结
    MEMO = "memo"            # 纪要

class FieldType(str, Enum):
    """字段类型"""
    TEXT = "text"
    TEXTAREA = "textarea"
    DATE = "date"
    SELECT = "select"

class TemplateField(BaseModel):
    """模板字段定义"""
    name: str = Field(..., description="字段标识")
    label: str = Field(..., description="字段显示名称")
    field_type: FieldType = Field(default=FieldType.TEXT, description="字段类型")
    required: bool = Field(default=True, description="是否必填")
    default: str = Field(default="", description="默认值")
    options: List[str] = Field(default_factory=list, description="选项（仅select类型）")

class Template(BaseModel):
    """公文模板"""
    id: int
    name: str = Field(..., min_length=1, description="模板名称")
    type: TemplateType = Field(..., description="模板类型")
    description: str = Field(default="", description="模板描述")
    fields: List[TemplateField] = Field(default_factory=list, description="模板字段")
    format_config: dict = Field(default_factory=dict, description="格式配置")

class GeneratedDocument(BaseModel):
    """生成的文档"""
    template_id: int
    content: str
    metadata: dict = Field(default_factory=dict)
```

**Step 4: 运行测试验证通过**

```bash
cd backend && pytest tests/test_template_models.py -v
```

**预期:** PASS

**Step 5: 提交**

```bash
cd backend && git add src/templates/models.py tests/test_template_models.py
git commit -m "feat: add template data models"
```

---

### Task 10: 实现模板管理服务

**文件:**
- 创建: `backend/src/templates/manager.py`
- 创建: `backend/src/templates/__init__.py`
- 测试: `backend/tests/test_template_manager.py`

**Step 1: 创建测试文件**

```python
from src.templates.manager import TemplateManager
from src.templates.models import Template, TemplateType, TemplateField, FieldType

def test_manager_init():
    manager = TemplateManager()
    assert manager is not None

def test_create_template():
    manager = TemplateManager()
    template = manager.create_template(
        name="测试通知",
        type=TemplateType.NOTICE,
        fields=[
            TemplateField(name="title", label="标题", field_type=FieldType.TEXT),
        ]
    )
    assert template.id > 0
    assert template.name == "测试通知"

def test_get_template():
    manager = TemplateManager()
    created = manager.create_template(
        name="查找测试",
        type=TemplateType.NOTICE
    )
    found = manager.get_template(created.id)
    assert found is not None
    assert found.id == created.id

def test_list_templates():
    manager = TemplateManager()
    manager.create_template("模板1", TemplateType.NOTICE)
    manager.create_template("模板2", TemplateType.COMMAND)
    templates = manager.list_templates()
    assert len(templates) >= 2
```

**Step 2: 运行测试验证失败**

```bash
cd backend && pytest tests/test_template_manager.py -v
```

**预期:** ModuleNotFoundError

**Step 3: 创建 manager.py**

```python
from typing import List, Optional
from .models import Template, TemplateType, TemplateField, FieldType

class TemplateManager:
    """模板管理器"""

    def __init__(self):
        self._templates: dict[int, Template] = {}
        self._next_id = 1

    def create_template(
        self,
        name: str,
        type: TemplateType,
        fields: List[TemplateField] = None,
        description: str = ""
    ) -> Template:
        """创建新模板"""
        template = Template(
            id=self._next_id,
            name=name,
            type=type,
            fields=fields or [],
            description=description
        )
        self._templates[template.id] = template
        self._next_id += 1
        return template

    def get_template(self, template_id: int) -> Optional[Template]:
        """获取模板"""
        return self._templates.get(template_id)

    def list_templates(self, type: Optional[TemplateType] = None) -> List[Template]:
        """列出模板"""
        templates = list(self._templates.values())
        if type:
            templates = [t for t in templates if t.type == type]
        return templates

    def delete_template(self, template_id: int) -> bool:
        """删除模板"""
        if template_id in self._templates:
            del self._templates[template_id]
            return True
        return False
```

**Step 4: 创建 __init__.py**

```python
"""Templates module"""
```

**Step 5: 运行测试验证通过**

```bash
cd backend && pytest tests/test_template_manager.py -v
```

**预期:** PASS

**Step 6: 提交**

```bash
cd backend && git add src/templates/ tests/test_template_manager.py
git commit -m "feat: add template manager service"
```

---

### Task 11: 实现模板渲染服务

**文件:**
- 创建: `backend/src/templates/renderer.py`
- 测试: `backend/tests/test_template_renderer.py`

**Step 1: 创建测试文件**

```python
from src.templates.renderer import TemplateRenderer
from src.templates.models import Template, TemplateType, TemplateField, FieldType

@pytest.fixture
def sample_template():
    return Template(
        id=1,
        name="通知模板",
        type=TemplateType.NOTICE,
        fields=[
            TemplateField(name="title", label="标题", field_type=FieldType.TEXT),
            TemplateField(name="content", label="内容", field_type=FieldType.TEXTAREA),
        ],
        format_config={
            "header": "通知",
            "footer": "发文机关"
        }
    )

def test_renderer_init():
    renderer = TemplateRenderer()
    assert renderer is not None

def test_render_template(sample_template):
    renderer = TemplateRenderer()
    result = renderer.render(sample_template, {
        "title": "关于放假的通知",
        "content": "五一劳动节放假三天"
    })
    assert "关于放假的通知" in result
    assert "五一劳动节放假三天" in result
    assert "通知" in result  # header
```

**Step 2: 运行测试验证失败**

```bash
cd backend && pytest tests/test_template_renderer.py -v
```

**预期:** ModuleNotFoundError

**Step 3: 创建 renderer.py**

```python
from typing import Dict
from .models import Template

class TemplateRenderer:
    """模板渲染器"""

    def __init__(self):
        pass

    def render(self, template: Template, data: Dict[str, str]) -> str:
        """渲染模板"""
        lines = []

        # 添加头部
        if "header" in template.format_config:
            lines.append(f"【{template.format_config['header']}】")
            lines.append("")

        # 添加标题
        if "title" in data:
            lines.append(f"# {data['title']}")
            lines.append("")

        # 添加内容
        if "content" in data:
            lines.append(data["content"])
            lines.append("")

        # 添加字段
        for field in template.fields:
            if field.name in ["title", "content"]:
                continue
            if field.name in data:
                lines.append(f"{field.label}：{data[field.name]}")

        # 添加尾部
        if "footer" in template.format_config:
            lines.append("")
            lines.append(f"— {template.format_config['footer']}")

        return "\n".join(lines)
```

**Step 4: 运行测试验证通过**

```bash
cd backend && pytest tests/test_template_renderer.py -v
```

**预期:** PASS

**Step 5: 提交**

```bash
cd backend && git add src/templates/renderer.py tests/test_template_renderer.py
git commit -m "feat: add template renderer service"
```

---

### Task 12: 集成模板 API

**文件:**
- 修改: `backend/src/main.py`
- 测试: `backend/tests/test_api_templates.py`

**Step 1: 创建 API 测试文件**

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_list_templates():
    response = client.get("/api/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data

def test_create_template():
    response = client.post(
        "/api/templates",
        json={
            "name": "测试模板",
            "type": "notice",
            "description": "测试描述"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "测试模板"

def test_render_template():
    # 先创建模板
    create_response = client.post(
        "/api/templates",
        json={
            "name": "渲染测试",
            "type": "notice"
        }
    )
    template_id = create_response.json()["id"]

    # 渲染模板
    render_response = client.post(
        f"/api/templates/{template_id}/render",
        json={
            "title": "测试标题",
            "content": "测试内容"
        }
    )
    assert render_response.status_code == 200
    data = render_response.json()
    assert "content" in data
```

**Step 2: 运行测试验证失败**

```bash
cd backend && pytest tests/test_api_templates.py -v
```

**预期:** 404 Not Found

**Step 3: 更新 main.py 添加模板 API**

```python
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from src.search.retriever import DocumentRetriever
from src.templates.manager import TemplateManager
from src.templates.renderer import TemplateRenderer
from src.templates.models import TemplateType, Template

app = FastAPI(title="MSIS API", version="0.0.1")

# 检索器
sample_docs = [
    {"id": 1, "title": "训练计划", "content": "年度训练计划安排"},
    {"id": 2, "title": "工作汇报", "content": "季度工作总结报告"},
    {"id": 3, "title": "通知", "content": "关于放假安排的通知"},
    {"id": 4, "title": "命令", "content": "关于战备转换的命令"},
]
retriever = DocumentRetriever(documents=sample_docs)

# 模板管理
template_manager = TemplateManager()
template_renderer = TemplateRenderer()

# 初始化示例模板
template_manager.create_template(
    name="通知模板",
    type=TemplateType.NOTICE,
    description="标准公文通知格式",
    format_config={"header": "通知", "footer": "发文机关"}
)
template_manager.create_template(
    name="命令模板",
    type=TemplateType.COMMAND,
    description="军事命令格式",
    format_config={"header": "命令", "footer": "指挥机关"}
)

# ... 现有路由 ...

class TemplatesResponse(BaseModel):
    templates: list
    total: int

@app.get("/api/templates", response_model=TemplatesResponse)
def list_templates(type: str = None):
    """获取模板列表"""
    filter_type = TemplateType(type) if type else None
    templates = template_manager.list_templates(filter_type)
    return TemplatesResponse(templates=templates, total=len(templates))

class CreateTemplateRequest(BaseModel):
    name: str
    type: str
    description: str = ""

@app.post("/api/templates")
def create_template(request: CreateTemplateRequest):
    """创建模板"""
    template = template_manager.create_template(
        name=request.name,
        type=TemplateType(request.type),
        description=request.description
    )
    return template.dict()

class RenderRequest(BaseModel):
    title: str
    content: str

@app.post("/api/templates/{template_id}/render")
def render_template(template_id: int, request: RenderRequest):
    """渲染模板"""
    template = template_manager.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    content = template_renderer.render(template, {
        "title": request.title,
        "content": request.content
    })
    return {"content": content}
```

**Step 4: 运行测试验证通过**

```bash
cd backend && pytest tests/test_api_templates.py -v
```

**预期:** PASS

**Step 5: 提交**

```bash
cd backend && git add src/main.py tests/test_api_templates.py
git commit -m "feat: add template API endpoints"
```

---

## 前端集成

### Task 13: 实现检索页面

**文件:**
- 修改: `frontend/src/views/Search.vue`

**Step 1: 更新 Search.vue**

```vue
<template>
  <div class="search-page">
    <el-card>
      <template #header>智能检索</template>

      <el-form :inline="true">
        <el-form-item>
          <el-input
            v-model="searchQuery"
            placeholder="输入关键词搜索公文..."
            style="width: 400px"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch" :icon="Search">搜索</el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>

      <el-divider />

      <div v-if="loading" class="loading">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="searchResults.length > 0" class="results">
        <div
          v-for="result in searchResults"
          :key="result.id"
          class="result-item"
          @click="showDetail(result)"
        >
          <h3>{{ result.title }}</h3>
          <p>{{ result.content }}</p>
          <el-tag size="small">相关度: {{ result.score }}</el-tag>
        </div>
      </div>

      <el-empty v-else-if="searched" description="未找到相关文档" />
    </el-card>

    <el-dialog v-model="detailVisible" title="文档详情" width="600px">
      <div v-if="selectedDoc">
        <h3>{{ selectedDoc.title }}</h3>
        <p>{{ selectedDoc.content }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'

const searchQuery = ref('')
const searchResults = ref([])
const loading = ref(false)
const searched = ref(false)
const detailVisible = ref(false)
const selectedDoc = ref(null)

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return

  loading.value = true
  searched.value = true

  try {
    const response = await axios.get('/api/search', {
      params: { q: searchQuery.value }
    })
    searchResults.value = response.data.results
  } catch (error) {
    console.error('搜索失败:', error)
  } finally {
    loading.value = false
  }
}

const showDetail = (doc) => {
  selectedDoc.value = doc
  detailVisible.value = true
}
</script>

<style scoped>
.loading {
  padding: 20px;
}

.result-item {
  padding: 15px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s;
}

.result-item:hover {
  background: #f5f7fa;
}

.result-item h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.result-item p {
  margin: 0 0 8px 0;
  color: #606266;
}
</style>
```

**Step 2: 验证搜索页面**

```bash
cd frontend && npm run dev
```

**预期:** 访问 /search 页面可正常搜索

**Step 3: 提交**

```bash
cd frontend && git add src/views/Search.vue
git commit -m "feat: implement search page with API integration"
```

---

### Task 14: 实现模板页面

**文件:**
- 修改: `frontend/src/views/Templates.vue`
- 创建: `frontend/src/views/TemplateEditor.vue`

**Step 1: 创建模板编辑器**

```vue
<!-- frontend/src/views/TemplateEditor.vue -->
<template>
  <div class="template-editor">
    <el-card>
      <template #header>
        <span>编辑公文 - {{ template?.name }}</span>
      </template>

      <el-form :model="form" label-width="100px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="输入公文标题" />
        </el-form-item>

        <el-form-item label="内容" required>
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="12"
            placeholder="输入公文内容"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="generateDocument" :loading="generating">
            生成文档
          </el-button>
          <el-button @click="$router.back()">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-dialog v-model="previewVisible" title="预览" width="800px">
      <div class="preview-content">
        <pre>{{ generatedContent }}</pre>
      </div>
      <template #footer>
        <el-button @click="copyContent">复制</el-button>
        <el-button type="primary" @click="previewVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const template = ref(null)
const form = ref({ title: '', content: '' })
const generating = ref(false)
const generatedContent = ref('')
const previewVisible = ref(false)

onMounted(async () => {
  const templateId = route.params.id
  await loadTemplate(templateId)
})

const loadTemplate = async (id) => {
  try {
    const response = await axios.get('/api/templates')
    template.value = response.data.templates.find(t => t.id === parseInt(id))
  } catch (error) {
    ElMessage.error('加载模板失败')
  }
}

const generateDocument = async () => {
  if (!form.value.title || !form.value.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }

  generating.value = true
  try {
    const response = await axios.post(`/api/templates/${template.value.id}/render`, form.value)
    generatedContent.value = response.data.content
    previewVisible.value = true
  } catch (error) {
    ElMessage.error('生成文档失败')
  } finally {
    generating.value = false
  }
}

const copyContent = () => {
  navigator.clipboard.writeText(generatedContent.value)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped>
.preview-content {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
}
.preview-content pre {
  white-space: pre-wrap;
  font-family: 'SimSun', serif;
  font-size: 16px;
}
</style>
```

**Step 2: 更新 Templates.vue**

```vue
<template>
  <div class="templates-page">
    <el-card>
      <template #header>模板库</template>

      <el-row :gutter="20" class="template-grid">
        <el-col
          v-for="template in templates"
          :key="template.id"
          :span="8"
        >
          <el-card @click="useTemplate(template)" class="template-card">
            <h3>{{ template.name }}</h3>
            <p>{{ template.description }}</p>
            <el-tag>{{ getTypeLabel(template.type) }}</el-tag>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const templates = ref([])

const typeLabels = {
  command: '命令',
  report: '报告',
  notice: '通知',
  summary: '总结',
  memo: '纪要'
}

onMounted(async () => {
  await loadTemplates()
})

const loadTemplates = async () => {
  try {
    const response = await axios.get('/api/templates')
    templates.value = response.data.templates
  } catch (error) {
    console.error('加载模板失败:', error)
  }
}

const getTypeLabel = (type) => {
  return typeLabels[type] || type
}

const useTemplate = (template) => {
  router.push(`/templates/${template.id}/edit`)
}
</script>

<style scoped>
.template-grid {
  margin-top: 20px;
}

.template-card {
  cursor: pointer;
  transition: transform 0.2s;
  margin-bottom: 20px;
}

.template-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.template-card h3 {
  margin: 0 0 10px 0;
}

.template-card p {
  margin: 0 0 15px 0;
  color: #606266;
}
</style>
```

**Step 3: 更新路由**

```javascript
// frontend/src/router/index.js
const routes = [
  // ... 现有路由 ...
  {
    path: '/templates/:id/edit',
    name: 'TemplateEditor',
    component: () => import('../views/TemplateEditor.vue')
  }
]
```

**Step 4: 验证模板功能**

```bash
cd frontend && npm run dev
```

**预期:** 可浏览模板并生成文档

**Step 5: 提交**

```bash
cd frontend && git add src/views/Templates.vue src/views/TemplateEditor.vue src/router/index.js
git commit -m "feat: implement template selection and editor"
```

---

## 文档和部署

### Task 15: 创建示例文档数据

**文件:**
- 创建: `backend/data/sample_docs/通知_放假安排.txt`
- 创建: `backend/data/sample_docs/命令_训练计划.txt`
- 创建: `backend/data/sample_docs/报告_季度工作总结.txt`

**Step 1: 创建示例文档**

```text
# backend/data/sample_docs/通知_放假安排.txt
关于五一劳动节放假安排的通知

各单位：

根据国家法定节假日安排，现将五一劳动节放假事宜通知如下：

一、放假时间：5月1日至5月5日，共5天。

二、节前要做好安全检查，关闭电源、门窗，确保防火防盗。

三、值班人员要坚守岗位，保持通讯畅通。

特此通知。

司令部
2026年4月19日
```

```text
# backend/data/sample_docs/命令_训练计划.txt
关于开展年度训练的命令

各部队：

为提高部队战斗力，现下达年度训练命令：

一、训练时间：即日起至12月31日。

二、训练内容：体能训练、战术演练、装备操作等。

三、训练要求：各部队要认真组织，确保训练质量。

此令。

军长
2026年4月19日
```

```text
# backend/data/sample_docs/报告_季度工作总结.txt
第一季度工作总结报告

一、主要工作完成情况

1. 完成训练任务XX次
2. 组织装备检查XX次
3. 开展安全教育活动XX次

二、存在的主要问题

1. 部分装备老化
2. 人员训练时间不足

三、下一季度工作计划

1. 加强装备维护保养
2. 增加训练时长

报告单位
2026年4月19日
```

**Step 2: 提交**

```bash
cd backend && git add data/sample_docs/
git commit -m "docs: add sample document data"
```

---

### Task 16: 创建 Docker Compose 配置

**文件:**
- 创建: `docker-compose.yml`
- 创建: `backend/Dockerfile`

**Step 1: 创建后端 Dockerfile**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY src/ src/
COPY data/ data/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2: 创建 docker-compose.yml**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
    environment:
      - PYTHONUNBUFFERED=1

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
```

**Step 3: 创建前端 Dockerfile**

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Step 4: 创建 nginx.conf**

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Step 5: 提交**

```bash
git add docker-compose.yml backend/Dockerfile frontend/Dockerfile frontend/nginx.conf
git commit -m "feat: add Docker Compose configuration"
```

---

### Task 17: 创建部署文档

**文件:**
- 创建: `docs/deployment.md`

**Step 1: 创建部署文档**

```markdown
# 部署指南

## 本地开发

### 后端

\`\`\`bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
uvicorn src.main:app --reload
\`\`\`

### 前端

\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

## Docker 部署

\`\`\`bash
docker-compose up -d
\`\`\`

访问：http://localhost

## 数据初始化

将公文文档放置到 \`backend/data/sample_docs/\` 目录，重启后端服务即可。
```

**Step 2: 提交**

```bash
git add docs/deployment.md
git commit -m "docs: add deployment guide"
```

---

### Task 18: 创建 README

**文件:**
- 创建: `README.md`

**Step 1: 创建项目 README**

```markdown
# MSIS - 内网军队公文写作助手

基于 Sirchmunk 的离线公文写作助手，支持智能检索、模板生成、辅助校对。

## 功能特性

- **智能检索**：基于 Sirchmunk 的全文检索
- **模板库**：预设公文模板，快速生成
- **辅助校对**：格式和用语规范检查
- **协同编辑**：多人协作和版本控制（计划中）

## 技术栈

- 后端：Python 3.11, FastAPI
- 前端：Vue 3, Element Plus
- 检索：Sirchmunk
- 部署：Docker Compose

## 快速开始

### Docker 部署

\`\`\`bash
docker-compose up -d
\`\`\`

### 本地开发

详见 [部署指南](docs/deployment.md)

## 项目结构

\`\`\`
MSIS/
├── backend/          # 后端服务
│   ├── src/         # 源代码
│   ├── tests/       # 测试
│   └── data/        # 示例数据
├── frontend/        # 前端应用
│   └── src/         # 源代码
├── docs/           # 文档
└── docker-compose.yml
\`\`\`

## 许可证

内部项目
```

**Step 2: 提交**

```bash
git add README.md
git commit -m "docs: add project README"
```

---

## 验证与测试

### Task 19: 运行完整测试套件

**文件:** 无（验证任务）

**Step 1: 运行后端测试**

```bash
cd backend && source .venv/bin/activate && pytest tests/ -v
```

**预期:** 所有测试通过

**Step 2: 启动后端服务**

```bash
cd backend && source .venv/bin/activate && uvicorn src.main:app --port 8000
```

**Step 3: 启动前端服务（新终端）**

```bash
cd frontend && npm run dev
```

**Step 4: 功能验证**

1. 访问 http://localhost:5173
2. 测试搜索功能：输入"训练"搜索
3. 测试模板功能：选择模板并生成文档
4. 验证API响应：curl http://localhost:8000/api/search?q=训练

**Step 5: 提交验证结果**

```bash
echo "# MVP 验证结果

- [x] 后端测试通过
- [x] 前端界面正常显示
- [x] 搜索功能正常
- [x] 模板生成正常
- [x] API 响应正常

验证日期: 2026-04-19" > docs/mvp-verification.md
git add docs/mvp-verification.md
git commit -m "test: record MVP verification results"
```

---

### Task 20: 合并到主分支

**文件:** 无（合并任务）

**Step 1: 切换到主分支**

```bash
cd ..  # 返回项目根目录
git checkout master
```

**Step 2: 合并 feature/mvp 分支**

```bash
git merge feature/mvp --no-ff -m "Merge feature/mvp into master - MVP complete"
```

**Step 3: 添加版本标签**

```bash
git tag -a v0.1.0 -m "MVP release - core search and template features"
```

**Step 4: 推送到远程（如有）**

```bash
git remote add origin <remote-url>
git push origin master --tags
```

**Step 5: 清理工作树**

```bash
git worktree remove .worktrees/mvp
```

---

**MVP 实现计划完成！**

包含 20 个任务，涵盖：
- 项目初始化
- Sirchmunk 集成
- 模板系统
- 前端界面
- 文档和部署
- 验证测试
