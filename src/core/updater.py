"""
GitHub更新检测模块
检测并自动更新程序
"""

import os
import requests
import subprocess
import tempfile
from typing import Optional, Dict, List, Any
from pathlib import Path


class GitHubUpdater:
    """检测并自动更新"""

    GITHUB_API_BASE = "https://api.github.com"

    def __init__(self, repo: str = "username/chelp", current_version: str = "1.0.0"):
        self.repo = repo  # 格式: "owner/repo"
        self.current_version = current_version
        self.last_check = None
        self.update_available = False
        self.latest_release = None

    def _get_headers(self) -> Dict[str, str]:
        """获取API请求头"""
        return {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"Chelp/{self.current_version}"
        }

    def check_update(self) -> Optional[Dict[str, Any]]:
        """检查GitHub新版本"""
        try:
            url = f"{self.GITHUB_API_BASE}/repos/{self.repo}/releases/latest"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()

            release = response.json()
            self.latest_release = release

            # 检查版本
            latest_version = release.get("tag_name", "").lstrip("v")
            self.update_available = latest_version != self.current_version

            return {
                "has_update": self.update_available,
                "current_version": self.current_version,
                "latest_version": latest_version,
                "release_url": release.get("html_url"),
                "changelog": release.get("body"),
                "published_at": release.get("published_at")
            }

        except requests.RequestException as e:
            print(f"检查更新失败: {e}")
            return None

    def get_download_url(self, asset_pattern: str = None) -> Optional[str]:
        """获取下载链接"""
        if not self.latest_release:
            return None

        assets = self.latest_release.get("assets", [])

        if asset_pattern:
            # 查找匹配的资源
            for asset in assets:
                if asset_pattern.lower() in asset["name"].lower():
                    return asset["browser_download_url"]
        else:
            # 返回第一个资源
            if assets:
                return assets[0]["browser_download_url"]

        return None

    def download_update(self, url: str, dest_dir: str = None) -> Optional[str]:
        """下载更新文件"""
        if dest_dir is None:
            dest_dir = tempfile.gettempdir()

        filename = url.split("/")[-1]
        dest_path = Path(dest_dir) / filename

        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return str(dest_path)

        except requests.RequestException as e:
            print(f"下载失败: {e}")
            return None

    def install_update(self, installer_path: str) -> bool:
        """安装更新（Windows）"""
        if os.name != "nt":
            return False

        try:
            # 启动安装程序
            subprocess.Popen([
                installer_path,
                "/SILENT",  # 静默安装
                "/NOICONS"  # 不创建图标
            ])
            return True
        except Exception as e:
            print(f"安装失败: {e}")
            return False

    def fetch_new_plugins(self) -> List[Dict]:
        """从GitHub获取新插件配置"""
        try:
            url = f"{self.GITHUB_API_BASE}/repos/{self.repo}/contents/plugins-market.yaml"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()

            data = response.json()

            # 解析base64内容
            import base64
            import yaml

            if data.get("encoding") == "base64":
                content = base64.b64decode(data["content"]).decode("utf-8")
                plugins_config = yaml.safe_load(content)
                return plugins_config.get("plugins", [])

        except requests.RequestException as e:
            print(f"获取插件列表失败: {e}")

        return []

    def download_plugin(self, plugin_url: str, dest_dir: str) -> bool:
        """下载外部插件"""
        try:
            # 如果是GitHub仓库URL
            if "github.com" in plugin_url:
                # 转换为raw内容URL
                if "/tree/" in plugin_url:
                    # 分支URL
                    plugin_url = plugin_url.replace(
                        "github.com", "raw.githubusercontent.com"
                    ).replace("/tree/", "/")

                response = requests.get(plugin_url, timeout=30)
                response.raise_for_status()

                filename = plugin_url.split("/")[-1]
                dest_path = Path(dest_dir) / filename

                with open(dest_path, 'wb') as f:
                    f.write(response.content)

                return True

        except requests.RequestException as e:
            print(f"下载插件失败: {e}")

        return False

    def get_releases_notes(self, count: int = 5) -> List[Dict]:
        """获取最近几个版本的更新日志"""
        try:
            url = f"{self.GITHUB_API_BASE}/repos/{self.repo}/releases"
            response = requests.get(url, headers=self._get_headers()}, timeout=10)
            response.raise_for_status()

            releases = response.json()[:count]

            return [
                {
                    "version": r.get("tag_name", "").lstrip("v"),
                    "name": r.get("name"),
                    "date": r.get("published_at"),
                    "notes": r.get("body")
                }
                for r in releases
            ]

        except requests.RequestException:
            return []
