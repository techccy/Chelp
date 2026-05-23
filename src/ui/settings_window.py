"""
设置窗口
"""

import customtkinter as ctk
import os


class SettingsWindow(ctk.CTkToplevel):
    """设置窗口"""

    def __init__(self, parent, config):
        super().__init__(parent)

        self.config = config

        self._setup_window()
        self._create_widgets()
        self._load_settings()

    def _setup_window(self):
        """设置窗口"""
        self.title("设置")
        self.geometry("500x450")
        self.resizable(False, False)

        # 居中显示
        self.transient(self.master)
        self.grab_set()

    def _create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 外观设置
        self._create_appearance_section(main_frame)

        # AI设置
        self._create_ai_section(main_frame)

        # 保存按钮
        save_btn = ctk.CTkButton(
            self,
            text="保存",
            width=100,
            height=35,
            command=self._save_settings,
            font=("Microsoft YaHei", 13)
        )
        save_btn.pack(pady=10)

    def _create_appearance_section(self, parent):
        """外观设置部分"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 15))

        # 标题
        title = ctk.CTkLabel(
            section,
            text="🎨 外观",
            font=("Microsoft YaHei", 15, "bold")
        )
        title.pack(anchor="w", padx=15, pady=(15, 10))

        # 主题选择
        theme_frame = ctk.CTkFrame(section, fg_color="transparent")
        theme_frame.pack(fill="x", padx=15, pady=(0, 15))

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="主题：",
            font=("Microsoft YaHei", 13)
        )
        theme_label.pack(side="left")

        self.theme_var = ctk.StringVar(value=self.config.theme)

        light_radio = ctk.CTkRadioButton(
            theme_frame,
            text="浅色",
            variable=self.theme_var,
            value="light",
            font=("Microsoft YaHei", 12)
        )
        light_radio.pack(side="left", padx=10)

        dark_radio = ctk.CTkRadioButton(
            theme_frame,
            text="深色",
            variable=self.theme_var,
            value="dark",
            font=("Microsoft YaHei", 12)
        )
        dark_radio.pack(side="left", padx=10)

        system_radio = ctk.CTkRadioButton(
            theme_frame,
            text="跟随系统",
            variable=self.theme_var,
            value="system",
            font=("Microsoft YaHei", 12)
        )
        system_radio.pack(side="left", padx=10)

    def _create_ai_section(self, parent):
        """AI设置部分"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 15))

        # 标题
        title = ctk.CTkLabel(
            section,
            text="🤖 AI设置",
            font=("Microsoft YaHei", 15, "bold")
        )
        title.pack(anchor="w", padx=15, pady=(15, 10))

        # API密钥
        api_frame = ctk.CTkFrame(section, fg_color="transparent")
        api_frame.pack(fill="x", padx=15, pady=(0, 10))

        api_label = ctk.CTkLabel(
            api_frame,
            text="API密钥：",
            font=("Microsoft YaHei", 12),
            width=80
        )
        api_label.pack(side="left")

        self.api_key_var = ctk.StringVar(value=self.config.ai_api_key)

        api_entry = ctk.CTkEntry(
            api_frame,
            textvariable=self.api_key_var,
            placeholder_text="sk-...",
            show="*",
            font=("Microsoft YaHei", 12)
        )
        api_entry.pack(side="left", fill="x", expand=True)

        # 提示
        hint_label = ctk.CTkLabel(
            section,
            text="💡 使用DeepSeek API获取AI功能支持",
            font=("Microsoft YaHei", 11),
            text_color="gray"
        )
        hint_label.pack(anchor="w", padx=15, pady=(0, 15))

        # 模型选择
        model_frame = ctk.CTkFrame(section, fg_color="transparent")
        model_frame.pack(fill="x", padx=15, pady=(0, 15))

        model_label = ctk.CTkLabel(
            model_frame,
            text="模型：",
            font=("Microsoft YaHei", 12),
            width=80
        )
        model_label.pack(side="left")

        self.model_var = ctk.StringVar(value=self.config.ai_model)

        model_combo = ctk.CTkOptionMenu(
            model_frame,
            variable=self.model_var,
            values=["deepseek-chat", "gpt-4o-mini", "gpt-3.5-turbo"],
            font=("Microsoft YaHei", 12)
        )
        model_combo.pack(side="left", fill="x", expand=True)

        # 混合模式开关
        hybrid_frame = ctk.CTkFrame(section, fg_color="transparent")
        hybrid_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.hybrid_var = ctk.BooleanVar(value=self.config.hybrid_mode)

        hybrid_switch = ctk.CTkSwitch(
            hybrid_frame,
            text="混合模式（先关键词后AI）",
            variable=self.hybrid_var,
            font=("Microsoft YaHei", 12)
        )
        hybrid_switch.pack(side="left")

    def _load_settings(self):
        """加载设置"""
        # 已在创建时加载
        pass

    def _save_settings(self):
        """保存设置"""
        # 保存主题
        self.config.theme = self.theme_var.get()
        ctk.set_appearance_mode(self.theme_var.get())

        # 保存AI设置
        self.config.ai_api_key = self.api_key_var.get()
        self.config.set("ai.model", self.model_var.get())
        self.config.set("ai.hybrid_mode", self.hybrid_var.get())

        # 保存到文件
        self.config.save()

        # 显示保存成功提示
        self._show_save_success()

    def _show_save_success(self):
        """显示保存成功提示"""
        # 简单闪烁按钮
        original = self.title()
        self.title("设置 ✅ 已保存")

        import tkinter as tk
        self.after(1500, lambda: self.title(original))
