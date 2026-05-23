"""
输入法重装插件
下载并重新安装微信输入法
"""

import os
import subprocess
import tempfile
import requests
from typing import Dict, Any
from pathlib import Path
from .base import PluginBase


class InputMethodPlugin(PluginBase):
    """输入法重装插件"""

    # 微信输入法下载地址（需要更新为实际地址）
    WECHAT_INPUT_URL = "https://ime.weixin.qq.com/"

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

    def execute(self) -> Dict[str, Any]:
        """执行输入法重装"""
        try:
            if os.name != "nt":
                return {
                    "success": False,
                    "message": "此插件仅支持Windows系统",
                    "data": None
                }

            # 先打开下载页面作为备用方案
            import webbrowser
            webbrowser.open(self.WECHAT_INPUT_URL)

            # 尝试自动下载并安装
            result = self._install_via_powershell()

            if result["success"]:
                result["message"] = "微信输入法安装成功！请重启电脑后使用"
            else:
                result["message"] = "已打开微信输入法下载页面，请手动下载安装"

            return result

        except Exception as e:
            # 确保至少打开下载页面
            import webbrowser
            webbrowser.open(self.WECHAT_INPUT_URL)

            return {
                "success": False,
                "message": f"已打开下载页面，请手动安装。错误: {str(e)}",
                "data": {"url": self.WECHAT_INPUT_URL}
            }

    def _install_via_powershell(self) -> Dict[str, Any]:
        """通过PowerShell下载并安装"""
        try:
            # 尝试从常见的下载地址获取
            download_urls = [
                # 微信输入法官方下载地址（需要替换为实际地址）
                "https://dldir1.qq.com/qqfile/qq/PCQQ9200/WeChatIME.exe",
            ]

            installer_path = None

            for url in download_urls:
                installer_path = self._download_installer(url)
                if installer_path:
                    break

            if not installer_path:
                return {
                    "success": False,
                    "message": "无法下载安装包",
                    "data": None
                }

            # 静默安装
            install_result = self._silent_install(installer_path)

            # 清理安装包
            try:
                os.remove(installer_path)
            except OSError:
                pass

            return install_result

        except Exception as e:
            return {
                "success": False,
                "message": f"安装过程出错: {str(e)}",
                "data": None
            }

    def _download_installer(self, url: str) -> str | None:
        """下载安装程序"""
        try:
            temp_dir = tempfile.gettempdir()
            filename = "WeChatIME_installer.exe"
            dest_path = os.path.join(temp_dir, filename)

            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return dest_path

        except requests.RequestException:
            return None

    def _silent_install(self, installer_path: str) -> Dict[str, Any]:
        """静默安装"""
        try:
            # 常见的静默安装参数
            install_args = [
                installer_path,
                "/S",  # 静默安装
                "/D=C:\\Program Files\\WeChatIME"  # 安装目录
            ]

            result = subprocess.run(
                install_args,
                capture_output=True,
                timeout=300
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "微信输入法安装成功，请重启电脑后使用",
                    "data": {"installed": True}
                }
            else:
                return {
                    "success": False,
                    "message": f"安装失败，错误代码: {result.returncode}",
                    "data": None
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "安装超时",
                "data": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"安装出错: {str(e)}",
                "data": None
            }

    def set_default_input_method(self) -> Dict[str, Any]:
        """设置微信输入法为默认"""
        try:
            # 使用PowerShell设置输入法
            ps_command = """
            $List = Get-WinUserLanguageList
            $List.Add('zh-CN')
            Set-WinUserLanguageList $List -Force
            Set-WinSystemLocale -SystemLocale 'zh-CN'
            """

            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "已设置中文输入法为默认",
                    "data": None
                }
            else:
                return {
                    "success": False,
                    "message": f"设置失败: {result.stderr}",
                    "data": None
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"设置失败: {str(e)}",
                "data": None
            }

    def pre_check(self) -> str | None:
        """执行前检查"""
        if os.name != "nt":
            return "此插件仅支持Windows系统"
        return None
