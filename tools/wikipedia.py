"""维基百科查询工具。

【负责人】B
【完成时间】第 2 周

【依赖】pip install wikipedia-api

【实现要点】
1. 中文优先（lang='zh'），失败时回退到英文
2. 返回前 500 字摘要
3. 词条不存在时返回 "Error: 未找到..."
4. 网络超时时返回 "Error: 网络超时"
"""

from tools.base import Tool
from config import WIKIPEDIA_LANG, WIKIPEDIA_TIMEOUT


class WikipediaTool(Tool):
    name = "wikipedia"
    description = "查询维基百科。输入一个查询词，返回该词条的摘要。"
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "查询词，如 '爱因斯坦' 或 'quantum mechanics'"
            }
        },
        "required": ["query"],
    }

    def __init__(self):
        # TODO(B): 初始化 wikipedia-api 客户端
        # import wikipediaapi
        # self.wiki_zh = wikipediaapi.Wikipedia(
        #     user_agent="mini-agent/0.1 (course project)",
        #     language="zh",
        # )
        # self.wiki_en = wikipediaapi.Wikipedia(
        #     user_agent="mini-agent/0.1 (course project)",
        #     language="en",
        # )
        pass

    def run(self, query: str) -> str:
        """
        TODO(B): 实现维基百科查询

        参考实现：

        try:
            # 中文优先
            page = self.wiki_zh.page(query)
            if not page.exists():
                # 回退英文
                page = self.wiki_en.page(query)
            if not page.exists():
                return f"Error: 未找到「{query}」相关词条"

            summary = page.summary[:500]
            return summary if summary else "Error: 词条存在但摘要为空"
        except Exception as e:
            return f"Error: 维基查询失败 - {e}"
        """
        return f"[TODO B] 待实现：查询 {query}"
