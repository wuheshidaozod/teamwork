# 接口约定 INTERFACES.md

> **本文档是全组的"合同"。任何接口修改必须先在群里讨论，得到受影响成员同意后再改。**

## 1. Tool 基类（B 实现，A/D 调用）

```python
# tools/base.py
from abc import ABC, abstractmethod

class Tool(ABC):
    name: str           # 工具唯一标识，给 LLM 使用，如 "calculator"
    description: str    # 给 LLM 看的功能说明
    parameters: dict    # JSON Schema 格式的参数描述

    @abstractmethod
    def run(self, **kwargs) -> str:
        """执行工具。出错时返回 'Error: xxx'，禁止抛异常。"""
        ...
```

## 2. ToolRegistry（B 实现）

```python
# tools/registry.py
class ToolRegistry:
    def register(self, tool: Tool) -> None: ...
    def get(self, name: str) -> Tool | None: ...
    def list_names(self) -> list[str]: ...
    def format_for_prompt(self) -> str:
        """格式化所有工具为 System Prompt 中的描述段"""
    def call(self, name: str, args: dict) -> str:
        """统一调用入口。工具不存在返回 'Error: ...'"""
```

## 3. Memory 基类（C 实现，A 调用）

```python
# memory/base.py
class Memory(ABC):
    @abstractmethod
    def add(self, role: str, content: str) -> None: ...
    @abstractmethod
    def get_messages(self) -> list[dict]:
        """返回 OpenAI 格式的 messages 列表"""
    @abstractmethod
    def clear(self) -> None: ...
```

## 4. Agent 主类（A 实现）

```python
# agent/core.py
class Agent:
    def __init__(self,
                 llm_client,                 # OpenAI 客户端
                 tools: ToolRegistry,
                 memory: Memory,
                 system_prompt: str,
                 model: str = "deepseek-chat",
                 max_iterations: int = 10):
        ...

    def run(self, user_input: str) -> str:
        """同步版本，跑完整个 ReAct 循环返回最终答案"""

    def run_stream(self, user_input: str):
        """流式版本，逐步 yield 字典：
            {"type": "thought" | "action" | "observation" | "final", "content": str}
        给 D 的评测脚本和 C 的 Gradio UI 用。
        """

    # 评测用属性（D 要求 A 暴露这些）
    last_iteration_count: int    # 上一次 run() 用了几轮
    last_token_count: int        # 上一次 run() 总 token 消耗
    last_trace: list[dict]       # 上一次 run() 的完整轨迹
```

## 5. JSON 解析器（B 实现）

```python
# agent/parser.py
def parse_action(llm_output: str) -> dict | None:
    """
    必须能处理以下 5 种情况，返回 {"tool": str, "args": dict} 或 None：

    1. 标准 JSON
    2. 包裹在 ```json ... ``` 中
    3. 包裹在 ``` ... ``` 中
    4. 中文标点（：，"")
    5. Action 关键字前后多余空白

    单元测试见 tests/test_parser.py，B 必须保证 ≥ 95% 通过率。
    """
```

## 6. 数据流与依赖关系

```
              ┌──────────────┐
       user → │    Agent (A) │
              │              │
       ┌──────┤  llm_client  │←── DeepSeek API
       │      │              │
       │      │  ┌────────┐  │     ┌──────────────────┐
       │      ├──┤ parser ├──┼──→  │ ToolRegistry (B) │
       │      │  └────────┘  │     └────────┬─────────┘
       │      │              │              │
       │      │  ┌────────┐  │              ↓
       │      └──┤ Memory ├──┼──→  ┌──────────────┐
       │         └────────┘  │     │  Tools (B)   │
       │           (C)       │     │  - calc      │
       │                     │     │  - wiki      │
       ↓                     │     │  - file_io   │
   final answer              │     └──────────────┘
                             │
              ┌──────────────┘
              ↓
     ┌────────────────┐    ┌──────────────────┐
     │  Gradio UI (C) │    │  Eval Script (D) │
     └────────────────┘    └──────────────────┘
```

## 7. 修改流程

1. 想改任何接口签名前，先在群里 @ 所有受影响的人
2. 取得同意后，**先改本文档，再改代码**
3. 改完在群里发"已更新 INTERFACES.md"
4. 提交 commit 时在 message 里写 `[breaking] 改了 xxx 接口`

## 8. 当前版本

- v0.1（第 1 周末）：初始版本，主要确定基类签名
- v0.2（待第 2 周末更新）
