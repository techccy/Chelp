"""
AI功能匹配模块
使用混合模式进行自然语言-功能匹配
"""

import json
import re
from typing import List, Optional, Dict, Any
from openai import OpenAI


class AIMatcher:
    """混合模式：关键词匹配 + AI模型"""

    def __init__(self, plugins: List, config: Dict[str, Any] = None):
        self.plugins = plugins
        self.config = config or {}
        self.plugins_index = self._build_index()
        self.client = None

        # 初始化AI客户端
        api_key = self.config.get("ai_api_key", "")
        if api_key:
            base_url = self.config.get("api_base", "https://api.deepseek.com")
            self.client = OpenAI(api_key=api_key, base_url=base_url)

    def _build_index(self) -> str:
        """构建插件索引文本"""
        index_lines = []
        for plugin in self.plugins:
            keywords = ", ".join(plugin.keywords)
            index_lines.append(
                f"- {plugin.name} ({plugin.id}): {plugin.description}\n"
                f"  分类: {plugin.category} | 关键词: {keywords}"
            )
        return "\n".join(index_lines)

    def _keyword_match(self, user_input: str) -> Optional[List]:
        """关键词精确匹配"""
        user_input = user_input.lower()
        results = []
        exact_match = None

        for plugin in self.plugins:
            # 精确匹配名称
            if user_input == plugin.name.lower():
                exact_match = plugin
                break

            # 包含匹配
            if user_input in plugin.name.lower():
                results.append(plugin)
                continue

            # 关键词匹配
            for keyword in plugin.keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in user_input or user_input in keyword_lower:
                    results.append(plugin)
                    break

        return [exact_match] if exact_match else (results if results else None)

    def _ai_match(self, user_input: str) -> List:
        """调用DeepSeek API进行语义匹配"""
        if not self.client:
            return self._keyword_match(user_input) or []

        try:
            prompt = f"""你是一个电脑助手功能推荐系统。根据用户问题，从以下可用功能中选择最合适的1-3个。

可用功能列表：
{self.plugins_index}

用户问题：{user_input}

请以JSON格式返回，格式如下：
{{
    "recommendations": [
        {{"plugin_id": "xxx", "reason": "推荐理由"}},
        {{"plugin_id": "yyy", "reason": "推荐理由"}}
    ]
}}

只返回JSON，不要其他内容。"""

            response = self.client.chat.completions.create(
                model=self.config.get("ai_model", "deepseek-chat"),
                messages=[
                    {"role": "system", "content": "你是电脑助手功能推荐系统。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            result_text = response.choices[0].message.content.strip()

            # 提取JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result = json.loads(json_match.group())
                plugin_ids = [r["plugin_id"] for r in result.get("recommendations", [])]

                matched_plugins = []
                for pid in plugin_ids:
                    for plugin in self.plugins:
                        if plugin.id == pid:
                            matched_plugins.append(plugin)
                            break
                return matched_plugins

        except Exception as e:
            print(f"AI匹配失败: {e}")

        # 回退到关键词匹配
        return self._keyword_match(user_input) or []

    def match(self, user_input: str) -> List:
        """混合匹配策略"""
        # 1. 先尝试关键词精确匹配（快速）
        keyword_results = self._keyword_match(user_input)
        if keyword_results and len(keyword_results) == 1:
            return keyword_results

        # 2. 如果是混合模式，尝试AI匹配
        if self.config.get("hybrid_mode", True):
            return self._ai_match(user_input)

        # 3. 否则返回关键词匹配结果
        return keyword_results or []

    def chat(self, user_input: str, context: List[Dict] = None) -> str:
        """AI对话模式"""
        if not self.client:
            return "请先配置AI API密钥"

        try:
            system_prompt = f"""你是Chelp电脑助手的AI助手。你可以帮助用户解决电脑问题。

当前可用的功能列表：
{self.plugins_index}

当用户提出问题时：
1. 理解用户的问题
2. 从功能列表中推荐合适的解决方案
3. 如果有相关功能，说明如何使用
4. 提供友好的建议和步骤

用简洁、友好的语气回复，使用emoji让回复更生动。"""

            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # 添加上下文
            if context:
                messages.extend(context[-4:])  # 保留最近4条对话

            messages.append({"role": "user", "content": user_input})

            response = self.client.chat.completions.create(
                model=self.config.get("ai_model", "deepseek-chat"),
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"抱歉，AI助手暂时无法响应：{str(e)}"
