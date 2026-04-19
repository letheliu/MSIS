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

```bash
docker-compose up -d
```

### 本地开发

详见 [部署指南](docs/deployment.md)

## 项目结构

```
MSIS/
├── backend/          # 后端服务
│   ├── src/         # 源代码
│   ├── tests/       # 测试
│   └── data/        # 示例数据
├── frontend/        # 前端应用
│   └── src/         # 源代码
├── docs/           # 文档
└── docker-compose.yml
```

## 许可证

内部项目
