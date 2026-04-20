import json
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """文档库配置管理器"""

    DEFAULT_CONFIG = {
        "document_path": "./data/sample_docs",
        "index_path": "./data/indexed",
        "auto_reindex": True,
        "supported_formats": [".txt", ".md", ".json", ".docx", ".pdf"]
    }

    def __init__(self, config_path: str = "backend/config/document_library.json"):
        self.config_path = Path(config_path)

    def load_config(self) -> Dict[str, Any]:
        """加载配置，如果不存在则创建默认配置"""
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 确保所有默认字段都存在
                for key, value in self.DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except (json.JSONDecodeError, IOError):
            return self.DEFAULT_CONFIG.copy()

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新配置"""
        config = self.load_config()
        config.update(updates)
        self._save_config(config)
        return config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
