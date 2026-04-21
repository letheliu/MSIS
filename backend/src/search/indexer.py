from pathlib import Path
from typing import Dict, List
import shutil
import logging

logger = logging.getLogger(__name__)

class DocumentIndexer:
    """文档索引器"""

    def __init__(self, output_dir: str = "./data/indexed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.supported_formats = {'.txt', '.md', '.json', '.docx', '.pdf'}

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
                    logger.info(f"索引成功: {file_path.name}")
                except (IOError, PermissionError, OSError) as e:
                    error_msg = f"索引文件失败 {file_path.name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

        logger.info(f"索引完成: 总计 {total}, 成功 {success}, 失败 {len(errors)}")
        return {"total": total, "success": success, "errors": errors}

    def _is_supported_format(self, file_path: Path) -> bool:
        """检查是否支持的格式"""
        return file_path.suffix.lower() in self.supported_formats

    def _index_file(self, file_path: Path) -> str:
        """索引单个文件，返回目标文件路径"""
        target = self.output_dir / file_path.name

        # 避免文件覆盖
        counter = 1
        original_target = target
        while target.exists():
            target = original_target.with_name(f"{original_target.stem}_{counter}{original_target.suffix}")
            counter += 1

        # 复制文件
        shutil.copy2(file_path, target)
        return str(target)

    def remove_file(self, file_name: str) -> bool:
        """从索引中移除文件"""
        target = self.output_dir / file_name
        if target.exists():
            target.unlink()
            logger.info(f"从索引中移除: {file_name}")
            return True
        return False

    def get_indexed_files(self) -> List[Dict]:
        """获取已索引的文件列表"""
        files = []
        for file_path in self.output_dir.glob("*"):
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "path": str(file_path)
                })
        return files
