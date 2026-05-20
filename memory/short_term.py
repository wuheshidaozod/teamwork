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


# 延迟导入 tiktoken，万一 C 还没装，让其他模块还能用
def _get_encoder():
    """获取 token 编码器，失败时返回 None（fallback 到字符数）"""
    try:
        import tiktoken
        # cl100k_base 是 GPT-3.5/4 用的编码，对中文统计也基本合理
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


class ShortTermMemory(Memory):
    """滑窗式短期记忆。"""

    def __init__(self, max_tokens: int = MAX_CONTEXT_TOKENS):
        self._messages: list[dict] = []
        self._encoder = _get_encoder()
        self.max_tokens = max_tokens

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})
        self._truncate_if_needed()

    def get_messages(self) -> list[dict]:
        # 返回副本，防止外部修改
        return [dict(m) for m in self._messages]

    def clear(self) -> None:
        self._messages.clear()

    # ===== 内部 =====
    def _count_tokens(self, text: str) -> int:
        if self._encoder:
            return len(self._encoder.encode(text))
        # fallback：粗略估算（中文 1.5 token/字，英文 0.3 token/字）
        zh_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        en_chars = len(text) - zh_chars
        return int(zh_chars * 1.5 + en_chars * 0.3)

    def _total_tokens(self) -> int:
        return sum(self._count_tokens(m["content"]) for m in self._messages)

    def _truncate_if_needed(self) -> None:
        """超出上限就从最早的非 system 消息开始丢弃。"""
        while (self._total_tokens() > self.max_tokens
               and len(self._messages) > 2):
            # 找到第一个非 system 消息删除
            for i, m in enumerate(self._messages):
                if m["role"] != "system":
                    self._messages.pop(i)
                    break
            else:
                # 全是 system（不应该发生），保险起见跳出
                break

    def __len__(self) -> int:
        return len(self._messages)

    def __repr__(self) -> str:
        return (f"<ShortTermMemory msgs={len(self._messages)} "
                f"tokens≈{self._total_tokens()}/{self.max_tokens}>")
