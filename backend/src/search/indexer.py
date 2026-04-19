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

        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and self._is_supported_format(file_path):
                total += 1
                try:
                    self._index_file(file_path)
                    success += 1
                except (IOError, PermissionError, OSError) as e:
                    errors.append(f"索引文件失败 {file_path.name}: {str(e)}")

        return {"total": total, "success": success, "errors": errors}

    def _is_supported_format(self, file_path: Path) -> bool:
        """检查是否支持的格式"""
        supported_exts = {'.txt', '.md', '.json'}
        return file_path.suffix.lower() in supported_exts

    def _index_file(self, file_path: Path) -> str:
        """索引单个文件，返回目标文件路径"""
        target = self.output_dir / file_path.name

        # 避免文件覆盖
        counter = 1
        original_target = target
        while target.exists():
            target = original_target.with_name(f"{original_target.stem}_{counter}{original_target.suffix}")
            counter += 1

        # 复制文件，异常由调用者处理
        shutil.copy2(file_path, target)
        return str(target)
        # TODO: 调用 Sirchmunk 索引 API
