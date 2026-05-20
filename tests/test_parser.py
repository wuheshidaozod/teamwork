"""JSON 解析器单元测试 —— 项目最容易翻车的地方。

【负责人】D（用例设计）+ B（实现）
【目标】≥ 95% 通过率

运行：pytest tests/test_parser.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.parser import parse_action


class TestParser:
    """LLM 输出 7 种常见情况，全部要能解析。"""

    def test_standard_json(self):
        text = 'Thought: 算一算\nAction: {"tool": "calculator", "args": {"expression": "1+1"}}'
        result = parse_action(text)
        assert result == {"tool": "calculator", "args": {"expression": "1+1"}}

    def test_markdown_json_fence(self):
        text = '''Thought: 算一算
Action: ```json
{"tool": "calculator", "args": {"expression": "1+1"}}
```'''
        result = parse_action(text)
        assert result is not None
        assert result["tool"] == "calculator"

    def test_markdown_plain_fence(self):
        text = '''Action: ```
{"tool": "calculator", "args": {"expression": "1+1"}}
```'''
        result = parse_action(text)
        assert result is not None
        assert result["tool"] == "calculator"

    def test_chinese_punctuation(self):
        # LLM 偶尔用中文标点
        text = 'Action: {"tool"："calculator"，"args":{"expression":"1+1"}}'
        result = parse_action(text)
        assert result is not None
        assert result["tool"] == "calculator"

    def test_chinese_quotes(self):
        # 全角引号
        text = 'Action: {“tool”: “calculator”, “args”: {“expression”: “1+1”}}'
        result = parse_action(text)
        assert result is not None
        assert result["tool"] == "calculator"

    def test_extra_text_before_json(self):
        text = '''Thought: 我需要算一下这个
Action: 我要用计算器
{"tool": "calculator", "args": {"expression": "1+1"}}'''
        result = parse_action(text)
        assert result is not None
        assert result["tool"] == "calculator"

    def test_garbage_input(self):
        """完全不像 JSON 的输入应返回 None"""
        assert parse_action("这不是 JSON") is None
        assert parse_action("") is None
        assert parse_action(None) is None

    def test_missing_tool_key(self):
        """缺少 tool 键应返回 None"""
        text = 'Action: {"args": {"x": 1}}'
        assert parse_action(text) is None

    def test_args_normalization(self):
        """没有 args 的情况应自动补 {}"""
        text = 'Action: {"tool": "calculator"}'
        result = parse_action(text)
        assert result == {"tool": "calculator", "args": {}}
