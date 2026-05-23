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

    # PyInstaller参数
    params = [
        "pyinstaller",
        "--name=Chelp",
        "--onefile",
        "--windowed",
        "--icon=assets/icon.ico" if os.path.exists("assets/icon.ico") else "",
        "--add-data=src:src",
        "--add-data=config:config",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
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
