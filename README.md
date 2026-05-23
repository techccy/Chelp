# Chelp - 电脑小助手

> 一个简单易用的Windows电脑辅助工具，帮助解决常见电脑问题

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey)

## 功能特性

- 🧹 **系统清理**: 磁盘清理、临时文件删除、回收站清空
- 🖥️ **显示恢复**: 一键恢复分辨率和显示缩放比例
- ⌨️ **输入法管理**: 重装微信输入法
- 🌐 **网络修复**: 自动诊断并修复网络连接问题
- 🚀 **启动项管理**: 管理开机自启动程序
- 🤖 **AI助手**: 自然语言描述问题，AI推荐解决方案
- 🔌 **插件系统**: 支持自定义插件扩展功能
- 📦 **自动更新**: 检测GitHub新版本并自动更新

## 截图

### 主界面
```
┌─────────────────────────────────────────────┐
│  Chelp - 电脑小助手                          │
├─────────────────────────────────────────────┤
│  🔍 搜索功能...  [AI助手🤖]                   │
├─────────────────────────────────────────────┤
│  分类: [全部] [系统清理] [显示] [输入法]        │
├─────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐           │
│  │ 🧹 磁盘清理  │  │ 🖥️ 显示恢复  │           │
│  │ 清理临时文件  │  │ 恢复分辨率   │           │
│  │   [执行]     │  │   [执行]    │           │
│  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────┘
```

## 安装

### 方式1: 直接下载exe（推荐）

从 [Releases](https://github.com/xxx/chelp/releases) 下载最新版本的安装包。

### 方式2: 从源码运行

```bash
# 克隆仓库
git clone https://github.com/xxx/chelp.git
cd chelp

# 安装依赖
pip install -r requirements.txt

# 运行程序
python src/main.py
```

## 使用方法

### 基本使用

1. **搜索功能**: 在搜索框输入关键词，快速找到需要的功能
2. **分类浏览**: 点击分类按钮，按类别浏览功能
3. **执行操作**: 点击功能卡片上的"执行"按钮

### AI助手

点击"AI助手"按钮，用自然语言描述你遇到的问题，AI会推荐合适的解决方案。

示例输入：
- "电脑很卡怎么办？"
- "网络连不上"
- "显示变小了"

### 添加自定义插件

在 `plugins/` 目录下创建新的Python文件：

```python
from src.plugins.base import PluginBase

class MyCustomPlugin(PluginBase):
    @property
    def id(self) -> str:
        return "my_plugin"

    @property
    def name(self) -> str:
        return "我的功能"

    @property
    def description(self) -> str:
        return "功能描述"

    @property
    def category(self) -> str:
        return "自定义"

    def execute(self):
        # 实现功能
        return {
            "success": True,
            "message": "执行成功",
            "data": None
        }
```

## 配置

配置文件位于 `~/.chelp/settings.yaml`：

```yaml
app:
  theme: light  # light/dark/system
  auto_update: true

ai:
  provider: deepseek
  api_key: "your-api-key"  # 在设置中配置
  hybrid_mode: true
```

## AI功能配置

要使用AI助手功能，需要配置API密钥：

1. 打开程序，点击"设置"
2. 在"AI设置"中填入API密钥
3. 选择使用的模型

支持的API提供商：
- DeepSeek（推荐，性价比高）
- OpenAI (GPT-4/GPT-3.5)
- 兼容OpenAI API的其他服务

## 开发

### 项目结构

```
chelp/
├── src/
│   ├── core/           # 核心模块
│   ├── plugins/        # 内置插件
│   ├── ui/             # 界面
│   └── main.py         # 入口
├── config/             # 配置文件
├── plugins/            # 用户插件
├── scripts/            # 构建脚本
└── requirements.txt
```

### 打包

```bash
# 使用PyInstaller打包
python scripts/build.py
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 致谢

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 现代化UI框架
- [DeepSeek](https://www.deepseek.com/) - AI API支持
