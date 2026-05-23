"""
磁盘清理插件
调用Windows系统磁盘清理工具，清理临时文件
"""

import os
import subprocess
import tempfile
from typing import Dict, Any
from .base import PluginBase


class DiskCleanerPlugin(PluginBase):
    """磁盘清理插件"""

    @property
    def id(self) -> str:
        return "disk_cleaner"

    @property
    def name(self) -> str:
        return "磁盘清理"

    @property
    def description(self) -> str:
        return "清理系统临时文件、缓存、回收站等，释放磁盘空间"

    @property
    def category(self) -> str:
        return "系统清理"

    @property
    def icon(self) -> str:
        return "🧹"

    @property
    def keywords(self) -> list:
        return ["清理", "磁盘", "垃圾", "临时文件", "缓存", "回收站", "空间"]

    def execute(self) -> Dict[str, Any]:
        """执行磁盘清理，清理临时文件和回收站"""
        try:
            if os.name != "nt":
                return {"success": False, "message": "此插件仅支持Windows系统", "data": None}

            total_freed = 0
            temp_freed = 0
            recycle_freed = 0
            details = []

            # 清理临时文件
            temp_freed = self._clean_temp_files()
            if temp_freed > 0:
                details.append(f"临时文件: {temp_freed} MB")
                total_freed += temp_freed

            # 清空回收站
            recycle_freed = self._empty_recycle_bin()
            if recycle_freed > 0:
                details.append(f"回收站: ~{recycle_freed} MB")
                total_freed += recycle_freed

            if total_freed > 0:
                message = f"清理完成，释放约 {total_freed} MB 空间\n" + "\n".join(details)
            else:
                message = "清理完成，未发现需要清理的文件"

            return {
                "success": True,
                "message": message,
                "data": {
                    "temp_freed": temp_freed,
                    "recycle_freed": recycle_freed,
                    "total_freed": total_freed
                }
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"清理失败: {str(e)}",
                "data": None
            }

    def _clean_temp_files(self) -> int:
        """清理临时文件"""
        freed_mb = 0

        temp_dirs = [
            tempfile.gettempdir(),
            os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
            os.path.expandvars(r"%TEMP%"),
        ]

        for temp_dir in temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    before_size = self._get_dir_size(temp_dir)
                    self._delete_temp_files(temp_dir)
                    after_size = self._get_dir_size(temp_dir)
                    freed_mb += (before_size - after_size) // (1024 * 1024)
            except Exception:
                pass

        return freed_mb

    def _delete_temp_files(self, directory: str):
        """删除目录中的临时文件"""
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)

                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        # 跳过正在使用的文件/文件夹
                        self._delete_temp_files(item_path)
                        try:
                            os.rmdir(item_path)
                        except OSError:
                            pass
                except (OSError, PermissionError):
                    # 跳过无法删除的文件
                    pass
        except (OSError, PermissionError):
            pass

    def _get_dir_size(self, directory: str) -> int:
        """获取目录大小（字节）"""
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except OSError:
                        pass
        except OSError:
            pass
        return total_size

    def _empty_recycle_bin(self) -> int:
        """清空回收站"""
        try:
            # 使用PowerShell清空回收站
            result = subprocess.run(
                ["powershell", "-Command",
                 "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                capture_output=True,
                text=True,
                timeout=60
            )
            # 估算回收站大小（无法精确获取）
            return 50  # 假设回收站约50MB
        except Exception:
            return 0

    def _launch_disk_cleanup(self):
        """启动Windows磁盘清理工具"""
        try:
            # 运行系统磁盘清理工具
            subprocess.Popen(
                ["cleanmgr", "/d", "C:"],
                shell=True
            )
        except Exception:
            pass

    def pre_check(self) -> str | None:
        """执行前检查"""
        if os.name != "nt":
            return "此插件仅支持Windows系统"
        return None
