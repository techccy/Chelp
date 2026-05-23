"""
网络修复插件
自动诊断并修复常见网络问题
"""

import os
import subprocess
from typing import Dict, Any
from .base import PluginBase


class NetworkFixerPlugin(PluginBase):
    """网络修复插件"""

    @property
    def id(self) -> str:
        return "network_fixer"

    @property
    def name(self) -> str:
        return "网络诊断修复"

    @property
    def description(self) -> str:
        return "自动诊断并修复常见网络连接问题"

    @property
    def category(self) -> str:
        return "网络"

    @property
    def icon(self) -> str:
        return "🌐"

    @property
    def keywords(self) -> list:
        return ["网络", "连接", "wifi", "网线", "上网", "断网", "修复"]

    def execute(self) -> Dict[str, Any]:
        """执行网络修复"""
        try:
            if os.name != "nt":
                return {
                    "success": False,
                    "message": "此插件仅支持Windows系统",
                    "data": None
                }

            results = []
            success_count = 0

            # 1. 释放并更新DNS缓存
            if self._flush_dns():
                results.append("DNS缓存已清理")
                success_count += 1

            # 2. 重置网络适配器
            if self._reset_network():
                results.append("网络适配器已重置")
                success_count += 1

            # 3. 重启Windows防火墙服务
            if self._reset_firewall():
                results.append("防火墙服务已重启")
                success_count += 1

            # 4. 重置Winsock目录
            if self._reset_winsock():
                results.append("Winsock已重置")
                success_count += 1

            # 5. 刷新ARP缓存
            if self._flush_arp():
                results.append("ARP缓存已清理")
                success_count += 1

            if success_count > 0:
                return {
                    "success": True,
                    "message": "、".join(results) + "，请重启电脑后生效",
                    "data": {
                        "actions": results,
                        "count": success_count
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "未能完成任何修复操作",
                    "data": None
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"修复失败: {str(e)}",
                "data": None
            }

    def _flush_dns(self) -> bool:
        """释放并更新DNS缓存"""
        try:
            result = subprocess.run(
                ["ipconfig", "/flushdns"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return "成功" in result.stdout
        except Exception:
            return False

    def _reset_network(self) -> bool:
        """重置网络适配器"""
        try:
            # 释放IP
            subprocess.run(
                ["ipconfig", "/release"],
                capture_output=True,
                timeout=30
            )
            # 更新IP
            result = subprocess.run(
                ["ipconfig", "/renew"],
                capture_output=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False

    def _reset_firewall(self) -> bool:
        """重启防火墙服务"""
        try:
            # 重启防火墙服务
            subprocess.run(
                ["netsh", "advfirewall", "reset"],
                capture_output=True,
                timeout=30
            )
            return True
        except Exception:
            return False

    def _reset_winsock(self) -> bool:
        """重置Winsock目录"""
        try:
            result = subprocess.run(
                ["netsh", "winsock", "reset"],
                capture_output=True,
                timeout=30
            )
            return "成功" in result.stdout.decode('gbk', errors='ignore')
        except Exception:
            return False

    def _flush_arp(self) -> bool:
        """清理ARP缓存"""
        try:
            result = subprocess.run(
                ["netsh", "interface", "ip", "delete", "arpcache"],
                capture_output=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False

    def diagnose(self) -> Dict[str, Any]:
        """网络诊断"""
        try:
            diagnostics = []

            # 检查网络连接
            result = subprocess.run(
                ["ping", "-n", "1", "223.5.5.5"],  # 阿里DNS
                capture_output=True,
                text=True,
                timeout=10
            )
            if "往返" in result.stdout or "bytes from" in result.stdout:
                diagnostics.append({"item": "互联网连接", "status": "正常"})
            else:
                diagnostics.append({"item": "互联网连接", "status": "异常"})

            # 检查DNS解析
            result = subprocess.run(
                ["nslookup", "www.baidu.com"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if "Addresses" in result.stdout or "地址" in result.stdout:
                diagnostics.append({"item": "DNS解析", "status": "正常"})
            else:
                diagnostics.append({"item": "DNS解析", "status": "异常"})

            return {
                "success": True,
                "message": "诊断完成",
                "data": {"diagnostics": diagnostics}
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"诊断失败: {str(e)}",
                "data": None
            }

    def pre_check(self) -> str | None:
        """执行前检查"""
        if os.name != "nt":
            return "此插件仅支持Windows系统"
        return None
