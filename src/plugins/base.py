"""
插件基类模块
所有插件都应继承 PluginBase 类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class PluginBase(ABC):
    """所有插件的基类"""

    def __init__(self):
        self._config = {}

    @property
    @abstractmethod
    def id(self) -> str:
        """插件唯一标识符 (英文ID)"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """插件显示名称 (中文)"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """功能描述"""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """分类：系统清理/显示设置/输入法/网络等"""
        pass

    @property
    def icon(self) -> str:
        """图标emoji"""
        return "🔧"

    @property
    def keywords(self) -> List[str]:
        """搜索关键词"""
        return []

    @property
    def dangerous(self) -> bool:
        """是否需要确认（危险操作）"""
        return False

    @property
    def enabled(self) -> bool:
        """是否启用"""
        return True

    def set_config(self, config: Dict[str, Any]):
        """设置插件配置"""
        self._config = config

    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self._config.get(key, default)

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """执行插件功能

        返回: {
            "success": bool,
            "message": str,
            "data": any
        }
        """
        pass

    def pre_check(self) -> Optional[str]:
        """执行前检查，返回错误信息或None"""
        return None

    def post_execute(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """执行后处理，可覆盖以添加额外处理"""
        return result

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
