"""
Chelp - 电脑小助手
主程序入口
"""

import sys
import os

# 处理打包后的路径
if getattr(sys, 'frozen', False):
    # 打包后的exe环境
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller解压临时目录
        bundle_dir = sys._MEIPASS
        src_dir = os.path.join(bundle_dir, 'src')
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
    # 当前exe所在目录（用于运行时资源）
    if getattr(sys, 'executable', None):
        app_dir = os.path.dirname(sys.executable)
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)
else:
    # 开发环境
    src_dir = os.path.dirname(os.path.abspath(__file__))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

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
