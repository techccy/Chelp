"""
显示恢复插件
恢复分辨率和显示比例到初始状态
"""

import os
import ctypes
import subprocess
from typing import Dict, Any, Optional
from .base import PluginBase


class DisplayFixerPlugin(PluginBase):
    """显示恢复插件"""

    # 常见分辨率
    COMMON_RESOLUTIONS = [
        (1920, 1080),
        (1366, 768),
        (2560, 1440),
        (3840, 2160),
        (1680, 1050),
        (1600, 900),
        (1440, 900),
        (1280, 1024),
        (1280, 720)
    ]

    @property
    def id(self) -> str:
        return "display_fixer"

    @property
    def name(self) -> str:
        return "显示恢复"

    @property
    def description(self) -> str:
        return "恢复分辨率和显示缩放比例到初始状态"

    @property
    def category(self) -> str:
        return "显示设置"

    @property
    def icon(self) -> str:
        return "🖥️"

    @property
    def keywords(self) -> list:
        return ["分辨率", "显示", "缩放", "屏幕", "DPI", "显示比例"]

    def __init__(self):
        super().__init__()
        self.saved_settings = self._load_saved_settings()

    def _load_saved_settings(self) -> Dict[str, Any]:
        """加载保存的显示设置"""
        return {
            "resolution": self.get_config("default_resolution"),
            "scale": self.get_config("default_scale", 100)
        }

    def execute(self) -> Dict[str, Any]:
        """执行显示恢复"""
        try:
            if os.name != "nt":
                return {
                    "success": False,
                    "message": "此插件仅支持Windows系统",
                    "data": None
                }

            result = {
                "resolution_changed": False,
                "scale_changed": False,
                "details": []
            }

            # 恢复分辨率
            if self.saved_settings["resolution"]:
                width, height = self._parse_resolution(self.saved_settings["resolution"])
                if width and height:
                    if self._set_resolution(width, height):
                        result["resolution_changed"] = True
                        result["details"].append(f"分辨率设为 {width}x{height}")

            # 恢复缩放比例
            if self.saved_settings["scale"]:
                scale = int(self.saved_settings["scale"])
                if self._set_dpi_awareness(scale):
                    result["scale_changed"] = True
                    result["details"].append(f"缩放比例设为 {scale}%")

            if result["details"]:
                return {
                    "success": True,
                    "message": "、".join(result["details"]),
                    "data": result
                }
            else:
                return {
                    "success": False,
                    "message": "未配置保存的显示设置，请先在设置中保存当前显示状态",
                    "data": result
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"恢复失败: {str(e)}",
                "data": None
            }

    def _parse_resolution(self, resolution: str) -> Optional[tuple]:
        """解析分辨率字符串"""
        try:
            if "x" in resolution:
                width, height = resolution.split("x")
                return int(width), int(height)
            elif "*" in resolution:
                width, height = resolution.split("*")
                return int(width), int(height)
        except (ValueError, AttributeError):
            pass
        return None

    def _set_resolution(self, width: int, height: int) -> bool:
        """设置显示器分辨率"""
        try:
            # 使用Windows API设置分辨率
            import ctypes.wintypes

            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32

            # 获取当前显示设置
            class DEVMODE(ctypes.Structure):
                _fields_ = [
                    ("dmSize", ctypes.c_ushort),
                    ("dmDriverExtra", ctypes.c_ushort),
                    ("dmFields", ctypes.c_ulong),
                    ("dmPelsWidth", ctypes.c_ulong),
                    ("dmPelsHeight", ctypes.c_ulong),
                    ("dmDisplayFlags", ctypes.c_ulong),
                    ("dmDisplayFrequency", ctypes.c_ulong),
                ]

            dm = DEVMODE()
            dm.dmSize = ctypes.sizeof(DEVMODE)
            dm.dmFields = 0x100000 | 0x20000  # DM_PELSWIDTH | DM_PELSHEIGHT
            dm.dmPelsWidth = width
            dm.dmPelsHeight = height

            result = user32.ChangeDisplaySettingsW(
                ctypes.byref(dm), 0
            )

            return result == 0  # DISP_CHANGE_SUCCESSFUL

        except Exception as e:
            print(f"设置分辨率失败: {e}")
            return False

    def _set_dpi_awareness(self, scale: int) -> bool:
        """设置DPI缩放比例"""
        try:
            # Windows 10/11 通过注册表设置DPI
            import winreg

            # 计算DPI值
            dpi_value = int(scale * 96 / 100)

            # 打开注册表
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Control Panel\Desktop",
                0,
                winreg.KEY_SET_VALUE
            )

            # 设置DPI值
            winreg.SetValueEx(key, "LogPixels", 0, winreg.REG_DWORD, dpi_value)
            winreg.CloseKey(key)

            # 通知系统设置已更改
            subprocess.run(
                ["powershell", "-Command",
                 "Set-ItemProperty -Path 'HKCU:Control Panel\Desktop' -Name Win8DpiScaling -Value 1"],
                capture_output=True
            )

            return True

        except Exception as e:
            print(f"设置DPI失败: {e}")
            return False

    def save_current_display(self) -> Dict[str, Any]:
        """保存当前显示设置"""
        try:
            resolution = self._get_current_resolution()
            if resolution:
                self.saved_settings["resolution"] = resolution
                return {
                    "success": True,
                    "message": f"已保存当前显示设置: {resolution}",
                    "data": {"resolution": resolution}
                }
            return {
                "success": False,
                "message": "无法获取当前显示设置",
                "data": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"保存失败: {str(e)}",
                "data": None
            }

    def _get_current_resolution(self) -> Optional[str]:
        """获取当前分辨率"""
        try:
            user32 = ctypes.windll.user32
            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)
            return f"{width}x{height}"
        except Exception:
            return None

    def pre_check(self) -> str | None:
        """执行前检查"""
        if os.name != "nt":
            return "此插件仅支持Windows系统"
        return None
