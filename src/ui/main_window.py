"""
主窗口模块
CustomTkinter主界面
"""

import customtkinter as ctk
from typing import Optional, List, Dict, Any
import threading
import logging


class MainWindow(ctk.CTk):
    """主窗口"""

    def __init__(self, plugin_manager, ai_matcher=None, config=None):
        super().__init__()

        self.plugin_manager = plugin_manager
        self.ai_matcher = ai_matcher
        self.config = config
        self.current_category = "全部"

        self._setup_window()
        self._create_widgets()
        self._load_plugins()

    def _setup_window(self):
        """设置窗口"""
        self.title("Chelp - 电脑小助手")
        self.geometry("900x650")

        # 设置主题
        if self.config:
            theme = self.config.theme
            ctk.set_appearance_mode(theme)

        self.minsize(800, 600)

    def _create_widgets(self):
        """创建界面组件"""
        # 顶部搜索栏
        self._create_search_bar()

        # 分类筛选
        self._create_category_filter()

        # 插件列表
        self._create_plugin_list()

        # 底部状态栏
        self._create_status_bar()

    def _create_search_bar(self):
        """创建搜索栏"""
        search_frame = ctk.CTkFrame(self, height=60)
        search_frame.pack(fill="x", padx=20, pady=(20, 10))
        search_frame.pack_propagate(False)

        # 搜索框
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search)

        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 搜索功能...",
            textvariable=self.search_var,
            height=40,
            font=("Microsoft YaHei", 14)
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # AI助手按钮
        if self.ai_matcher:
            ai_button = ctk.CTkButton(
                search_frame,
                text="🤖 AI助手",
                width=120,
                height=40,
                command=self._open_ai_chat,
                font=("Microsoft YaHei", 13)
            )
            ai_button.pack(side="right")

    def _create_category_filter(self):
        """创建分类筛选"""
        filter_frame = ctk.CTkFrame(self, height=50)
        filter_frame.pack(fill="x", padx=20, pady=(0, 10))
        filter_frame.pack_propagate(False)

        categories = ["全部"] + self.plugin_manager.get_categories()

        self.category_buttons = []
        for i, category in enumerate(categories):
            btn = ctk.CTkButton(
                filter_frame,
                text=category,
                width=100,
                height=35,
                command=lambda c=category: self._filter_by_category(c),
                font=("Microsoft YaHei", 12)
            )
            btn.pack(side="left", padx=5)
            self.category_buttons.append(btn)

        # 默认选中"全部"
        self._select_category_button("全部")

    def _create_plugin_list(self):
        """创建插件列表"""
        # 主容器
        list_container = ctk.CTkFrame(self)
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # 滚动区域
        scroll_frame = ctk.CTkScrollableFrame(list_container)
        scroll_frame.pack(fill="both", expand=True)

        self.plugin_container = scroll_frame
        self.plugin_widgets = []

    def _create_status_bar(self):
        """创建状态栏"""
        status_frame = ctk.CTkFrame(self, height=40)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        status_frame.pack_propagate(False)

        # 版本信息
        if self.config:
            version_label = ctk.CTkLabel(
                status_frame,
                text=f"v{self.config.version}",
                font=("Microsoft YaHei", 11)
            )
            version_label.pack(side="right", padx=10)

        # 日志按钮
        log_btn = ctk.CTkButton(
            status_frame,
            text="📋 日志",
            width=80,
            height=30,
            command=self._open_log_window,
            font=("Microsoft YaHei", 11)
        )
        log_btn.pack(side="right", padx=5)

        # 设置按钮
        settings_btn = ctk.CTkButton(
            status_frame,
            text="⚙️ 设置",
            width=80,
            height=30,
            command=self._open_settings,
            font=("Microsoft YaHei", 11)
        )
        settings_btn.pack(side="right", padx=5)

    def _load_plugins(self):
        """加载并显示插件"""
        self._clear_plugin_list()

        plugins = self.plugin_manager.get_all_plugins()

        for plugin in plugins:
            widget = self._create_plugin_widget(plugin)
            self.plugin_widgets.append(widget)

    def _create_plugin_widget(self, plugin) -> ctk.CTkFrame:
        """创建单个插件卡片"""
        card = ctk.CTkFrame(self.plugin_container, height=120)
        card.pack(fill="x", pady=5)
        card.pack_propagate(False)

        # 图标
        icon_label = ctk.CTkLabel(
            card,
            text=plugin.icon,
            font=("Microsoft YaHei", 32)
        )
        icon_label.pack(side="left", padx=(15, 10))

        # 信息区
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # 名称
        name_label = ctk.CTkLabel(
            info_frame,
            text=plugin.name,
            font=("Microsoft YaHei", 16, "bold"),
            anchor="w"
        )
        name_label.pack(fill="x")

        # 描述
        desc_label = ctk.CTkLabel(
            info_frame,
            text=plugin.description,
            font=("Microsoft YaHei", 12),
            anchor="w",
            text_color="gray"
        )
        desc_label.pack(fill="x", pady=(5, 0))

        # 执行按钮
        btn_color = "darkred" if plugin.dangerous else "#1f6aa5"
        btn_text = "⚠️ 执行" if plugin.dangerous else "执行"

        execute_btn = ctk.CTkButton(
            card,
            text=btn_text,
            width=100,
            height=40,
            fg_color=btn_color,
            command=lambda p=plugin: self._execute_plugin(p),
            font=("Microsoft YaHei", 13)
        )
        execute_btn.pack(side="right", padx=15)

        # 存储插件引用
        card.plugin = plugin
        card.execute_btn = execute_btn

        return card

    def _clear_plugin_list(self):
        """清空插件列表"""
        for widget in self.plugin_container.winfo_children():
            widget.destroy()
        self.plugin_widgets = []

    def _on_search(self, *args):
        """搜索事件处理"""
        query = self.search_var.get().strip()

        if not query:
            # 显示所有插件
            self._filter_by_category("全部")
            return

        # 搜索插件
        results = self.plugin_manager.search(query)
        self._display_plugins(results)

    def _filter_by_category(self, category: str):
        """按分类筛选"""
        self.current_category = category
        self._select_category_button(category)

        if category == "全部":
            plugins = self.plugin_manager.get_all_plugins()
        else:
            plugins = self.plugin_manager.get_by_category(category)

        # 考虑搜索关键词
        query = self.search_var.get().strip()
        if query:
            filtered = []
            for plugin in plugins:
                if (query in plugin.name.lower() or
                        query in plugin.description.lower()):
                    filtered.append(plugin)
            plugins = filtered

        self._display_plugins(plugins)

    def _select_category_button(self, category: str):
        """选中分类按钮"""
        categories = ["全部"] + self.plugin_manager.get_categories()

        for i, cat in enumerate(categories):
            if cat == category:
                # 高亮选中
                self.category_buttons[i].configure(
                    fg_color="#1f6aa5"
                )
            else:
                # 取消高亮
                self.category_buttons[i].configure(
                    fg_color="gray"
                )

    def _display_plugins(self, plugins: List):
        """显示插件列表"""
        self._clear_plugin_list()

        for plugin in plugins:
            widget = self._create_plugin_widget(plugin)
            self.plugin_widgets.append(widget)

    def _execute_plugin(self, plugin):
        """执行插件"""
        logging.info(f"开始执行插件: {plugin.name} ({plugin.id})")

        # 禁用按钮防止重复点击
        for widget in self.plugin_widgets:
            if hasattr(widget, 'plugin') and widget.plugin == plugin:
                widget.execute_btn.configure(state="disabled", text="执行中...")
                break

        # 在后台线程执行
        def run():
            try:
                result = self.plugin_manager.execute_plugin(plugin.id)
                logging.info(f"插件执行完成: {plugin.name} - 成功={result.get('success', False)}, 消息={result.get('message', 'N/A')}")
            except Exception as e:
                logging.error(f"插件执行出错: {plugin.name} - {e}")
                result = {
                    "success": False,
                    "message": f"执行出错: {str(e)}",
                    "data": None
                }

            # 恢复按钮状态
            self.after(0, lambda: self._on_execute_complete(plugin, result))

        threading.Thread(target=run, daemon=True).start()

    def _on_execute_complete(self, plugin, result: Dict[str, Any]):
        """执行完成回调"""
        # 恢复按钮
        for widget in self.plugin_widgets:
            if hasattr(widget, 'plugin') and widget.plugin == plugin:
                btn_text = "⚠️ 执行" if plugin.dangerous else "执行"
                widget.execute_btn.configure(state="normal", text=btn_text)
                break

        # 显示结果
        self._show_result(plugin.name, result)

    def _show_result(self, title: str, result: Dict[str, Any]):
        """显示执行结果"""
        logging.info(f"显示结果对话框: 标题={title}, 成功={result.get('success')}, 消息={result.get('message', 'N/A')}")

        dialog = ResultDialog(self, title, result)
        dialog.lift()  # 确保对话框在最前面
        dialog.attributes('-topmost', True)  # macOS上置顶
        dialog.after_idle(dialog.attributes, '-topmost', False)  # 然后取消置顶
        dialog.wait_window()

    def _open_ai_chat(self):
        """打开AI对话窗口"""
        from .ai_chat_window import AIChatWindow

        chat_window = AIChatWindow(
            self,
            self.ai_matcher,
            self.plugin_manager
        )
        chat_window.show()

    def _open_settings(self):
        """打开设置窗口"""
        from .settings_window import SettingsWindow

        settings = SettingsWindow(self, self.config)
        settings.show()
        settings.focus_set()  # 确保窗口获得焦点

    def _open_log_window(self):
        """打开日志窗口"""
        from .log_window import LogWindow
        from pathlib import Path

        # 日志文件路径
        log_file = None
        if self.config:
            log_dir = Path(self.config.config_dir) / "logs"
            log_file = str(log_dir / "chelp.log")

        log_window = LogWindow(self, log_file)
        log_window.focus_set()


class ResultDialog(ctk.CTkToplevel):
    """结果对话框"""

    def __init__(self, parent, title: str, result: Dict[str, Any]):
        super().__init__(parent)

        self.title(title)
        self.geometry("400x250")
        self.resizable(False, False)

        # 居中显示
        self.transient(parent)
        self.grab_set()

        self._create_content(result)

    def _create_content(self, result: Dict[str, Any]):
        """创建内容"""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=30, pady=30)

        # 状态图标
        icon = "✅" if result.get("success") else "❌"
        icon_label = ctk.CTkLabel(
            frame,
            text=icon,
            font=("Microsoft YaHei", 48)
        )
        icon_label.pack(pady=(0, 20))

        # 消息
        msg_label = ctk.CTkLabel(
            frame,
            text=result.get("message", "操作完成"),
            font=("Microsoft YaHei", 14),
            wraplength=350
        )
        msg_label.pack(pady=(0, 20))

        # 关闭按钮
        close_btn = ctk.CTkButton(
            frame,
            text="关闭",
            width=100,
            height=35,
            command=self.destroy,
            font=("Microsoft YaHei", 13)
        )
        close_btn.pack()
