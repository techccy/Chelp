"""
配置管理模块
管理应用程序配置和用户设置
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""

    # 默认配置
    DEFAULT_CONFIG = {
        "app": {
            "name": "Chelp",
            "version": "1.1.0",
            "theme": "light",  # light/dark
            "language": "zh-CN",
            "auto_update": True,
            "check_update_interval": 86400,  # 秒
            "window": {
                "width": 800,
                "height": 600,
                "remember_size": True
            }
        },
        "ai": {
            "provider": "deepseek",  # deepseek/ollama/openai
            "model": "deepseek-chat",
            "api_key": "",
            "api_base": "https://api.deepseek.com",
            "local_model": "gemma2:2b",
            "enable_local": True,
            "hybrid_mode": True  # 混合模式：先关键词后AI
        },
        "plugins": {
            "auto_load_external": True,
            "external_dir": "plugins",
            "market_url": ""  # GitHub插件市场URL
        },
        "saved_state": {
                "display": {
                    "resolution": "1920x1080",
                    "scale": 100,
                    "auto_read": False
                },
                "input_method": {
                    "default": None
                }
            }
    }

    def __init__(self, config_dir: str = None, config_file: str = "settings.yaml"):
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # 默认配置目录
            self.config_dir = Path.home() / ".chelp"

        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / config_file
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = yaml.safe_load(f)
                    if loaded:
                        return self._merge_config(self.DEFAULT_CONFIG, loaded)
            except Exception as e:
                print(f"加载配置失败: {e}")

        return self.DEFAULT_CONFIG.copy()

    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """合并配置"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def save(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项，支持点号分隔的路径"""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """设置配置项，支持点号分隔的路径"""
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()

    def reset(self):
        """重置为默认配置"""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save()

    @property
    def app_name(self) -> str:
        return self.get("app.name", "Chelp")

    @property
    def version(self) -> str:
        return self.get("app.version", "1.0.0")

    @property
    def theme(self) -> str:
        return self.get("app.theme", "light")

    @theme.setter
    def theme(self, value: str):
        self.set("app.theme", value)

    @property
    def auto_update(self) -> bool:
        return self.get("app.auto_update", True)

    @property
    def ai_provider(self) -> str:
        return self.get("ai.provider", "deepseek")

    @property
    def ai_api_key(self) -> str:
        return self.get("ai.api_key", "")

    @ai_api_key.setter
    def ai_api_key(self, value: str):
        self.set("ai.api_key", value)

    @property
    def ai_model(self) -> str:
        return self.get("ai.model", "deepseek-chat")

    @property
    def hybrid_mode(self) -> bool:
        return self.get("ai.hybrid_mode", True)

    def save_display_state(self, resolution: str = None, scale: int = None):
        """保存显示状态"""
        if resolution:
            self.set("saved_state.display.resolution", resolution)
        if scale:
            self.set("saved_state.display.scale", scale)
        self.save()

    def get_display_state(self) -> Dict[str, Any]:
        """获取保存的显示状态"""
        return {
            "resolution": self.get("saved_state.display.resolution"),
            "scale": self.get("saved_state.display.scale")
        }

    def save_input_method(self, method: str):
        """保存默认输入法"""
        self.set("saved_state.input_method.default", method)
        self.save()

    def get_input_method(self) -> Optional[str]:
        """获取保存的输入法"""
        return self.get("saved_state.input_method.default")

    def export_to_json(self, file_path: str = None) -> str:
        """导出配置到JSON文件

        Args:
            file_path: 导出文件路径，如果为None则使用默认路径

        Returns:
            实际导出的文件路径
        """
        if file_path is None:
            file_path = self.config_dir / "chelp_config.json"
        else:
            file_path = Path(file_path)

        # 过滤敏感信息的占位符
        export_config = self._config.copy()

        # 如果API密钥为空，添加占位符说明
        if not export_config.get("ai", {}).get("api_key"):
            export_config.setdefault("ai", {})["api_key"] = ""

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_config, f, ensure_ascii=False, indent=2)

        return str(file_path)

    def import_from_json(self, file_path: str, merge: bool = True) -> bool:
        """从JSON文件导入配置

        Args:
            file_path: JSON文件路径
            merge: 是否合并现有配置，False则完全替换

        Returns:
            是否导入成功
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            if merge:
                # 合并配置
                self._config = self._merge_config(self._config, imported_config)
            else:
                # 完全替换
                self._config = imported_config

            # 保存到YAML配置文件
            self.save()
            return True

        except Exception as e:
            print(f"导入配置失败: {e}")
            return False

    def get_safe_config(self) -> Dict[str, Any]:
        """获取安全的配置副本（用于展示或部分导出）

        隐藏敏感信息如API密钥
        """
        config = self._config.copy()
        if "ai" in config and "api_key" in config["ai"]:
            api_key = config["ai"]["api_key"]
            if api_key:
                # 只显示前4位和后4位
                if len(api_key) > 8:
                    config["ai"]["api_key"] = api_key[:4] + "****" + api_key[-4:]
                else:
                    config["ai"]["api_key"] = "****"
        return config


# 全局配置实例
_config_instance: Optional[ConfigManager] = None


def get_config(config_dir: str = None) -> ConfigManager:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager(config_dir)
    return _config_instance
