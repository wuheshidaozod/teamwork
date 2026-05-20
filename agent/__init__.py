"""Agent 包：ReAct 智能体核心实现。

【负责人】A（组长）

模块：
    core.py    - Agent 主类
    prompt.py  - System Prompt
    parser.py  - LLM 输出解析（B 维护）
"""

from agent.core import Agent

__all__ = ["Agent"]
