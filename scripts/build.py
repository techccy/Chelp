"""
打包脚本
使用PyInstaller将程序打包为exe
"""

import os
import subprocess
import shutil


def build():
    """执行打包"""
    print("开始打包 Chelp...")

    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("请先安装 PyInstaller: pip install pyinstaller")
        return

    # 路径分隔符（Windows用;，其他用:）
    path_sep = ";" if os.name == "nt" else ":"

    # PyInstaller参数
    params = [
        "pyinstaller",
        "--name=Chelp",
        "--onefile",
        "--windowed",
        "--icon=assets/icon.ico" if os.path.exists("assets/icon.ico") else "",
        f"--add-data=src/core{path_sep}src/core",
        f"--add-data=src/ui{path_sep}src/ui",
        f"--add-data=src/plugins{path_sep}src/plugins",
        f"--add-data=config{path_sep}config",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=core.config",
        "--hidden-import=core.plugin_manager",
        "--hidden-import=core.ai_matcher",
        "--hidden-import=core.updater",
        "--hidden-import=ui.main_window",
        "--hidden-import=ui.ai_chat_window",
        "--hidden-import=ui.settings_window",
        "--hidden-import=plugins.base",
        "--hidden-import=plugins.disk_cleaner",
        "--hidden-import=plugins.display_fixer",
        "--hidden-import=plugins.input_method",
        "--hidden-import=plugins.network_fixer",
        "--hidden-import=plugins.startup_manager",
        "--noconfirm",
        "src/main.py"
    ]

    # 过滤空参数
    params = [p for p in params if p]

    print(f"执行命令: {' '.join(params)}")

    # 执行打包
    result = subprocess.run(params, capture_output=True, text=True)

    if result.returncode == 0:
        print("\n✅ 打包成功！")
        print("输出文件: dist/Chelp.exe")
    else:
        print("\n❌ 打包失败:")
        print(result.stderr)


if __name__ == "__main__":
    build()
