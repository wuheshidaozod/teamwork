"""Agent 主类 —— ReAct 循环的实现。

【负责人】组长 A
【完成时间】第 2 周

本文件提供了 Agent 类的完整骨架。第 1 周的 main_v0.py 验证了
ReAct 范式可行，本类将其拆分为可复用的面向对象设计。

接口约定见 docs/INTERFACES.md §4。
"""

import re
from typing import Iterator

from config import DEFAULT_MODEL, MAX_ITERATIONS, TEMPERATURE, DEBUG

_THOUGHT_RE = re.compile(
    r"Thought\s*:\s*(.+?)(?:\n(?:Action|Final Answer)|$)", re.DOTALL
)
from agent.parser import parse_action
from tools.registry import ToolRegistry
from memory.base import Memory


class Agent:
    """ReAct 智能体。

    使用示例：
        from agent import Agent
        from agent.prompt import build_system_prompt
        from tools.registry import ToolRegistry
        from memory.short_term import ShortTermMemory
        from config import get_llm_client

        tools = ToolRegistry()
        tools.register(CalculatorTool())
        # ...

        agent = Agent(
            llm_client=get_llm_client(),
            tools=tools,
            memory=ShortTermMemory(),
            system_prompt=build_system_prompt(tools),
        )
        answer = agent.run("爱因斯坦活了多少岁？")
    """

    def __init__(self,
                 llm_client,
                 tools: ToolRegistry,
                 memory: Memory,
                 system_prompt: str,
                 model: str = DEFAULT_MODEL,
                 max_iterations: int = MAX_ITERATIONS,
                 debug: bool = None):
        self.llm = llm_client
        self.tools = tools
        self.memory = memory
        self.system_prompt = system_prompt
        self.model = model
        self.max_iterations = max_iterations
        self.debug = DEBUG if debug is None else debug

        # 评测用：每次 run() 后由 D 的脚本读取
        self.last_iteration_count: int = 0
        self.last_token_count: int = 0
        self.last_trace: list[dict] = []

    # ================================================================
    # 同步版本：跑完整个循环返回最终答案
    # ================================================================
    def run(self, user_input: str) -> str:
        """同步运行 ReAct 循环。

        Args:
            user_input: 用户问题

        Returns:
            最终答案字符串。失败返回 '(未能给出答案)'
        """
        # 收集所有 stream 步骤并拼装答案
        final_answer = "(未能给出答案)"
        for step in self.run_stream(user_input):
            if step["type"] == "final":
                final_answer = step["content"]
        return final_answer

    # ================================================================
    # 流式版本：逐步 yield，供 UI 和评测用
    # ================================================================
    def run_stream(self, user_input: str) -> Iterator[dict]:
        """流式运行，逐步 yield 字典。

        yield 的字典格式：
            {"type": "thought" | "action" | "observation" | "final" | "error",
             "content": str}
        """
        # 初始化本次运行的状态
        self.last_iteration_count = 0
        self.last_token_count = 0
        self.last_trace = []

        # 准备 messages
        self.memory.clear()
        self.memory.add("system", self.system_prompt)
        self.memory.add("user", user_input)

        for step in range(1, self.max_iterations + 1):
            self.last_iteration_count = step

            # ---- 调 LLM ----
            try:
                output = self._call_llm()
            except Exception as e:
                error_msg = f"LLM 调用失败: {e}"
                yield {"type": "error", "content": error_msg}
                return

            if self.debug:
                print(f"\n--- 第 {step} 轮 · LLM 输出 ---\n{output}\n")

            self.last_trace.append({"step": step, "raw_output": output})

            # ---- 检查 Final Answer ----
            if "Final Answer:" in output:
                # 顺便把 Thought 输出
                thought = self._extract_thought(output)
                if thought:
                    yield {"type": "thought", "content": thought}
                answer = output.split("Final Answer:")[-1].strip()
                yield {"type": "final", "content": answer}
                return

            # ---- 解析 Action ----
            action = parse_action(output)
            thought = self._extract_thought(output)
            if thought:
                yield {"type": "thought", "content": thought}

            if action is None:
                # 解析失败，反馈给 LLM 让它重试
                error_obs = ("Error: 你的输出不是合法的 Action JSON。"
                             "请严格按 {\"tool\": \"...\", \"args\": {...}} 格式。")
                self.memory.add("assistant", output)
                self.memory.add("user", f"Observation: {error_obs}")
                yield {"type": "observation", "content": error_obs}
                continue

            # ---- 执行工具 ----
            tool_name = action.get("tool", "")
            tool_args = action.get("args", {}) or {}
            yield {"type": "action",
                   "content": f"{tool_name}({tool_args})"}

            observation = self.tools.call(tool_name, tool_args)
            yield {"type": "observation", "content": observation}

            # ---- 写入历史 ----
            self.memory.add("assistant", output)
            self.memory.add("user", f"Observation: {observation}")

        # 达到最大轮数
        yield {"type": "error",
               "content": f"达到最大迭代次数 {self.max_iterations}"}

    # ================================================================
    # 内部方法
    # ================================================================
    def _call_llm(self) -> str:
        """调用 LLM，返回输出文本。"""
        response = self.llm.chat.completions.create(
            model=self.model,
            messages=self.memory.get_messages(),
            temperature=TEMPERATURE,
            # 关键技巧：让 LLM 输出到 Observation 就停下，
            # 否则它会自己脑补 Observation，整个循环就废了
            stop=["Observation:", "\nObservation"],
        )
        # 统计 token
        if hasattr(response, "usage") and response.usage:
            self.last_token_count += response.usage.total_tokens
        return response.choices[0].message.content

    @staticmethod
    def _extract_thought(output: str) -> str:
        m = _THOUGHT_RE.search(output)
        return m.group(1).strip() if m else ""
