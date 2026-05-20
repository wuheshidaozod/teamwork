"""Tool 基类。

【负责人】B
【接口约定】见 docs/INTERFACES.md §1
"""

from abc import ABC, abstractmethod


class Tool(ABC):
    """所有工具的基类。

    子类必须设置 name / description / parameters 三个类属性，
    并实现 run() 方法。

    示例：
        class CalculatorTool(Tool):
            name = "calculator"
            description = "数学计算器。"
            parameters = {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }

            def run(self, expression: str) -> str:
                ...
    """

    name: str = ""
    description: str = ""
    parameters: dict = {}

    @abstractmethod
    def run(self, **kwargs) -> str:
        """执行工具。

        【重要】出错时返回 "Error: xxx" 字符串，禁止抛异常。
        因为我们希望让 LLM 看到错误信息后能自我调整。
        """
        ...

    def describe(self) -> str:
        """给 System Prompt 用的简短描述。"""
        params_brief = ", ".join(
            f"{k}: {v.get('type', '?')}"
            for k, v in self.parameters.get("properties", {}).items()
        )
        return f"- {self.name}({params_brief})\n    功能: {self.description}"
