"""
输入法重装插件
打开微信输入法官网下载页面，并卸载已存在的输入法
"""

import os
import subprocess
from typing import Dict, Any, List
from .base import PluginBase


class InputMethodPlugin(PluginBase):
    """输入法重装插件"""

    # 微信输入法下载地址（需要更新为实际地址）
    WECHAT_INPUT_URL = "https://z.weixin.qq.com/"

    @property
    def id(self) -> str:
        return "input_method"

    @property
    def name(self) -> str:
        return "重装微信输入法"

    @property
    def description(self) -> str:
        return "下载并重新安装微信输入法"

    @property
    def category(self) -> str:
        return "输入法"

    @property
    def icon(self) -> str:
        return "⌨️"

    @property
    def keywords(self) -> list:
        return ["输入法", "微信", "打字", "拼音", "重装"]

    @property
    def dangerous(self) -> bool:
        return True

    def _get_installed_input_methods(self) -> List[str]:
        """获取已安装的输入法列表"""
        try:
            # 使用PowerShell获取已安装的输入法
            result = subprocess.run([
                "powershell", "-Command",
                "Get-WinUserLanguageList | Select-Object -ExpandProperty LocalizedString"
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                methods = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                return methods
        except Exception:
            pass
        return []

    def _check_wechat_input_installed(self) -> bool:
        """检查微信输入法是否已安装"""
        try:
            # 检查注册表中的微信输入法
            import winreg
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"

            # 遍历卸载项查找微信输入法
            for key in winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path):
                try:
                    subkey_name = key[0]
                    subkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{key_path}\\{subkey_name}")
                    display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                    winreg.CloseKey(subkey)
                    if "微信" in display_name or "WeChat" in display_name or "输入法" in display_name:
                        return True
                except (OSError, FileNotFoundError):
                    continue

            # 检查用户安装路径
            user_key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            try:
                for key in winreg.OpenKey(winreg.HKEY_CURRENT_USER, user_key_path):
                    try:
                        subkey_name = key[0]
                        subkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"{user_key_path}\\{subkey_name}")
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                        winreg.CloseKey(subkey)
                        if "微信" in display_name or "WeChat" in display_name or "输入法" in display_name:
                            return True
                    except (OSError, FileNotFoundError):
                        continue
            except (OSError, FileNotFoundError):
                pass

        except Exception:
            pass
        return False

    def _uninstall_wechat_input_method(self) -> bool:
        """尝试卸载微信输入法"""
        try:
            # 尝试通过WMl卸载
            result = subprocess.run([
                "powershell", "-Command",
                "Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like '*微信*' -or $_.Name -like '*WeChat*'} | ForEach-Object { $_.Uninstall() }"
            ], capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                return True
        except Exception:
            pass
        return False

    def execute(self) -> Dict[str, Any]:
        """执行输入法重装"""
        try:
            if os.name != "nt":
                return {
                    "success": False,
                    "message": "此插件仅支持Windows系统",
                    "data": None
                }

            messages = []

            # 检查微信输入法是否已安装
            if self._check_wechat_input_installed():
                messages.append("检测到已安装微信输入法")
                # 尝试卸载
                if self._uninstall_wechat_input_method():
                    messages.append("已自动卸载微信输入法")
                else:
                    messages.append("卸载失败，请手动在控制面板中卸载后重新安装")

            # 打开微信输入法官网下载页面
            import webbrowser
            webbrowser.open(self.WECHAT_INPUT_URL)
            messages.append("已打开微信输入法官网下载页面，请在浏览器中下载并安装")

            return {
                "success": True,
                "message": "\n".join(messages),
                "data": {"url": self.WECHAT_INPUT_URL}
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"操作失败: {str(e)}",
                "data": None
            }

    def pre_check(self) -> str | None:
        """执行前检查"""
        if os.name != "nt":
            return "此插件仅支持Windows系统"
        return None
