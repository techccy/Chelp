"""
AI对话窗口
"""

import customtkinter as ctk
from typing import List, Dict, Any
import threading


class AIChatWindow(ctk.CTkToplevel):
    """AI对话窗口"""

    def __init__(self, parent, ai_matcher, plugin_manager):
        super().__init__(parent)

        self.ai_matcher = ai_matcher
        self.plugin_manager = plugin_manager
        self.chat_history: List[Dict] = []

        self._setup_window()
        self._create_widgets()

        # 欢迎消息
        self._add_message("assistant", "你好！我是电脑助手AI。你可以描述你遇到的问题，我会推荐合适的解决方案。")

    def _setup_window(self):
        """设置窗口"""
        self.title("🤖 AI助手")
        self.geometry("600x500")
        self.resizable(True, True)

        # 居中显示
        self.transient(self.master)
        self.grab_set()

    def _create_widgets(self):
        """创建界面组件"""
        # 聊天区域
        chat_frame = ctk.CTkFrame(self)
        chat_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # 滚动区域
        scroll_frame = ctk.CTkScrollableFrame(chat_frame)
        scroll_frame.pack(fill="both", expand=True)

        self.chat_container = scroll_frame

        # 输入区域
        input_frame = ctk.CTkFrame(self, height=80)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        input_frame.pack_propagate(False)

        # 输入框
        self.input_var = ctk.StringVar()
        input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="描述你遇到的问题...",
            textvariable=self.input_var,
            height=40,
            font=("Microsoft YaHei", 13)
        )
        input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        input_entry.bind("<Return>", lambda e: self._send_message())

        # 发送按钮
        send_btn = ctk.CTkButton(
            input_frame,
            text="发送",
            width=80,
            height=40,
            command=self._send_message,
            font=("Microsoft YaHei", 13)
        )
        send_btn.pack(side="right")

    def _add_message(self, role: str, content: str):
        """添加消息"""
        msg_frame = ctk.CTkFrame(self.chat_container, fg_color="transparent")

        if role == "user":
            msg_frame.pack(fill="x", pady=5, anchor="e")

            bubble = ctk.CTkFrame(
                msg_frame,
                fg_color="#1f6aa5",
                corner_radius=10
            )
            bubble.pack(side="right", padx=(50, 0), ipadx=15, ipady=10)

            label = ctk.CTkLabel(
                bubble,
                text=content,
                font=("Microsoft YaHei", 13),
                text_color="white",
                wraplength=350
            )
            label.pack()

        else:
            msg_frame.pack(fill="x", pady=5, anchor="w")

            bubble = ctk.CTkFrame(
                msg_frame,
                fg_color="#2b2b2b",
                corner_radius=10
            )
            bubble.pack(side="left", padx=(0, 50), ipadx=15, ipady=10)

            label = ctk.CTkLabel(
                bubble,
                text=content,
                font=("Microsoft YaHei", 13),
                wraplength=350
            )
            label.pack()

        # 滚动到底部
        self.chat_container._parent_canvas.yview_moveto(1.0)

    def _send_message(self):
        """发送消息"""
        content = self.input_var.get().strip()
        if not content:
            return

        # 清空输入框
        self.input_var.set("")

        # 显示用户消息
        self._add_message("user", content)
        self.chat_history.append({"role": "user", "content": content})

        # 禁用输入
        # self.input_entry.configure(state="disabled")

        # 在后台获取AI回复
        def run():
            response = self.ai_matcher.chat(content, self.chat_history)

            # 恢复输入并显示回复
            self.after(0, lambda: self._on_ai_response(response))

        threading.Thread(target=run, daemon=True).start()

    def _on_ai_response(self, response: str):
        """AI回复处理"""
        # 恢复输入
        # self.input_entry.configure(state="normal")

        # 显示AI回复
        self._add_message("assistant", response)
        self.chat_history.append({"role": "assistant", "content": response})

        # 尝试解析推荐的插件
        self._extract_plugin_recommendations(response)

    def _extract_plugin_recommendations(self, response: str):
        """从AI回复中提取插件推荐"""
        plugins = self.plugin_manager.get_all_plugins()

        for plugin in plugins:
            if plugin.name in response:
                # 添加快捷执行按钮
                self._add_plugin_button(plugin)

    def _add_plugin_button(self, plugin):
        """添加插件执行按钮"""
        btn_frame = ctk.CTkFrame(self.chat_container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5, anchor="w")

        btn = ctk.CTkButton(
            btn_frame,
            text=f"🔧 {plugin.name}",
            width=150,
            height=30,
            command=lambda p=plugin: self._execute_plugin(p),
            font=("Microsoft YaHei", 12)
        )
        btn.pack(side="left", padx=(50, 0))

        # 滚动到底部
        self.chat_container._parent_canvas.yview_moveto(1.0)

    def _execute_plugin(self, plugin):
        """执行插件"""
        result = self.plugin_manager.execute_plugin(plugin.id)

        # 显示执行结果
        result_msg = f"{plugin.name}：{'成功' if result['success'] else '失败'}\n{result['message']}"
        self._add_message("assistant", result_msg)
