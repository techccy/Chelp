"""
启动项管理插件
管理系统启动项，提升开机速度
"""

import os
import subprocess
from typing import Dict, Any, List
from .base import PluginBase


class StartupManagerPlugin(PluginBase):
    """启动项管理插件"""

    @property
    def id(self) -> str:
        return "startup_manager"

    @property
    def name(self) -> str:
        return "启动项管理"

    @property
    def description(self) -> str:
        return "管理系统启动项，关闭不必要的自启动程序"

    @property
    def category(self) -> str:
        return "系统清理"

    @property
    def icon(self) -> str:
        return "🚀"

    @property
    def keywords(self) -> list:
        return ["启动", "开机", "自启动", "加速", "启动项", "开机速度"]

    def execute(self) -> Dict[str, Any]:
        """打开启动项管理界面"""
        try:
            if os.name != "nt":
                return {
                    "success": False,
                    "message": "此插件仅支持Windows系统",
                    "data": None
                }

            # 打开任务管理器的启动选项卡
            subprocess.run(
                ["taskmgr", "/0", "/startup"],
                check=False
            )

            return {
                "success": True,
                "message": "已打开启动项管理界面，请禁用不需要的启动项",
                "data": None
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"打开失败: {str(e)}",
                "data": None
            }

    def get_startup_items(self) -> Dict[str, Any]:
        """获取启动项列表"""
        try:
            if os.name != "nt":
                return {"success": False, "message": "仅支持Windows"}

            items = []

            # 通过注册表获取启动项
            import winreg

            startup_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ]

            for root, path in startup_paths:
                try:
                    key = winreg.OpenKey(root, path)
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            items.append({
                                "name": name,
                                "path": value,
                                "location": "注册表"
                            })
                            i += 1
                        except OSError:
                            break
                    winreg.CloseKey(key)
                except WindowsError:
                    pass

            # 检查启动文件夹
            startup_folder = os.path.join(
                os.environ.get("APPDATA", ""),
                r"Microsoft\Windows\Start Menu\Programs\Startup"
            )

            if os.path.exists(startup_folder):
                for item in os.listdir(startup_folder):
                    if item.endswith(".lnk"):
                        items.append({
                            "name": item,
                            "path": os.path.join(startup_folder, item),
                            "location": "启动文件夹"
                        })

            return {
                "success": True,
                "message": f"找到 {len(items)} 个启动项",
                "data": {"items": items}
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"获取失败: {str(e)}",
                "data": None
            }

    def disable_startup_item(self, item_name: str) -> Dict[str, Any]:
        """禁用启动项"""
        try:
            import winreg

            # 查找并删除注册表启动项
            paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ]

            for root, path in paths:
                try:
                    key = winreg.OpenKey(root, path, 0, winreg.KEY_SET_VALUE)
                    try:
                        winreg.DeleteValue(key, item_name)
                        winreg.CloseKey(key)
                        return {
                            "success": True,
                            "message": f"已禁用启动项: {item_name}",
                            "data": None
                        }
                    except OSError:
                        winreg.CloseKey(key)
                except OSError:
                    pass

            return {
                "success": False,
                "message": f"未找到启动项: {item_name}",
                "data": None
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"禁用失败: {str(e)}",
                "data": None
            }

    def open_startup_folder(self) -> Dict[str, Any]:
        """打开启动文件夹"""
        try:
            startup_folder = os.path.join(
                os.environ.get("APPDATA", ""),
                r"Microsoft\Windows\Start Menu\Programs\Startup"
            )

            if os.path.exists(startup_folder):
                subprocess.run(
                    ["explorer", startup_folder],
                    check=False
                )
                return {
                    "success": True,
                    "message": "已打开启动文件夹",
                    "data": {"path": startup_folder}
                }
            else:
                return {
                    "success": False,
                    "message": "启动文件夹不存在",
                    "data": None
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"打开失败: {str(e)}",
                "data": None
            }

    def pre_check(self) -> str | None:
        """执行前检查"""
        if os.name != "nt":
            return "此插件仅支持Windows系统"
        return None
