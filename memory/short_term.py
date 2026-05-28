"""短期记忆 —— 滑窗 + token 截断。

【负责人】C
【完成时间】第 2 周（本文件已给出完整可用实现）

【核心策略】
- 用 tiktoken 估算 token 数
- 超出 max_tokens 时，从最早的非 system 消息开始丢弃
- 保留 system prompt 始终在首位
"""

from memory.base import Memory
from config import MAX_CONTEXT_TOKENS


def _get_encoder():
    try:
        import tiktoken
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


_ENCODER = _get_encoder()  # 进程级单例，避免每个实例重复初始化


def _count(text: str) -> int:
    if _ENCODER:
        return len(_ENCODER.encode(text))
    zh = sum(1 for c in text if "一" <= c <= "鿿")
    return int(zh * 1.5 + (len(text) - zh) * 0.3)


class ShortTermMemory(Memory):
    """滑窗式短期记忆（增量 token 计数）。"""

    def __init__(self, max_tokens: int = MAX_CONTEXT_TOKENS):
        self._messages: list[dict] = []
        self._token_counts: list[int] = []  # 与 _messages 一一对应
        self._total: int = 0
        self.max_tokens = max_tokens

    def add(self, role: str, content: str) -> None:
        tokens = _count(content)
        self._messages.append({"role": role, "content": content})
        self._token_counts.append(tokens)
        self._total += tokens
        self._truncate_if_needed()

    def get_messages(self) -> list[dict]:
        return [dict(m) for m in self._messages]

    def clear(self) -> None:
        self._messages.clear()
        self._token_counts.clear()
        self._total = 0

    def _truncate_if_needed(self) -> None:
        while self._total > self.max_tokens and len(self._messages) > 2:
            for i, m in enumerate(self._messages):
                if m["role"] != "system":
                    self._total -= self._token_counts[i]
                    self._messages.pop(i)
                    self._token_counts.pop(i)
                    break
            else:
                break

    def __len__(self) -> int:
        return len(self._messages)

    def __repr__(self) -> str:
        return (f"<ShortTermMemory msgs={len(self._messages)} "
                f"tokens≈{self._total}/{self.max_tokens}>")
