"""
设置窗口
"""

import customtkinter as ctk
import os
import logging
from pathlib import Path


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
        self.geometry("500x600")
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

        # 显示设置
        self._create_display_section(main_frame)
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

        # 导入导出按钮
        io_frame = ctk.CTkFrame(self, fg_color="transparent")
        io_frame.pack(pady=(0, 10))

        import_btn = ctk.CTkButton(
            io_frame,
            text="📥 导入配置",
            width=120,
            height=35,
            command=self._import_config,
            font=("Microsoft YaHei", 12)
        )
        import_btn.pack(side="left", padx=5)

        export_btn = ctk.CTkButton(
            io_frame,
            text="📤 导出配置",
            width=120,
            height=35,
            command=self._export_config,
            font=("Microsoft YaHei", 12)
        )
        export_btn.pack(side="left", padx=5)

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

    def _create_display_section(self, parent):
        """显示设置部分"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 15))

        # 标题
        title = ctk.CTkLabel(
            section,
            text="🖥️ 显示设置",
            font=("Microsoft YaHei", 15, "bold")
        )
        title.pack(anchor="w", padx=15, pady=(15, 10))

        # 分辨率输入
        res_frame = ctk.CTkFrame(section, fg_color="transparent")
        res_frame.pack(fill="x", padx=15, pady=(0, 10))

        res_label = ctk.CTkLabel(
            res_frame,
            text="分辨率：",
            font=("Microsoft YaHei", 12),
            width=80
        )
        res_label.pack(side="left")

        self.resolution_var = ctk.StringVar(
            value=self.config.get("saved_state.display.resolution", "1920x1080")
        )

        res_entry = ctk.CTkEntry(
            res_frame,
            textvariable=self.resolution_var,
            placeholder_text="1920x1080",
            font=("Microsoft YaHei", 12)
        )
        res_entry.pack(side="left", fill="x", expand=True)

        # 缩放比例滑块
        scale_frame = ctk.CTkFrame(section, fg_color="transparent")
        scale_frame.pack(fill="x", padx=15, pady=(0, 10))

        scale_label = ctk.CTkLabel(
            scale_frame,
            text="比例%：",
            font=("Microsoft YaHei", 12),
            width=80
        )
        scale_label.pack(side="left")

        self.scale_var = ctk.IntVar(
            value=self.config.get("saved_state.display.scale", 100)
        )

        scale_slider = ctk.CTkSlider(
            scale_frame,
            from_=50,
            to=200,
            variable=self.scale_var,
            number_of_steps=15,
            font=("Microsoft YaHei", 12)
        )
        scale_slider.pack(side="left", fill="x", expand=True)

        self.scale_val_label = ctk.CTkLabel(
            scale_frame,
            text="100",
            font=("Microsoft YaHei", 12)
        )
        self.scale_val_label.pack(side="left", padx=5)

        # 更新滑块值显示
        def update_scale_label(value):
            self.scale_val_label.configure(text=f"{int(value)}")

        scale_slider.configure(command=update_scale_label)

        # 自动读取当前分辨率复选框
        auto_frame = ctk.CTkFrame(section, fg_color="transparent")
        auto_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.auto_read_var = ctk.BooleanVar(
            value=self.config.get("saved_state.display.auto_read", False)
        )

        auto_check = ctk.CTkCheckBox(
            auto_frame,
            text="读取当前分辨率作为标准分辨率",
            variable=self.auto_read_var,
            font=("Microsoft YaHei", 12)
        )
        auto_check.pack(side="left")

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

        # 保存显示设置
        self.config.set("saved_state.display.resolution", self.resolution_var.get())
        self.config.set("saved_state.display.scale", self.scale_var.get())
        self.config.set("saved_state.display.auto_read", self.auto_read_var.get())

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

    def _export_config(self):
        """导出配置到JSON文件"""
        try:
            from tkinter import filedialog
            from datetime import datetime

            # 默认文件名
            default_name = f"chelp_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            file_path = filedialog.asksaveasfilename(
                title="导出配置",
                defaultextension=".json",
                initialfile=default_name,
                filetypes=[
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )

            if file_path:
                exported_path = self.config.export_to_json(file_path)
                self.title("设置 ✅ 配置已导出")
                self.after(2000, lambda: self.title("设置"))
                logging.info(f"配置已导出到: {exported_path}")

        except Exception as e:
            self.title(f"设置 ❌ 导出失败: {str(e)}")
            self.after(3000, lambda: self.title("设置"))
            logging.error(f"导出配置失败: {e}")

    def _import_config(self):
        """从JSON文件导入配置"""
        try:
            from tkinter import filedialog
            import tkinter.messagebox as messagebox

            file_path = filedialog.askopenfilename(
                title="导入配置",
                filetypes=[
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )

            if file_path:
                # 确认导入
                confirm = messagebox.askyesno(
                    "确认导入",
                    "导入配置将覆盖当前设置，是否继续？"
                )

                if confirm:
                    success = self.config.import_from_json(file_path, merge=True)

                    if success:
                        # 重新加载界面
                        self._reload_widgets()

                        self.title("设置 ✅ 配置已导入")
                        self.after(2000, lambda: self.title("设置"))
                        logging.info(f"配置已从文件导入: {file_path}")
                    else:
                        self.title("设置 ❌ 导入失败")
                        self.after(2000, lambda: self.title("设置"))

        except Exception as e:
            self.title(f"设置 ❌ 导入失败: {str(e)}")
            self.after(3000, lambda: self.title("设置"))
            logging.error(f"导入配置失败: {e}")

    def _reload_widgets(self):
        """重新加载界面组件"""
        # 更新主题选择
        if hasattr(self, 'theme_var'):
            self.theme_var.set(self.config.theme)

        # 更新显示设置
        if hasattr(self, 'resolution_var'):
            self.resolution_var.set(self.config.get("saved_state.display.resolution", "1920x1080"))
        if hasattr(self, 'scale_var'):
            self.scale_var.set(self.config.get("saved_state.display.scale", 100))
        if hasattr(self, 'auto_read_var'):
            self.auto_read_var.set(self.config.get("saved_state.display.auto_read", False))

        # 更新API密钥
        if hasattr(self, 'api_key_var'):
            self.api_key_var.set(self.config.ai_api_key)

        # 更新模型选择
        if hasattr(self, 'model_var'):
            self.model_var.set(self.config.ai_model)

        # 更新混合模式开关
        if hasattr(self, 'hybrid_var'):
            self.hybrid_var.set(self.config.hybrid_mode)
