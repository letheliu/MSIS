import pytest
import json
from pathlib import Path
from src.documents.config import ConfigManager


def test_config_manager_load_default():
    """测试加载默认配置"""
    config_file = Path("backend/config/document_library.json")
    if config_file.exists():
        config_file.unlink()

    manager = ConfigManager()
    config = manager.load_config()

    assert config["document_path"] == "./data/sample_docs"
    assert config["index_path"] == "./data/indexed"
    assert config["auto_reindex"] is True
    assert ".txt" in config["supported_formats"]


def test_config_manager_update_path():
    """测试更新配置"""
    manager = ConfigManager()
    new_path = "./custom_docs"
    manager.update_config({"document_path": new_path})

    config = manager.load_config()
    assert config["document_path"] == new_path

    # 恢复默认
    manager.update_config({"document_path": "./data/sample_docs"})
