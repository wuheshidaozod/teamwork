"""长期记忆 —— 向量检索（进阶）。

【负责人】C
【完成时间】第 3 周（进阶项，时间不够可砍掉）

【实现策略】
1. 用 sentence-transformers 把每条对话编码成向量
2. 存到本地 JSON / pickle
3. 查询时用 numpy 手写余弦相似度（不准用 langchain/faiss 的高层封装）

【依赖】pip install sentence-transformers
"""

import json
from pathlib import Path

from memory.base import Memory


class LongTermMemory(Memory):
    """基于向量检索的长期记忆。

    TODO(C 第 3 周): 完整实现

    参考骨架：

    def __init__(self, store_path: str = "memory/long_term_store.json",
                 model_name: str = "shibing624/text2vec-base-chinese"):
        from sentence_transformers import SentenceTransformer
        import numpy as np

        self.store_path = Path(store_path)
        self.model = SentenceTransformer(model_name)
        self._memories: list[dict] = []  # [{"text": str, "vec": list[float]}]
        self._load()

    def add(self, role: str, content: str) -> None:
        vec = self.model.encode(content).tolist()
        self._memories.append({"role": role, "text": content, "vec": vec})
        self._save()

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        import numpy as np
        if not self._memories:
            return []
        q_vec = self.model.encode(query)
        # 手写余弦相似度
        mat = np.array([m["vec"] for m in self._memories])
        sims = mat @ q_vec / (
            np.linalg.norm(mat, axis=1) * np.linalg.norm(q_vec) + 1e-8)
        top_indices = sims.argsort()[-top_k:][::-1]
        return [self._memories[i]["text"] for i in top_indices]

    def get_messages(self) -> list[dict]:
        # 长期记忆通常不直接作为 messages 返回，而是被 retrieve 后注入 prompt
        return []

    def clear(self) -> None:
        self._memories = []
        self._save()

    def _save(self):
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.store_path.write_text(json.dumps(self._memories, ensure_ascii=False))

    def _load(self):
        if self.store_path.exists():
            self._memories = json.loads(self.store_path.read_text())
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "LongTermMemory 待 C 同学第 3 周实现，参见本文件注释"
        )

    def add(self, role: str, content: str) -> None: ...
    def get_messages(self) -> list[dict]: ...
    def clear(self) -> None: ...
