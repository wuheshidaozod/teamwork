"""工具注册表。

【负责人】B
【接口约定】见 docs/INTERFACES.md §2
"""

from tools.base import Tool


class ToolRegistry:
    """工具注册中心。负责注册、查找、统一调用。"""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """注册一个工具。重名时覆盖并打印警告。"""
        if not tool.name:
            raise ValueError("工具必须设置 name 属性")
        if tool.name in self._tools:
            print(f"⚠️ 工具 {tool.name} 被重复注册，已覆盖")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_names(self) -> list[str]:
        return list(self._tools.keys())

    def format_for_prompt(self) -> str:
        """格式化为 System Prompt 中的工具列表段落。"""
        return "\n".join(t.describe() for t in self._tools.values())

    def call(self, name: str, args: dict) -> str:
        """统一调用入口。工具不存在 / 参数错 / 执行异常 都返回 Error 字符串。"""
        tool = self.get(name)
        if tool is None:
            return (f"Error: 工具 '{name}' 不存在。"
                    f"可用工具: {self.list_names()}")
        try:
            return tool.run(**args)
        except TypeError as e:
            return f"Error: 参数不匹配 - {e}"
        except Exception as e:
            return f"Error: 工具执行异常 - {e}"
