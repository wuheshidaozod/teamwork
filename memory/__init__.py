"""对话历史与记忆模块。

【负责人】C

模块：
    base.py        - Memory 基类
    short_term.py  - 短期记忆（必做）
    long_term.py   - 长期记忆（进阶，第 3 周）
"""

from memory.base import Memory
from memory.short_term import ShortTermMemory

__all__ = ["Memory", "ShortTermMemory"]
