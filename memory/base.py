"""Memory 基类。

【负责人】C
【接口约定】见 docs/INTERFACES.md §3
"""

from abc import ABC, abstractmethod


class Memory(ABC):
    """对话历史的抽象基类。"""

    @abstractmethod
    def add(self, role: str, content: str) -> None:
        """添加一条消息。role 取 'system' / 'user' / 'assistant'"""
        ...

    @abstractmethod
    def get_messages(self) -> list[dict]:
        """返回 OpenAI 格式的 messages 列表，
        每条形如 {'role': 'user', 'content': '...'}"""
        ...

    @abstractmethod
    def clear(self) -> None:
        """清空所有历史"""
        ...
