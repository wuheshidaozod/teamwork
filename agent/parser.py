"""LLM 输出解析器。

【负责人】B
【完成时间】第 2 周

【目标】95% 解析成功率（在 tests/test_parser.py 的样本上）

LLM 输出经常"不老实"，必须容错处理：
    1. 标准 JSON
    2. ```json ... ``` 包裹
    3. ``` ... ``` 包裹
    4. 中文标点（：，"")
    5. Action 关键字前后多余空白
    6. 解释文字 + JSON 混在一起
"""

import re
import json


def parse_action(text: str) -> dict | None:
    """从 LLM 输出中提取 Action JSON。

    Args:
        text: LLM 完整输出

    Returns:
        {"tool": str, "args": dict} 或 None（解析失败）
    """
    if not text:
        return None

    # 1) 剥 markdown 代码围栏
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = cleaned.replace("```", "")

    # 2) 中文标点替换
    cleaned = (cleaned
               .replace("：", ":")
               .replace("，", ",")
               .replace("\u201c", '"').replace("\u201d", '"')   # 中文双引号 " "
               .replace("\u2018", "'").replace("\u2019", "'"))  # 中文单引号 ' '

    # 3) 优先匹配 "Action:" 后的 JSON
    m = re.search(r"Action\s*:\s*(\{.*?\})(?=\n\s*(?:Observation|Thought|Final|$)|\Z)",
                  cleaned, re.DOTALL)
    if m:
        candidate = m.group(1)
        result = _try_parse(candidate)
        if result:
            return result

    # 4) 兜底：找第一个看起来像 Action 的 JSON 对象
    for m in re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", cleaned, re.DOTALL):
        result = _try_parse(m.group(0))
        if result:
            return result

    return None


def _try_parse(candidate: str) -> dict | None:
    """尝试解析单个候选字符串。"""
    try:
        result = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    if not isinstance(result, dict):
        return None
    if "tool" not in result:
        return None
    # 规范化 args 为字典
    if "args" not in result:
        result["args"] = {}
    elif not isinstance(result["args"], dict):
        return None
    return result
