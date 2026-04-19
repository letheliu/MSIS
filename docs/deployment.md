# 部署指南

## 本地开发

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
uvicorn src.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## Docker 部署

```bash
docker-compose up -d
```

访问：http://localhost

## 数据初始化

将公文文档放置到 `backend/data/sample_docs/` 目录，重启后端服务即可。
