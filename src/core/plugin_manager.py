"""
插件管理器
管理所有插件的加载、搜索和执行
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import List, Dict, Optional, Type, Any
import yaml

from plugins.base import PluginBase


class PluginManager:
    """管理所有插件的加载、搜索和执行"""

    # 分类映射
    CATEGORIES = {
        "system": "系统清理",
        "display": "显示设置",
        "input": "输入法",
        "network": "网络",
        "registry": "注册表",
        "software": "软件管理",
    }

    def __init__(self, config_path: str = None):
        self.plugins: List[PluginBase] = []
        self._plugin_classes: Dict[str, Type[PluginBase]] = {}
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict:
        """加载插件配置"""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {"plugins": []}

    def get_plugin_config(self, plugin_id: str) -> Dict:
        """获取特定插件的配置"""
        for plugin_config in self._config.get("plugins", []):
            if plugin_config.get("id") == plugin_id:
                return plugin_config.get("settings", {})
        return {}

    def register_plugin_class(self, plugin_class: Type[PluginBase]):
        """注册插件类"""
        plugin = plugin_class()
        plugin.set_config(self.get_plugin_config(plugin.id))
        self._plugin_classes[plugin.id] = plugin_class
        if plugin.enabled:
            self.plugins.append(plugin)

    def load_builtin_plugins(self):
        """加载内置插件"""
        from plugins.disk_cleaner import DiskCleanerPlugin
        from plugins.display_fixer import DisplayFixerPlugin
        from plugins.input_method import InputMethodPlugin
        from plugins.network_fixer import NetworkFixerPlugin
        from plugins.startup_manager import StartupManagerPlugin

        self.register_plugin_class(DiskCleanerPlugin)
        self.register_plugin_class(DisplayFixerPlugin)
        self.register_plugin_class(InputMethodPlugin)
        self.register_plugin_class(NetworkFixerPlugin)
        self.register_plugin_class(StartupManagerPlugin)

    def load_external_plugins(self, plugins_dir: str = None):
        """从 plugins/ 目录加载外部插件"""
        if plugins_dir is None:
            plugins_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "plugins"
            )

        plugins_path = Path(plugins_dir)
        if not plugins_path.exists():
            return

        for plugin_file in plugins_path.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue

            try:
                spec = importlib.util.spec_from_file_location(
                    plugin_file.stem, plugin_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[plugin_file.stem] = module
                    spec.loader.exec_module(module)

                    # 查找插件类
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if (isinstance(item, type) and
                                issubclass(item, PluginBase) and
                                item != PluginBase):
                            self.register_plugin_class(item)
            except Exception as e:
                print(f"加载插件 {plugin_file} 失败: {e}")

    def get_all_plugins(self) -> List[PluginBase]:
        """获取所有插件"""
        return self.plugins

    def get_plugin_by_id(self, plugin_id: str) -> Optional[PluginBase]:
        """根据ID获取插件"""
        for plugin in self.plugins:
            if plugin.id == plugin_id:
                return plugin
        return None

    def search(self, query: str) -> List[PluginBase]:
        """按关键词搜索插件"""
        query = query.lower()
        results = []

        for plugin in self.plugins:
            # 搜索名称
            if query in plugin.name.lower():
                results.append(plugin)
                continue

            # 搜索描述
            if query in plugin.description.lower():
                results.append(plugin)
                continue

            # 搜索关键词
            for keyword in plugin.keywords:
                if query in keyword.lower():
                    results.append(plugin)
                    break

        return results

    def get_by_category(self, category: str) -> List[PluginBase]:
        """按分类获取插件"""
        return [p for p in self.plugins if p.category == category]

    def get_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set(p.category for p in self.plugins)
        return sorted(categories)

    def execute_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """执行指定插件"""
        plugin = self.get_plugin_by_id(plugin_id)
        if not plugin:
            return {
                "success": False,
                "message": f"未找到插件: {plugin_id}",
                "data": None
            }

        # 执行前检查
        check_result = plugin.pre_check()
        if check_result:
            return {
                "success": False,
                "message": check_result,
                "data": None
            }

        # 执行插件
        try:
            result = plugin.execute()
            return plugin.post_execute(result)
        except Exception as e:
            return {
                "success": False,
                "message": f"执行失败: {str(e)}",
                "data": None
            }

    def reload(self):
        """重新加载所有插件"""
        self.plugins = []
        self._plugin_classes = {}
        self.load_builtin_plugins()
        self.load_external_plugins()
