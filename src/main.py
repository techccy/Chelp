"""
Chelp - 电脑小助手
主程序入口
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from core.config import get_config
from core.plugin_manager import PluginManager
from core.ai_matcher import AIMatcher
from ui.main_window import MainWindow


def main():
    """主函数"""
    # 初始化配置
    config = get_config()

    # 设置主题
    ctk.set_appearance_mode(config.theme)

    # 创建插件管理器
    plugin_manager = PluginManager()
    plugin_manager.load_builtin_plugins()

    # 创建AI匹配器（如果配置了API密钥）
    ai_matcher = None
    if config.ai_api_key:
        ai_config = {
            "ai_api_key": config.ai_api_key,
            "ai_model": config.ai_model,
            "api_base": config.get("ai.api_base", "https://api.deepseek.com"),
            "hybrid_mode": config.hybrid_mode
        }
        ai_matcher = AIMatcher(plugin_manager.get_all_plugins(), ai_config)

    # 创建主窗口
    app = MainWindow(plugin_manager, ai_matcher, config)

    # 运行应用
    app.mainloop()


if __name__ == "__main__":
    main()
