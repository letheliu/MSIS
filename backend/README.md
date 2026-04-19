# MSIS Backend

内网军队公文写作助手后端服务

## 安装依赖

```bash
pip install -e .
```

## 运行

```bash
uvicorn src.main:app --reload
```

## 测试

```bash
# 运行所有测试
pytest

# 运行测试并显示详细输出
pytest -v

# 运行特定测试文件
pytest tests/test_example.py
```
