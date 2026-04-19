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
        # 检查目标文件是否存在，避免覆盖
        if target.exists():
            # 添加数字后缀避免覆盖
            counter = 1
            while target.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                target = self.output_dir / f"{stem}_{counter}{suffix}"
                counter += 1
        try:
            shutil.copy2(file_path, target)
        except (IOError, PermissionError, OSError) as e:
            raise
        # TODO: 调用 Sirchmunk 索引 API
