"""
日志窗口模块
显示程序运行日志
"""

import customtkinter as ctk
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


class LogHandler(logging.Handler):
    """自定义日志处理器，将日志发送到窗口"""

    def __init__(self):
        super().__init__()
        self.callbacks = []

    def emit(self, record):
        """发送日志记录"""
        try:
            msg = self.format(record)
            for callback in self.callbacks:
                callback(msg, record.levelno)
        except Exception:
            self.handleError(record)

    def add_callback(self, callback):
        """添加回调函数"""
        self.callbacks.append(callback)

    def remove_callback(self, callback):
        """移除回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)


# 全局日志处理器
_log_handler: Optional[LogHandler] = None


def get_log_handler() -> LogHandler:
    """获取全局日志处理器"""
    global _log_handler
    if _log_handler is None:
        _log_handler = LogHandler()
        _log_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        ))
    return _log_handler


class LogWindow(ctk.CTkToplevel):
    """日志窗口"""

    def __init__(self, parent, log_file: str = None):
        super().__init__(parent)

        self.log_file = log_file
        self.auto_scroll = True
        self.log_buffer = []
        self.max_lines = 5000  # 最大行数

        self._setup_window()
        self._create_widgets()
        self._connect_logger()
        self._load_existing_logs()

    def _setup_window(self):
        """设置窗口"""
        self.title("运行日志")
        self.geometry("900x600")
        self.resizable(True, True)

        # 居中显示
        self.transient(self.master)
        self.grab_set()

    def _create_widgets(self):
        """创建界面组件"""
        # 工具栏
        toolbar = ctk.CTkFrame(self, height=50)
        toolbar.pack(fill="x", padx=10, pady=(10, 5))
        toolbar.pack_propagate(False)

        # 清空按钮
        clear_btn = ctk.CTkButton(
            toolbar,
            text="清空",
            width=80,
            height=35,
            command=self._clear_logs,
            font=("Microsoft YaHei", 12)
        )
        clear_btn.pack(side="left", padx=5)

        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            toolbar,
            text="刷新",
            width=80,
            height=35,
            command=self._refresh_logs,
            font=("Microsoft YaHei", 12)
        )
        refresh_btn.pack(side="left", padx=5)

        # 导出按钮
        export_btn = ctk.CTkButton(
            toolbar,
            text="导出",
            width=80,
            height=35,
            command=self._export_logs,
            font=("Microsoft YaHei", 12)
        )
        export_btn.pack(side="left", padx=5)

        # 自动滚动开关
        self.scroll_var = ctk.BooleanVar(value=True)
        scroll_switch = ctk.CTkSwitch(
            toolbar,
            text="自动滚动",
            variable=self.scroll_var,
            command=self._toggle_auto_scroll,
            font=("Microsoft YaHei", 12)
        )
        scroll_switch.pack(side="left", padx=15)

        # 日志级别筛选
        level_label = ctk.CTkLabel(
            toolbar,
            text="级别：",
            font=("Microsoft YaHei", 12)
        )
        level_label.pack(side="left", padx=(20, 5))

        self.level_var = ctk.StringVar(value="全部")
        level_combo = ctk.CTkOptionMenu(
            toolbar,
            variable=self.level_var,
            values=["全部", "DEBUG", "INFO", "WARNING", "ERROR"],
            width=100,
            height=35,
            command=self._filter_logs,
            font=("Microsoft YaHei", 12)
        )
        level_combo.pack(side="left", padx=5)

        # 日志显示区
        text_frame = ctk.CTkFrame(self)
        text_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self.text_widget = ctk.CTkTextbox(
            text_frame,
            font=("Consolas", 11),
            wrap="char"
        )
        self.text_widget.pack(fill="both", expand=True, padx=5, pady=5)

        # 配置标签颜色
        self.text_widget.tag_config("DEBUG", foreground="gray")
        self.text_widget.tag_config("INFO", foreground="black")
        self.text_widget.tag_config("WARNING", foreground="#FF9500")
        self.text_widget.tag_config("ERROR", foreground="red")
        self.text_widget.tag_config("CRITICAL", foreground="darkred", font=("Consolas", 11, "bold"))

    def _connect_logger(self):
        """连接日志处理器"""
        handler = get_log_handler()
        handler.add_callback(self._append_log)

    def _load_existing_logs(self):
        """加载已有的日志文件"""
        if self.log_file and Path(self.log_file).exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content:
                        self._append_text(content)
            except Exception as e:
                self._append_log(f"加载日志文件失败: {e}\n", logging.WARNING)

    def _append_log(self, message: str, level: int = logging.INFO):
        """追加日志"""
        # 确定标签
        if level >= logging.CRITICAL:
            tag = "CRITICAL"
        elif level >= logging.ERROR:
            tag = "ERROR"
        elif level >= logging.WARNING:
            tag = "WARNING"
        elif level >= logging.INFO:
            tag = "INFO"
        else:
            tag = "DEBUG"

        # 检查筛选
        current_filter = self.level_var.get()
        if current_filter != "全部":
            filter_level = getattr(logging, current_filter)
            if level < filter_level:
                return

        # 添加到缓冲区
        self.log_buffer.append((message + "\n", tag))

        # 限制行数
        if len(self.log_buffer) > self.max_lines:
            self.log_buffer = self.log_buffer[-self.max_lines:]

        # 在主线程更新UI
        self.after_idle(self._update_display)

    def _update_display(self):
        """更新显示"""
        if not self.log_buffer:
            return

        # 获取当前内容位置
        current_pos = self.text_widget.index("end-1c")

        # 批量添加
        for msg, tag in self.log_buffer:
            self.text_widget.insert("end", msg, tag)

        self.log_buffer.clear()

        # 自动滚动
        if self.scroll_var.get():
            self.text_widget.see("end")

    def _append_text(self, text: str):
        """直接添加文本"""
        self.text_widget.insert("end", text)

    def _clear_logs(self):
        """清空日志"""
        self.text_widget.delete("1.0", "end")
        self.log_buffer.clear()

    def _refresh_logs(self):
        """刷新日志"""
        self._clear_logs()
        self._load_existing_logs()

    def _export_logs(self):
        """导出日志"""
        from tkinter import filedialog
        from datetime import datetime

        filename = filedialog.asksaveasfilename(
            title="导出日志",
            defaultextension=".txt",
            initialfile=f"chelp_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )

        if filename:
            try:
                content = self.text_widget.get("1.0", "end-1c")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.title(f"运行日志 - 已导出到 {Path(filename).name}")
                self.after(2000, lambda: self.title("运行日志"))
            except Exception as e:
                self._append_log(f"导出失败: {e}\n", logging.ERROR)

    def _toggle_auto_scroll(self):
        """切换自动滚动"""
        self.auto_scroll = self.scroll_var.get()

    def _filter_logs(self, value):
        """筛选日志（仅影响新增日志）"""
        pass

    def destroy(self):
        """关闭窗口"""
        handler = get_log_handler()
        try:
            handler.remove_callback(self._append_log)
        except ValueError:
            pass
        super().destroy()


def setup_logging(log_file: str = None, level: int = logging.INFO) -> LogHandler:
    """设置日志系统"""
    # 创建logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # 清除现有处理器
    logger.handlers.clear()

    # 获取自定义处理器
    handler = get_log_handler()
    handler.setLevel(level)
    logger.addHandler(handler)

    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(
            log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return handler
